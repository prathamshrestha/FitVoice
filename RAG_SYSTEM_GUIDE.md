# 🏋️ FitVoice RAG System Guide

## Overview

This guide explains how to use the **Retrieval-Augmented Generation (RAG)** system that powers FitVoice with detailed, accurate fitness knowledge.

---

## What is RAG (Retrieval-Augmented Generation)?

RAG enhances LLM responses by:
1. **Retrieving** relevant knowledge from a vector database
2. **Injecting** that knowledge into the LLM prompt
3. **Generating** responses informed by factual, verified data

**Without RAG:** LLM generates based on training knowledge alone → Generic responses
**With RAG:** LLM retrieves specific fitness facts → Accurate, detailed responses

---

## Architecture

### Knowledge Sources

The system has **3 layers of knowledge**:

```
┌─────────────────────────────────────┐
│  Comprehensive Fitness Knowledge    │
│  (160+ detailed documents)          │
├─────────────────────────────────────┤
│ Nutrition  │ Workouts  │ Health     │
│ Recovery   │ Programs  │ Injury Prev│
└────────────────────────────────────┬┘
                  ↓
        ┌─────────────────────┐
        │ Vector Database     │
        │ (Chroma + Embeddings)
        └────────────┬────────┘
                  ↓
        ┌─────────────────────┐
        │   Semantic Search   │
        │  (Find relevant KB) │
        └────────────┬────────┘
                  ↓
        ┌─────────────────────┐
        │  TinyLlama LLM      │
        │  (Generate response)│
        └─────────────────────┘
```

### Components

| Component | Purpose | Technology |
|-----------|---------|-----------|
| **Knowledge Base** | Comprehensive fitness facts | 160+ JSONL documents |
| **Embeddings** | Convert text to vectors | Sentence-Transformers (all-MiniLM-L6-v2) |
| **Vector DB** | Fast semantic search | Chroma (DuckDB-backed) |
| **Hybrid Retrieval** | Dual knowledge sources | KB + Q&A examples |
| **Integration** | Inject context into LLM | Prompt engineering |

---

## Setup

### Step 1: Install Dependencies

```bash
cd be
pip install chromadb sentence-transformers
```

### Step 2: Generate Knowledge Base

```bash
python setup_rag.py
```

This script:
✅ Generates 160+ fitness knowledge documents
✅ Checks dependencies
✅ Initializes Chroma vector database
✅ Tests RAG system
✅ Tests LLM integration

**What gets created:**
- `fitness_knowledge_base.jsonl` - 160+ fact documents
- `chroma_db/` - Vector database directory

### Step 3: Verify Setup

```bash
# Test RAG system directly
python fitness_rag_system.py

# Test full integration
python setup_rag.py
```

---

## Knowledge Base Content

### Nutrition (40+ documents)
- ✅ Macronutrient guidelines (protein, carbs, fats)
- ✅ Micronutrient facts (iron, calcium, electrolytes)
- ✅ Meal planning and timing
- ✅ Goal-specific diets (weight loss, muscle building)

### Workouts (35+ documents)
- ✅ Exercise types (strength, cardio, flexibility)
- ✅ Proper form techniques (squat, deadlift, bench press)
- ✅ Goal-specific programs
- ✅ Programming principles (periodization, rest days)

### Health & Wellness (35+ documents)
- ✅ Sleep optimization
- ✅ Injury prevention and recovery
- ✅ Stress management
- ✅ Special populations (older adults, pregnancy, menopause)
- ✅ Medical conditions (diabetes, hypertension, back pain)

### Recovery & Performance (15+ documents)
- ✅ Active recovery methods
- ✅ Supplementation strategies
- ✅ Performance monitoring
- ✅ Sleep protocols

---

## How RAG Works in FitVoice

### Request Flow

