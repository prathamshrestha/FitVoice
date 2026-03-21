# FitVoice AI Coach - Training & Inference Guide

This guide covers training and deploying the fitness-specific AI models for FitVoice personal fitness and wellness voice coach.

## Overview

FitVoice uses a multi-model architecture:
- **ASR (Whisper)**: Transcribes user speech queries
- **Emotion Classification**: Detects user emotions from audio
- **Fitness LLM (TinyLlama)**: Generates fitness advice tailored to user goals
- **TTS (VITS)**: Converts responses to speech

This guide focuses on fine-tuning the **Fitness LLM** to provide personalized fitness advice.

## Supported Fitness Goals

The system supports 5 primary fitness goals:
1. **weight_loss** - Weight loss and fat reduction
2. **muscle_building** - Muscle gain and strength development
3. **cardiovascular_health** - Heart health and endurance
4. **general_wellness** - Overall health, flexibility, and balance
5. **athletic_performance** - Sports performance and agility

## Quick Start

### 1. Generate Training Data

```bash
cd be
python fitness_dataset_generator.py
```

This creates 250 synthetic training examples (50 per fitness goal) in `training_data/`:
- `fitness_data.jsonl` - Combined dataset
- `fitness_data_<goal>.jsonl` - Goal-specific datasets

### 2. Fine-tune the Fitness LLM

```bash
python fitness_llm_trainer.py
```

Parameters to customize:
- `num_epochs`: Number of training epochs (default: 3)
- `batch_size`: Batch size (default: 4, reduce if GPU memory is limited)
- `learning_rate`: Learning rate (default: 2e-4)
- Model checkpoint saved to `fitness_llm_model/`

**Requirements:**
- GPU recommended (will run on CPU but slower)
- ~4GB GPU memory with batch_size=4
- Uses LoRA for efficient fine-tuning (~200MB disk space)

### 3. Start the FitVoice Server

```bash
python -m uvicorn app.server:app --reload --host 0.0.0.0 --port 8000
```

The server will automatically load:
- Base TinyLlama model
- Fine-tuned LoRA weights (if available at `fitness_llm_model/`)

## API Reference

### User Profile Management

#### Create User Profile
```bash
POST /api/users
{
  "user_id": "user_123",
  "name": "Alice",
  "primary_goal": "weight_loss",
  "age": 28,
  "fitness_level": "intermediate",
  "weight_kg": 75.0,
  "height_cm": 165,
  "medical_conditions": null
}
```

Response:
```json
{
  "success": true,
  "user_id": "user_123",
  "profile": {
    "user_id": "user_123",
    "name": "Alice",
    "primary_goal": "weight_loss",
    "age": 28,
    "fitness_level": "intermediate",
    ...
  }
}
```

#### Get User Profile
```bash
GET /api/users/{user_id}
```

#### Update User Profile
```bash
PUT /api/users/{user_id}
{
  "primary_goal": "muscle_building",
  "weight_kg": 72.0,
  ...
}
```

#### List All Users
```bash
GET /api/users
```

Response:
```json
{
  "count": 5,
  "users": [...]
}
```

#### Delete User
```bash
DELETE /api/users/{user_id}
```

### Fitness Advice

#### Get Personalized Fitness Advice
```bash
POST /api/fitness-advice
{
  "user_id": "user_123",
  "query": "How can I lose weight effectively?"
}
```

Response:
```json
{
  "query": "How can I lose weight effectively?",
  "user_id": "user_123",
  "user_goal": "weight_loss",
  "advice": "For weight loss, focus on creating a calorie deficit through a combination of diet and exercise. Aim for 300-500 calorie deficit daily. Include both cardio (30-45 min, 3-5x/week) and strength training (2-3x/week) to preserve muscle mass."
}
```

### WebSocket Connection

For real-time voice interaction with goal-aware responses:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

// Set user ID for personalized responses
ws.send('user_id:user_123');

// Send audio chunks (Int16 PCM, 16kHz)
ws.send(audioBuffer);

// Receive response
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Transcription:', data.text);
  console.log('Emotion:', data.emotion);
  console.log('Advice:', data.llm_response);
  console.log('Audio:', data.audio); // Base64 encoded
};
```

## System Prompts

The system generates context-aware prompts based on user profiles:

```python
from app.user_profile import get_goal_specific_system_prompt

profile = profile_manager.get_profile("user_123")
prompt = get_goal_specific_system_prompt(profile)
print(prompt)
```

Example output for weight loss goal:
```
You are a knowledgeable and friendly fitness coach specialized in weight loss.
Your role is to provide personalized fitness advice based on the user's fitness goals and health information.

User Information:
- Name: Alice
- Fitness Level: intermediate
- Primary Goal: weight loss
- Age: 28
- Weight: 75kg
- Height: 165cm

