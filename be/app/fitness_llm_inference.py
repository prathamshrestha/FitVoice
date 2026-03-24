"""
Fitness LLM Inference Utility with RAG
Loads fine-tuned fitness model and generates responses with user context and retrieved knowledge.
"""

import sys
import torch
from pathlib import Path
from typing import Optional, Tuple, List, Dict
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# Add app and parent directory to path to support both relative and direct imports
_app_dir = Path(__file__).parent
_parent_dir = _app_dir.parent
if str(_app_dir) not in sys.path:
    sys.path.insert(0, str(_app_dir))
if str(_parent_dir) not in sys.path:
    sys.path.insert(0, str(_parent_dir))

try:
    # Try relative imports first (when run as module)
    from .user_profile import UserProfile, get_goal_specific_system_prompt
except ImportError:
    # Fallback to absolute imports (when running from app directory)
    try:
        from user_profile import UserProfile, get_goal_specific_system_prompt
    except ImportError:
        from app.user_profile import UserProfile, get_goal_specific_system_prompt

# Try to import RAG system
try:
    from fitness_rag_system import HybridFitnessRAG
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("⚠️ RAG system not available. Install dependencies: pip install chromadb sentence-transformers")


class FitnessLLMInference:
    """Inference engine for fitness-specific LLM with RAG support."""
    
    def __init__(
        self,
        base_model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        lora_weights_path: Optional[str] = None,
        device: str = None,
        use_rag: bool = True,
    ):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.lora_weights_path = lora_weights_path
        self.use_rag = use_rag and RAG_AVAILABLE
        self.rag = None
        
        print(f"🤖 Loading fitness LLM on {self.device}...")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load base model
        self.model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else "cpu",
        )
        
        # Load LoRA weights if provided
        if lora_weights_path and Path(lora_weights_path).exists():
            print(f"📦 Loading LoRA weights from {lora_weights_path}...")
            self.model = PeftModel.from_pretrained(self.model, lora_weights_path)
        
        self.model.eval()
        print("✅ Model loaded successfully")
        
        # Initialize RAG system if available
        if self.use_rag:
            self._initialize_rag()
    
    def _initialize_rag(self):
        """Initialize RAG system for knowledge retrieval"""
        try:
            print("🔄 Initializing RAG system...")
            # Look for knowledge base in parent directory
            kb_path = Path(_parent_dir) / "fitness_knowledge_base.jsonl"
            qa_path = Path(_parent_dir) / "training_data" / "fitness_data.jsonl"
            
            if not kb_path.exists():
                print(f"⚠️ Knowledge base not found at {kb_path}")
                print("   Generate it with: python fitness_knowledge_base.py")
                return
            
            self.rag = HybridFitnessRAG(
                knowledge_base_path=str(kb_path),
                qa_pairs_path=str(qa_path) if qa_path.exists() else None
            )
            self.rag.load_knowledge_base()
            print("✅ RAG system initialized")
        except Exception as e:
            print(f"⚠️ Failed to initialize RAG: {e}")
            self.rag = None
    
    def _retrieve_context(self, query: str) -> str:
        """Retrieve relevant fitness knowledge using RAG"""
        if not self.rag or not self.use_rag:
            return ""
        
        try:
            context, _ = self.rag.retrieve_hybrid(query, kb_top_k=3, qa_top_k=2)
            return context
        except Exception as e:
            print(f"⚠️ RAG retrieval failed: {e}")
            return ""
    
    def generate_fitness_advice(
        self,
        query: str,
        user_profile: Optional[UserProfile] = None,
        max_new_tokens: int = 50,
        temperature: float = 0.7,
        top_p: float = 0.9,
        use_rag: bool = True,
    ) -> str:
        """Generate fitness advice for a user query with optional profile context and RAG."""
        
        # Create context-aware system prompt
        if user_profile:
            system_prompt = get_goal_specific_system_prompt(user_profile)
        else:
            system_prompt = """You are a knowledgeable and friendly fitness coach.
Provide safe, evidence-based fitness advice for all fitness levels and goals.
Always consider the user's health and safety in your recommendations."""
        
        # Retrieve knowledge context if RAG enabled
        knowledge_context = ""
        if use_rag and self.rag:
            knowledge_context = self._retrieve_context(query)
            if knowledge_context:
                system_prompt += f"\n\n{knowledge_context}"
        
        # Build the full prompt
        prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{query}\n<|assistant|>\n"
        
        # Generate response
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            output = self.model.generate(
                input_ids,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
        
        # Decode and extract response
        full_response = self.tokenizer.decode(output[0], skip_special_tokens=True)
        response = full_response[len(prompt):].strip()
        
        # Clean up response
        response = response.split("<|user|>")[0].strip()  # Remove any follow-up prompts
        response = response.split("<|system|>")[0].strip()
        
        return response
    
    def generate_personalized_advice(
        self,
        query: str,
        user_id: str,
        profile_manager,
        max_new_tokens: int = 50,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> Tuple[str, UserProfile]:
        """Generate advice using stored user profile."""
        
        profile = profile_manager.get_profile(user_id)
        if not profile:
            print(f"⚠️ User profile not found for {user_id}, using default behavior")
        
        response = self.generate_fitness_advice(
            query=query,
            user_profile=profile,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        
        return response, profile
    
    def batch_generate(
        self,
        queries: list,
        user_profile: Optional[UserProfile] = None,
        max_new_tokens: int = 50,
    ) -> list:
        """Generate responses for multiple queries."""
        responses = []
        for query in queries:
            response = self.generate_fitness_advice(
                query=query,
                user_profile=user_profile,
                max_new_tokens=max_new_tokens,
            )
            responses.append(response)
        return responses


# Global inference engine (lazy loaded)
_fitness_llm = None

def get_fitness_llm(
    base_model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    lora_weights_path: Optional[str] = None,
) -> FitnessLLMInference:
    """Get or create global fitness LLM instance."""
    global _fitness_llm
    
    if _fitness_llm is None:
        _fitness_llm = FitnessLLMInference(
            base_model_name=base_model_name,
            lora_weights_path=lora_weights_path,
        )
    
    return _fitness_llm


if __name__ == "__main__":
    # Example usage
    from app.user_profile import UserProfileManager, FitnessGoal
    
    # Initialize manager
    profile_mgr = UserProfileManager()
    
    # Create a test profile
    test_profile = profile_mgr.create_profile(
        user_id="test_user",
        name="John",
        age=30,
        fitness_level="beginner",
        primary_goal=FitnessGoal.WEIGHT_LOSS,
        weight_kg=95,
        height_cm=180,
    )
    
    # Initialize inference engine
    fitness_llm = FitnessLLMInference()
    
    # Test queries
    test_queries = [
        "How can I lose weight effectively?",
        "What exercises should I do as a beginner?",
        "How much protein do I need?",
    ]
    
    print("\n🧪 Testing Fitness LLM Inference:")
    print("="*50)
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        response = fitness_llm.generate_fitness_advice(
            query=query,
            user_profile=test_profile,
            max_length=120,
        )
        print(f"💭 Response: {response}\n")
