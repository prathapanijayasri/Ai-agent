# Model Adaptation: RAG vs. Fine-Tuning in Healthcare AI

In healthcare applications, ensuring factual accuracy, preventing hallucinations, and strictly attributing information to verified medical sources are the highest priorities.

Two primary techniques exist to adapt AI models to domain-specific healthcare knowledge:
1. **Retrieval-Augmented Generation (RAG)** *(Primary method used in MediBot AI)*
2. **Model Fine-Tuning (e.g., Parameter-Efficient Fine-Tuning with LoRA)**

---

## 1. Retrieval-Augmented Generation (RAG)

In RAG, the language model weights remain completely unchanged. When a user asks a question:
1. The question is converted into an embedding using a vector model (e.g., `all-MiniLM-L6-v2`).
2. A vector database (e.g., **ChromaDB**) searches indexed clinical guidelines (e.g., from WHO, NHS, MedlinePlus) for the most semantically relevant text passages.
3. The retrieved passages are passed into the prompt as verified ground-truth context.
4. The model synthesizes an answer strictly from that retrieved context.

### Why RAG is the Preferred Choice for MediBot AI:
- **Zero Hallucination of Citations:** Every piece of advice links back directly to the source document and page number.
- **Instant Knowledge Updates:** When clinical guidelines change, you simply update or re-index the document in ChromaDB—no expensive re-training or downtime needed.
- **Data Access Control:** You can restrict document ingestion or remove outdated medical advice instantly.
- **Low Compute Costs:** Runs smoothly on standard CPU hardware or low-cost containers without requiring expensive GPUs.

---

## 2. Model Fine-Tuning (LoRA / PEFT)

Fine-tuning involves adjusting the neural network parameters (weights) of a pre-trained model by training it on a domain-specific dataset.

### Low-Rank Adaptation (LoRA):
Standard fine-tuning modifies all model parameters, which is computationally prohibitive. **LoRA** freezes the original pre-trained model weights and injects trainable low-rank decomposition matrices into each transformer layer. This dramatically reduces the number of trainable parameters (often by >90%) and memory requirements.

### When to use Fine-Tuning:
- When you want to teach the model a specific clinical tone, communication style, or specialized medical terminology.
- When you want to train an agent to output structured medical records (e.g., HL7, FHIR, or JSON schemas).
- When operating in high-volume, low-latency environments where passing long context documents in every prompt is too slow or costly.

### Limitations of Fine-Tuning for Factual Medical Knowledge:
- **Knowledge Drift & Hallucination:** Fine-tuned models can still confabulate or hallucinate plausible-sounding medical facts without source traceability.
- **Static Knowledge:** Updating facts requires collecting new data and launching another training pipeline.
- **Resource Intensity:** Even parameter-efficient methods require significant memory and compute to train and evaluate safely.

---

## Summary Comparison

| Dimension | Retrieval-Augmented Generation (RAG) | Parameter-Efficient Fine-Tuning (LoRA) |
| :--- | :--- | :--- |
| **Model Weights** | Frozen (Unchanged) | Low-rank adapter weights modified |
| **Knowledge Source** | Dynamic external database (ChromaDB) | Baked into adapter weights |
| **Source Attribution** | Direct document name & page number | Cannot directly cite source text |
| **Updating Information** | Instant (add or re-index documents) | Requires re-training & validation |
| **Hardware Required** | Lightweight CPU or basic container | GPU recommended for practical training |
| **MediBot AI Status** | **Active Production Pipeline** | Optional educational reference script |

---

## Running the LoRA Fine-Tuning Demo
See `finetuning/lora_finetune_example.py` for a lightweight, runnable demonstration using Hugging Face `transformers` and `peft`.
