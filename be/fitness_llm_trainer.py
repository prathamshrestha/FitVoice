"""
TinyLlama Fine-tuning Script for Fitness Domain
Trains TinyLlama on fitness-specific Q&A data using LoRA for efficient fine-tuning.
"""

import os
import json
import torch
from pathlib import Path
from typing import Optional
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType
import numpy as np


class FitnessLLMTrainer:
    def __init__(
        self,
        model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        device: str = None,
        use_lora: bool = True
    ):
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.use_lora = use_lora
        
        print(f"🤖 Loading model: {model_name}")
        print(f"📱 Device: {self.device}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else "cpu"
        )
        
        # Apply LoRA if enabled
        if self.use_lora:
            self._setup_lora()
    
    def _setup_lora(self):
        """Setup LoRA configuration for efficient fine-tuning."""
        print("⚙️ Setting up LoRA configuration...")
        
        lora_config = LoraConfig(
            r=16,  # rank
            lora_alpha=32,
            target_modules=["q_proj", "v_proj"],  # Target attention layers
            lora_dropout=0.05,
            bias="none",
            task_type=TaskType.CAUSAL_LM
        )
        
        self.model = get_peft_model(self.model, lora_config)
        self.model.print_trainable_parameters()
    
    def load_dataset(self, data_path: str) -> Dataset:
        """Load JSONL dataset for fine-tuning."""
        print(f"📂 Loading dataset from {data_path}")
        
        data_list = []
        with open(data_path, 'r') as f:
            for line in f:
                data_list.append(json.loads(line))
        
        # Create dataset from dict
        dataset = Dataset.from_dict({
            "text": [item["full_text"] for item in data_list]
        })
        
        print(f"✅ Loaded {len(dataset)} training examples")
        return dataset
    
    def preprocess_function(self, examples):
        """Tokenize the dataset."""
        tokenized = self.tokenizer(
            examples["text"],
            max_length=512,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        # For causal LM, labels = input_ids
        tokenized["labels"] = tokenized["input_ids"].clone()
        
        return tokenized
    
    def train(
        self,
        train_data_path: str,
        output_dir: str = "fitness_llm_model",
        num_epochs: int = 3,
        batch_size: int = 4,
        learning_rate: float = 2e-4,
        warmup_steps: int = 100,
        eval_steps: int = 100,
        save_steps: int = 100,
        logging_steps: int = 10,
    ):
        """Fine-tune the model on fitness data."""
        
        # Load and preprocess dataset
        dataset = self.load_dataset(train_data_path)
        
        print("🔄 Tokenizing dataset...")
        tokenized_dataset = dataset.map(
            self.preprocess_function,
            batched=True,
            remove_columns=["text"],
            desc="Tokenizing"
        )
        
        # Create training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            overwrite_output_dir=True,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            learning_rate=learning_rate,
            warmup_steps=warmup_steps,
            weight_decay=0.01,
            logging_steps=logging_steps,
            save_steps=save_steps,
            eval_steps=eval_steps,
            save_strategy="steps",
            logging_strategy="steps",
            optim="adamw_torch",
            bf16=torch.cuda.is_available(),  # Use bfloat16 if GPU available
            gradient_accumulation_steps=2,
            dataloader_pin_memory=True,
        )
        
        # Create trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_dataset,
            data_collator=DataCollatorForLanguageModeling(
                tokenizer=self.tokenizer,
                mlm=False  # Causal LM, not MLM
            ),
        )
        
        # Train
        print("🚀 Starting fine-tuning...")
        trainer.train()
        
        # Save model
        if self.use_lora:
            self.model.save_pretrained(output_dir)
            print(f"✅ LoRA weights saved to {output_dir}")
        else:
            self.model.save_pretrained(output_dir)
            self.tokenizer.save_pretrained(output_dir)
            print(f"✅ Model saved to {output_dir}")
    
    def generate_response(
        self,
        prompt: str,
        max_length: int = 100,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> str:
        """Generate a response given a prompt."""
        
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            output = self.model.generate(
                input_ids,
                max_length=max_length,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        
        response = self.tokenizer.decode(output[0], skip_special_tokens=True)
        # Extract only the generated part (remove prompt)
        return response[len(prompt):]


def main():
    """Example usage of the FitnessLLMTrainer."""
    
    # Initialize trainer
    trainer = FitnessLLMTrainer(
        model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        use_lora=True
    )
    
    # Train on fitness data
    trainer.train(
        train_data_path="training_data/fitness_data.jsonl",
        output_dir="fitness_llm_model",
        num_epochs=3,
        batch_size=4,
        learning_rate=2e-4,
        warmup_steps=100,
        save_steps=200,
        logging_steps=10,
    )
    
    # Test generation
    print("\n🧪 Testing fine-tuned model:")
    test_prompt = "<|system|>\nYou are a helpful fitness coach.\n<|user|>\nWhat's the best way to lose weight?\n<|assistant|>\n"
    response = trainer.generate_response(test_prompt)
    print(f"Response: {response}")


if __name__ == "__main__":
    main()
