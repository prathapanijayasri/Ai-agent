import os
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
                logger.error(f"Gemini API call failed: {e}")
                # Fallback to offline extractor
                offline_res = self._offline_rag_synthesizer(question, context, reliable, sources)
                offline_res["error"] = f"Gemini API unavailable ({str(e)}). Fallen back to local RAG."
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
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.config.GEMINI_MODEL}:generateContent?key={self.config.GEMINI_API_KEY}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": SYSTEM_HEALTHCARE_PROMPT + "\n\n" + prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 800
            }
        }
        res = requests.post(url, json=payload, timeout=20)
        res.raise_for_status()
        data = res.json()
        candidates = data.get("candidates", [])
        if candidates and "content" in candidates[0]:
            parts = candidates[0]["content"].get("parts", [])
            if parts:
                return parts[0].get("text", "").strip()
        raise ValueError("Empty or invalid response from Gemini API.")

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
        A rule-bound, extractive RAG synthesizer.
        Extracts verified knowledge directly from the retrieved passages without hallucination,
        honestly admitting when reliable context is not found.
        """
        if not reliable or not context.strip():
            msg = (
                f"I do not have verified medical documentation on **\"{question}\"** in my current local knowledge base.\n\n"
                "To ensure your safety and avoid inaccurate or fabricated information:\n"
                "- Please consult a licensed physician, pharmacist, or healthcare provider for clinical evaluation.\n"
                "- You may also refer to authoritative healthcare portals such as the **World Health Organization (WHO)**, "
                "the **NHS**, or **MedlinePlus**.\n\n"
                f"*{STANDARD_DISCLAIMER}*"
            )
            return {
                "text": msg,
                "provider": "Extractive RAG (Offline Mode)",
                "error": None
            }

        # Present the extracted verified findings clearly
        sections = []
        sections.append(f"### Healthcare Educational Summary\nBased on verified material in the knowledge base:\n")

        for idx, src in enumerate(sources, 1):
            source_file = src.get("source", "Document")
            page_num = src.get("page", 1)
            snippet = src.get("snippet", "").strip()
            sections.append(f"**Key Point {idx}** *(from {source_file}, Page {page_num})*:\n{snippet}\n")

        sections.append(
            "\n**Important Precautions:**\n"
            "- Never start, stop, or change prescribed medications without consulting your doctor or pharmacist.\n"
            "- If your symptoms worsen, persist, or cause severe distress, please seek an in-person medical evaluation.\n"
        )
        sections.append(f"\n*{STANDARD_DISCLAIMER}*")

        return {
            "text": "\n".join(sections),
            "provider": "Extractive RAG (Offline Mode)",
            "error": None
        }