Guidelines for this user:
- Focus on calorie deficit strategies
- Recommend cardio combined with strength training
- Emphasize nutrition and portion control
- Track progress with realistic timelines (1-2 lbs/week)
- Preserve muscle mass during weight loss
```

## File Structure

```
be/
├── fitness_dataset_generator.py      # Generates synthetic training data
├── fitness_llm_trainer.py            # Fine-tuning script
├── app/
│   ├── server.py                     # FastAPI server with new endpoints
│   ├── user_profile.py               # User profile management
│   ├── fitness_llm_inference.py      # Inference engine
│   └── models/
│       └── emotion_model/            # Emotion detection model
├── training_data/                    # Generated datasets
│   ├── fitness_data.jsonl
│   ├── fitness_data_weight_loss.jsonl
│   ├── ...
└── fitness_llm_model/                # Fine-tuned model weights
    ├── adapter_config.json
    ├── adapter_model.bin
    └── ...
```

## Training Details

### Architecture
- **Base Model**: TinyLlama-1.1B-Chat-v1.0
- **Fine-tuning Method**: LoRA (Low-Rank Adaptation)
- **LoRA Config**:
  - Rank (r): 16
  - Alpha: 32
  - Target modules: q_proj, v_proj
  - Dropout: 0.05

### Data Format
JSONL format with fields:
```json
{
  "prompt": "<|system|>\n...\n<|user|>\nquery\n<|assistant|>\n",
  "response": "fitness advice here",
  "goal": "weight_loss",
  "query": "original query",
  "full_text": "complete conversation"
}
```

### Training Configuration
- **Optimizer**: AdamW
- **Batch Size**: 4 (per device)
- **Gradient Accumulation**: 2
- **Learning Rate**: 2e-4
- **Warmup Steps**: 100
- **Epochs**: 3
- **Weight Decay**: 0.01
- **Math Precision**: bfloat16 (GPU) / float32 (CPU)

## Performance Considerations

### Memory Usage
- **Base Model**: ~500MB
- **LoRA Weights**: ~50MB
- **Inference**: ~2GB RAM (CPU) or ~4GB VRAM (GPU)

### Speed
- **Generation**:  ~1-2 seconds per response (GPU)
- **WebSocket latency**: <100ms (excluding TTS)
- **TTS synthesis**: ~2-5 seconds per response

### Optimization Tips
1. Use GPU for inference (10x faster)
2. Batch API requests for multiple users
3. Cache user profiles in memory
4. Use LoRA for faster fine-tuning (30-50% reduction vs full fine-tune)

## Advanced Usage

### Custom Dataset

Create a JSONL file with your own fitness Q&A data:

```python
from fitness_llm_trainer import FitnessLLMTrainer

trainer = FitnessLLMTrainer()
trainer.train(
    train_data_path="custom_fitness_data.jsonl",
    output_dir="custom_fitness_model",
    num_epochs=5,
)
```

### Batch Inference

```python
from app.fitness_llm_inference import FitnessLLMInference
from app.user_profile import UserProfileManager

fitness_llm = FitnessLLMInference(lora_weights_path="fitness_llm_model")
profile_mgr = UserProfileManager()

queries = [
    "How should I structure my workouts?",
    "What should I eat before exercise?",
    "How much sleep do I need?",
]

profile = profile_mgr.get_profile("user_123")
responses = fitness_llm.batch_generate(queries, user_profile=profile)

for q, r in zip(queries, responses):
    print(f"Q: {q}")
    print(f"A: {r}\n")
```

### Inference Without LoRA

Use the base model without fine-tuned weights:

```python
from app.fitness_llm_inference import FitnessLLMInference

fitness_llm = FitnessLLMInference()  # No LoRA weights loaded
response = fitness_llm.generate_fitness_advice(
    query="What's the best workout for beginners?",
    user_profile=profile,
)
```

## Troubleshooting

### Model Loading Issues
```
Error: cannot import name 'FitnessLLMInference'
```
**Solution**: Ensure `app/` is in Python path and `__init__.py` exists in `app/`

### Out of Memory
```
RuntimeError: CUDA out of memory
```
**Solutions**:
- Reduce `batch_size` to 2
- Use CPU: `device="cpu"`
- Reduce `max_length` for generation

### Slow Inference
**Solutions**:
- Use GPU: `torch.cuda.is_available()`
- Use smaller `max_length` (default: 150)
- Cache the model instance

### LoRA Weights Not Loading
```python
# Check if file exists
import os
print(os.path.exists("fitness_llm_model/adapter_config.json"))

# Use base model as fallback
fitness_llm = FitnessLLMInference()
```

## Next Steps

1. **Collect Real Data**: Replace synthetic data with real user queries from your app
2. **Fine-tune on Real Data**: Run trainer on your dataset for better performance
3. **Monitor Performance**: Log queries and responses to improve over time
4. **A/B Testing**: Compare fine-tuned vs base model responses
5. **Domain Expansion**: Add nutrition, supplement, and injury prevention advice

## References

- [TinyLlama Model](https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0)
- [PEFT/LoRA Documentation](https://huggingface.co/docs/peft/)
- [Transformers Training Guide](https://huggingface.co/docs/transformers/)
- [Whisper ASR Model](https://github.com/openai/whisper)