```
User Voice Input
       ↓
   Transcription
       ↓
   User Query ("How much protein do I need?")
       ↓
   ┌─────────────────────────────────────┐
   │ RAG RETRIEVAL PHASE                 │
   │ 1. Generate query embedding         │
   │ 2. Search vector database (top-3)   │
   │ 3. Retrieve similar Q&A examples    │
   │ 4. Format knowledge context         │
   └──────────────┬──────────────────────┘
                  ↓
   ┌─────────────────────────────────────┐
   │ LLM GENERATION PHASE                │
   │ 1. Get user fitness profile         │
   │ 2. Add retrieved knowledge          │
   │ 3. Create enhanced system prompt    │
   │ 4. Generate response with LLM       │
   └──────────────┬──────────────────────┘
                  ↓
         Generated Response
       ("Based on your fitness level...")
              ↓
        Emotion Detection
              ↓
        Text-to-Speech
              ↓
        Audio Response
```

### Example

**User Query:** "I'm 30, want to lose weight, how should I eat?"

**RAG Retrieval:**
```
Retrieved Document 1 (95% relevant):
- Title: "Weight Loss Nutrition"
- Content: "Caloric deficit of 300-500 calories/day (0.5-1kg loss/week). 
            High protein (1.6-2.2g/kg) preserves muscle..."

Retrieved Document 2 (88% relevant):
- Title: "Protein Requirements"  
- Content: "Daily protein intake: 0.8g per kg body weight (sedentary), 
            1.2-2.0g per kg (active)..."

Retrieved Example (82% relevant Q&A):
- Q: "I want to lose fat but keep my muscle, what should I eat?"
- A: "Focus on protein intake at 1.8-2.2g per kg and maintain a moderate caloric deficit..."
```

**LLM Prompt with Context:**
```
<|system|>
You are a fitness coach. The user is 30 years old with a fitness goal of weight loss.
[... retrieved fitness knowledge ...]
</|system|>

<|user|>
I'm 30, want to lose weight, how should I eat?
</|user|>

<|assistant|>
[LLM generates response using both user profile and retrieved knowledge]
```

---

## Usage in Code

### Using RAG in Fitness LLM

```python
from app.fitness_llm_inference import FitnessLLMInference

# Initialize with RAG (default)
llm = FitnessLLMInference(use_rag=True)

# Generate response with RAG
response = llm.generate_fitness_advice(
    query="How do I build muscle?",
    user_profile=user_profile,
    use_rag=True  # Enable RAG retrieval
)
```

### Direct RAG Usage

```python
from fitness_rag_system import HybridFitnessRAG

# Initialize RAG
rag = HybridFitnessRAG()
rag.load_knowledge_base()

# Retrieve knowledge
retrieved_docs, context = rag.retrieve_hybrid(
    query="Best exercises for runners",
    kb_top_k=3,        # Top 3 knowledge base documents
    qa_top_k=2         # Top 2 Q&A examples
)

# Use context in your own prompt
print(context)
```

### Server Integration

RAG is **automatically enabled** in the FastAPI server:

```python
# In server.py
fitness_llm = FitnessLLMInference(
    lora_weights_path="fitness_llm_model",
    use_rag=True  # Default: True
)

# When generating responses
response = fitness_llm.generate_fitness_advice(
    query=transcribed_text,
    user_profile=user_profile,
    use_rag=True  # Uses RAG automatically
)
```

---

## Configuration

### Retrieval Parameters

Edit these in `fitness_rag_system.py` or at runtime:

```python
# In retrieve_hybrid()
kb_top_k = 3        # Knowledge base results (increase for more context)
qa_top_k = 2        # Q&A example results
min_distance = 0.3  # Relevance threshold (0-1, higher = stricter)
```

### LLM Generation Parameters

Control response quality in server.py:

```python
# Adjust in process_utterance()
max_new_tokens=75        # Response length (50-150 typical)
temperature=0.7          # Creativity (0.1=precise, 1.0=creative)
top_p=0.9               # Sampling focus
```

---

## Monitoring RAG Performance

### Check Retrieval Quality

```bash
# Running setup_rag.py shows retrieval examples
python setup_rag.py
```

Look for:
- ✅ Retrieved documents with >0.8 relevance
- ✅ Diverse knowledge sources (KB + Q&A)
- ✅ Relevant titles and content

### Enable Logging

In `server.py` terminal output:
```
📚 Fitness Knowledge Base (retrieval logs will show):
  Title: "Weight Loss Nutrition"
  Relevance: 0.94
  Category: goals
```

