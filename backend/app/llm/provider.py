import os
import re
import time
import json
import logging
import requests
from typing import Dict, Any, List

from backend.app.config import Config
from backend.app.llm.prompts import SYSTEM_HEALTHCARE_PROMPT, build_rag_prompt
from backend.app.safety import STANDARD_DISCLAIMER

logger = logging.getLogger(__name__)

class LLMProvider:
    def __init__(self, config: Config):
        self.config = config
        self.provider = config.LLM_PROVIDER

        # Auto-detect provider based on keys if set to 'auto'
        if self.provider == "auto":
            if config.GEMINI_API_KEY:
                self.provider = "gemini"
            elif config.OPENAI_API_KEY:
                self.provider = "openai"
            elif config.HUGGINGFACE_API_KEY:
                self.provider = "huggingface"
            else:
                self.provider = "offline"

    def get_provider_name(self) -> str:
        names = {
            "gemini": f"Google Gemini ({self.config.GEMINI_MODEL})",
            "openai": f"OpenAI ({self.config.OPENAI_MODEL})",
            "huggingface": f"Hugging Face ({self.config.HUGGINGFACE_MODEL})",
            "offline": "Local RAG Synthesizer (Extractive / Offline Mode)"
        }
        return names.get(self.provider, self.provider)

    def generate_response(self, question: str, context: str, reliable: bool, sources: List[Dict]) -> Dict[str, Any]:
        """
        Generates response using selected provider with fallback to offline extractive synthesizer.
        Returns:
            {
                "text": str,
                "provider": str,
                "error": Optional[str]
            }
        """
        prompt = build_rag_prompt(question, context, reliable)

        if self.provider == "gemini" and self.config.GEMINI_API_KEY:
            try:
                response_text = self._call_gemini(prompt)
                return {
                    "text": response_text,
                    "provider": self.get_provider_name(),
                    "error": None
                }
            except Exception as e:
                err_msg = str(e)
                if self.config.GEMINI_API_KEY in err_msg:
                    err_msg = err_msg.replace(self.config.GEMINI_API_KEY, "[REDACTED_API_KEY]")
                logger.error(f"Gemini API call failed: {err_msg}")
                # Fallback to offline extractor
                offline_res = self._offline_rag_synthesizer(question, context, reliable, sources)
                offline_res["error"] = f"Gemini API unavailable ({err_msg}). Fallen back to local RAG."
                return offline_res

        elif self.provider == "openai" and self.config.OPENAI_API_KEY:
            try:
                response_text = self._call_openai(prompt)
                return {
                    "text": response_text,
                    "provider": self.get_provider_name(),
                    "error": None
                }
            except Exception as e:
                logger.error(f"OpenAI API call failed: {e}")
                offline_res = self._offline_rag_synthesizer(question, context, reliable, sources)
                offline_res["error"] = f"OpenAI API unavailable ({str(e)}). Fallen back to local RAG."
                return offline_res

        elif self.provider == "huggingface" and self.config.HUGGINGFACE_API_KEY:
            try:
                response_text = self._call_huggingface(prompt)
                return {
                    "text": response_text,
                    "provider": self.get_provider_name(),
                    "error": None
                }
            except Exception as e:
                logger.error(f"Hugging Face API call failed: {e}")
                offline_res = self._offline_rag_synthesizer(question, context, reliable, sources)
                offline_res["error"] = f"Hugging Face API unavailable ({str(e)}). Fallen back to local RAG."
                return offline_res

        else:
            # Local Extractive RAG Synthesizer
            return self._offline_rag_synthesizer(question, context, reliable, sources)

    def _call_gemini(self, prompt: str) -> str:
        """
        Calls Google Gemini API using the official google-genai SDK.
        Includes graceful retry and fallback for transient demand spikes.
        """
        if not self.config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured or is empty.")

        from google import genai
        from google.genai import types

        client = genai.Client(api_key=self.config.GEMINI_API_KEY)
        last_error = None

        candidate_models = [self.config.GEMINI_MODEL, "gemini-flash-latest", "gemini-3.5-flash"]
        models_to_try = []
        for m in candidate_models:
            if m and m not in models_to_try:
                models_to_try.append(m)

        for model_name in models_to_try:
            for attempt in range(2):
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_HEALTHCARE_PROMPT,
                            temperature=0.2,
                            max_output_tokens=1000
                        )
                    )
                    if response and response.text:
                        return response.text.strip()
                    raise ValueError("Empty or invalid response from Gemini API.")
                except Exception as e:
                    last_error = e
                    err_str = str(e)
                    if attempt == 0 and ("503" in err_str or "UNAVAILABLE" in err_str):
                        time.sleep(1.0)
                        continue
                    break

        err_msg = str(last_error)
        if self.config.GEMINI_API_KEY in err_msg:
            err_msg = err_msg.replace(self.config.GEMINI_API_KEY, "[REDACTED_API_KEY]")
        raise RuntimeError(f"Gemini API Error: {err_msg}") from None




    def _call_openai(self, prompt: str) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.config.OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_HEALTHCARE_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 800
        }
        res = requests.post(url, headers=headers, json=payload, timeout=20)
        res.raise_for_status()
        data = res.json()
        choices = data.get("choices", [])
        if choices and "message" in choices[0]:
            return choices[0]["message"].get("content", "").strip()
        raise ValueError("Empty or invalid response from OpenAI API.")

    def _call_huggingface(self, prompt: str) -> str:
        url = f"https://api-inference.huggingface.co/models/{self.config.HUGGINGFACE_MODEL}"
        headers = {"Authorization": f"Bearer {self.config.HUGGINGFACE_API_KEY}"}
        payload = {
            "inputs": f"{SYSTEM_HEALTHCARE_PROMPT}\n\nUser Question: {prompt}",
            "parameters": {"max_new_tokens": 500, "temperature": 0.3}
        }
        res = requests.post(url, headers=headers, json=payload, timeout=25)
        res.raise_for_status()
        data = res.json()
        if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
            return data[0]["generated_text"].strip()
        raise ValueError("Invalid format from Hugging Face Inference API.")

    def _offline_rag_synthesizer(self, question: str, context: str, reliable: bool, sources: List[Dict]) -> Dict[str, Any]:
        """
        A rule-bound, extractive RAG synthesizer implementing the mandatory 6-part medical response structure.
        1. Brief symptom acknowledgment.
        2. Relevant educational information supported by sources.
        3. 1 or 2 concise follow-up questions.
        4. Warning signs and guidance on when to seek care.
        5. Source citations only when evidence supports the answer.
        6. Short educational disclaimer.
        """
        symptom_name = self._detect_primary_symptom(question)
        follow_ups = self._generate_follow_up_questions(question)

        if not reliable or not context.strip():
            # Honest acknowledgement of lack of verified local knowledge
            parts = [
                f"**Symptom Acknowledgment:** Thank you for consulting MediBot regarding {symptom_name}. I understand you are seeking information about this concern.",
                f"\n**Knowledge Base Notice:** I do not have verified medical documentation on **\"{question}\"** in my current local knowledge base. To prevent inaccurate or fabricated information, I cannot provide clinical guidance for this specific query.",
                "\n**General Guidance:**",
                "- Monitor your symptoms closely, rest the affected area if physical discomfort is present, and avoid activities that aggravate the issue.",
                "- Consult a licensed physician, pharmacist, or healthcare provider for an in-person clinical assessment.",
                "- Authoritative references include the **World Health Organization (WHO)**, **NHS UK**, and **MedlinePlus**.",
                "\n**Follow-Up Questions to Consider:**"
            ]
            for q_item in follow_ups[:2]:
                parts.append(f"- {q_item}")

            parts.append(
                "\n**When to Seek Immediate Care:**\n"
                "- If you experience severe, worsening, or sudden symptoms, fever with stiff neck, breathing difficulties, or acute trauma, seek immediate medical attention or call emergency services (112 in India, 911 in US/Canada)."
            )
            parts.append(f"\n*{STANDARD_DISCLAIMER}*")

            return {
                "text": "\n".join(parts),
                "provider": "Extractive RAG (Offline Mode)",
                "error": None
            }

        # 6-Part Structured Response with Verified Context
        parts = []

        # 1. Symptom Acknowledgment
        parts.append(f"**Symptom Acknowledgment:** Thank you for reaching out regarding {symptom_name}. Here is educational information based on verified healthcare guidelines.")

        # 2. Healthcare Educational Summary (Clean synthesis from verified passages)
        parts.append("\n### Healthcare Educational Summary")
        
        # Cleanly synthesize bullet points from context/sources without broken fragments
        cleaned_points = self._synthesize_key_points(context, sources)
        for pt in cleaned_points:
            parts.append(f"- {pt}")

        # 3. Follow-Up Questions (1 or 2 at a time)
        parts.append("\n**Clarifying Follow-Up Questions:**")
        for q_item in follow_ups[:2]:
            parts.append(f"- {q_item}")

        # 4. Warning Signs and Guidance on When to Seek Professional Care
        parts.append("\n**When to Seek Professional Medical Care:**")
        warning_signs = self._generate_warning_signs(question)
        for ws in warning_signs:
            parts.append(f"- {ws}")
        parts.append("- *Reminder:* Never start, stop, or adjust prescribed medications without consulting your prescribing physician or pharmacist.")

        # 5. Supporting Citations (only verified sources)
        if sources:
            parts.append("\n**Supporting Citations:**")
            unique_sources = {}
            for src in sources:
                s_name = src.get("source", "Document")
                p_num = src.get("page", 1)
                unique_sources[(s_name, p_num)] = src.get("snippet", "")

            for (s_name, p_num), snip in unique_sources.items():
                parts.append(f"- Verified from **{s_name}** (Page {p_num})")

        # 6. Educational Disclaimer
        parts.append(f"\n*{STANDARD_DISCLAIMER}*")

        return {
            "text": "\n".join(parts),
            "provider": "Extractive RAG (Offline Mode)",
            "error": None
        }

    def _detect_primary_symptom(self, question: str) -> str:
        q = question.lower()
        if re.search(r"\b(left\s+)?(hand|wrist|finger|palm|thumb)\b", q):
            return "hand or wrist discomfort"
        if re.search(r"\b(left\s+)?arm\b", q):
            return "arm discomfort"
        if re.search(r"\bheadache|migraine\b", q):
            return "headache symptoms"
        if re.search(r"\bburn|scald\b", q):
            return "burn first aid and wound care"
        if re.search(r"\bwater|hydration|dehydrat\b", q):
            return "daily hydration and fluid balance"
        if re.search(r"\bdiabetes|blood\s+sugar|glucose\b", q):
            return "Type 2 Diabetes awareness"
        if re.search(r"\bhypertension|blood\s+pressure\b", q):
            return "blood pressure management"
        if re.search(r"\bantibiotic\b", q):
            return "antibiotic precautions and stewardship"
        if re.search(r"\bsprain|strain|r\.?i\.?c\.?e\b", q):
            return "sprains, strains, and joint care"
        if re.search(r"\bfever|temperature\b", q):
            return "fever evaluation"
        if re.search(r"\bcough\b", q):
            return "cough symptoms"
        if re.search(r"\bsleep|insomnia\b", q):
            return "sleep hygiene"
        if re.search(r"\bexercise|fitness\b", q):
            return "physical activity guidelines"
        return "your reported health query"

    def _generate_follow_up_questions(self, question: str) -> List[str]:
        q = question.lower()
        if re.search(r"\b(hand|wrist|finger|arm|pain|ache|stiff|sprain|strain)\b", q):
            return [
                "Where exactly is the pain located (e.g., wrist, fingers, palm, or forearm), and did it start suddenly or develop gradually?",
                "Was there a recent injury, heavy strain, or repetitive activity involved (such as prolonged typing or repetitive gripping)?"
            ]
        if re.search(r"\bheadache|migraine\b", q):
            return [
                "When did this headache begin, and is it a constant dull pressure band or a throbbing pain on one side?",
                "Are you experiencing any other symptoms, such as light sensitivity, nausea, or neck stiffness?"
            ]
        if re.search(r"\bburn|scald\b", q):
            return [
                "How recently did the burn occur, and is the skin surface red, blistered, or charred/white?",
                "Have you already cooled the affected area under cool running water for at least 10 to 20 minutes?"
            ]
        if re.search(r"\bfever\b", q):
            return [
                "What is your current temperature reading, and how many consecutive days has the fever lasted?",
                "Are there accompanying warning signs such as a stiff neck, persistent vomiting, or difficulty breathing?"
            ]
        if re.search(r"\bcough\b", q):
            return [
                "How long have you had this cough (less than 3 weeks or 8 weeks or longer)?",
                "Is the cough dry or productive, and have you noticed any wheezing, chest tightness, or blood?"
            ]
        return [
            "When did this symptom first start, and has it been getting better, worse, or staying the same?",
            "Are there any other symptoms or relevant medical conditions you are currently managing?"
        ]

    def _generate_warning_signs(self, question: str) -> List[str]:
        q = question.lower()
        if re.search(r"\b(hand|wrist|arm|finger)\b", q):
            return [
                "Pain that persists for more than a few days, worsens despite rest, or significantly limits daily function.",
                "Noticeable swelling, warmth, joint redness, inability to move fingers, or progressive numbness.",
                "Red Flag: Any left arm or hand pain accompanied by chest pressure, shortness of breath, nausea, sweating, or faintness requires immediate emergency evaluation (call 112 / 911)."
            ]
        if re.search(r"\bheadache|migraine\b", q):
            return [
                "Sudden excruciating headache reaching maximum intensity within seconds or minutes ('thunderclap' headache).",
                "Headache accompanied by fever with stiff neck, confusion, facial drooping, arm weakness, or speech difficulty (call 112 / 911 immediately).",
                "Headache developing shortly after head trauma or a fall."
            ]
        if re.search(r"\bburn|scald\b", q):
            return [
                "Burn is larger than the palm of the casualty's hand, or involves the face, hands, feet, groin, or major joints.",
                "Chemical, electrical, or third-degree burns (white, blackened, or charred skin).",
                "Signs of wound infection such as increasing pain, spreading redness, pus, or fever."
            ]
        if re.search(r"\bfever\b", q):
            return [
                "A fever exceeding 39.4°C (103°F) in adults, or lasting more than 3 consecutive days.",
                "Fever accompanied by stiff neck, confusion, unexplained rash, or severe difficulty breathing."
            ]
        return [
            "Symptoms that are severe, rapidly worsening, or do not improve with conservative self-care.",
            "Any severe difficulty breathing, acute chest tightness, or sudden neurological deficits (slurred speech, facial drooping, one-sided weakness)."
        ]

    def _synthesize_key_points(self, context: str, sources: List[Dict]) -> List[str]:
        """Extracts and formats clean, coherent medical bullet points without fragment artifacts."""
        points = []
        raw_lines = [line.strip() for line in context.split("\n") if line.strip()]

        for line in raw_lines:
            # Skip headers and source tags
            if line.startswith("#") or line.startswith("[Source:") or line.startswith("---") or line.startswith("Topic:"):
                continue
            # Keep meaningful bullet points or informational sentences
            if line.startswith("-") or line.startswith("*"):
                cleaned = line.lstrip("-* ").strip()
                if len(cleaned) > 25 and not cleaned.startswith("emical"):
                    points.append(cleaned)
            elif len(line) > 40 and not line.endswith(":"):
                # Clean paragraph sentence
                sentences = re.split(r'(?<=[.!?])\s+', line)
                for s in sentences:
                    s_clean = s.strip()
                    if len(s_clean) > 30 and not s_clean.startswith("emical"):
                        points.append(s_clean)

        # Deduplicate while preserving order
        unique_points = []
        for p in points:
            # Avoid partial/truncated fragments
            if not p[0].isupper() and not p.startswith("("):
                continue
            if p not in unique_points:
                unique_points.append(p)

        if unique_points:
            return unique_points[:5]

        # Fallback to snippets from sources
        for src in sources:
            snip = src.get("snippet", "").strip()
            if snip and len(snip) > 20:
                unique_points.append(snip)
        return unique_points[:3] if unique_points else ["Follow evidence-based guidelines and consult a medical professional."]