### Performance Metrics

```python
# Get RAG statistics
stats = rag.get_full_stats()
print(f"Total KB docs: {stats['total_documents']}")
print(f"Total Q&A: {stats['qa_examples']}")
```

---

## Enhancement: Add Custom Knowledge

### Add More Fitness Facts

Edit `fitness_knowledge_base.py` → Add to relevant `_*_knowledge()` method:

```python
def _nutrition_knowledge(self):
    return [
        # ... existing facts ...
        {
            "category": "macronutrients",
            "title": "Your New Fact",
            "content": "Detailed explanation and guidelines..."
        }
    ]
```

Regenerate:
```bash
python fitness_knowledge_base.py
python setup_rag.py  # Reload into vector DB
```

### Add Real Fitness Q&A

If you have your own fitness Q&A dataset:

```python
# Prepare in JSONL format
with open("custom_qa.jsonl", "w") as f:
    for qa in your_data:
        json.dump({
            "question": qa["question"],
            "answer": qa["answer"]
        }, f)
        f.write("\n")

# Use in hybrid RAG
rag = HybridFitnessRAG(qa_pairs_path="custom_qa.jsonl")
```

---

## Troubleshooting

### Issue: "No documents retrieved"

**Solution:** Check knowledge base loaded
```bash
# Verify file exists
ls fitness_knowledge_base.jsonl

# Regenerate if needed
python fitness_knowledge_base.py
```

### Issue: "RAG not available"

**Solution:** Install dependencies
```bash
pip install chromadb sentence-transformers
```

### Issue: "Slow first query"

**Normal!** First query includes:
- Model loading (~2-3 sec)
- Embedding generation (~1 sec)
- LLM generation (~3-5 sec)

Subsequent queries are faster (only LLM + embedding).

### Issue: "Irrelevant retrieved documents"

**Solution:** Try different threshold
```python
# Lower threshold = more results but less relevant
retrieved = rag.retrieve(query, min_distance=0.2)

# Higher threshold = fewer but more relevant  
retrieved = rag.retrieve(query, min_distance=0.5)
```

---

## Performance Optimization

### Reduce Latency

1. **Use fewer retrieval results** (default is good)
   ```python
   rag.retrieve(query, top_k=3)  # Instead of 5
   ```

2. **Use lower embedding model** (already using lightweight model)
   ```python
   # all-MiniLM-L6-v2 = 384-dim, ~22MB (optimal for speed)
   ```

3. **Cache embeddings** (implemented in Chroma)
   ```python
   # Chroma caches all embeddings automatically
   ```

### Improve Quality

1. **More retrieval results** for comprehensive answers
   ```python
   rag.retrieve(query, top_k=5)
   ```

2. **Higher relevance threshold** for accuracy
   ```python
   rag.retrieve(query, min_distance=0.5)
   ```

3. **Add custom domain knowledge**
   ```python
   # Add sport-specific facts to knowledge base
   ```

---

## Future Enhancements

### Potential Improvements

- [ ] Support for external fitness APIs (nutrition databases)
- [ ] Fine-tuning embeddings on fitness domain
- [ ] Multi-language support
- [ ] User-specific knowledge personalization
- [ ] Real-time knowledge updates
- [ ] A/B testing retrieval strategies
- [ ] Feedback loop to rank helpful responses

---

## Conclusion

RAG transforms FitVoice from a generic chatbot into a **knowledgeable fitness coach** by:
- ✅ Grounding responses in verified fitness facts
- ✅ Maintaining accuracy and safety
- ✅ Providing personalized advice
- ✅ Adapting to user fitness goals

The system seamlessly integrates RAG into the voice pipeline, making expert fitness guidance available through natural conversation.

---

## Quick Links

- 📚 **Knowledge Base Generator:** `fitness_knowledge_base.py`
- 🔍 **RAG System:** `fitness_rag_system.py`
- 🤖 **LLM Integration:** `app/fitness_llm_inference.py`
- ⚙️ **Setup Script:** `setup_rag.py`
- 🚀 **Server:** `app/server.py`
