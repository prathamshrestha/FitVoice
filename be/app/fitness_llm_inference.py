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
    
    def _retrieve_context(self, query: str) -> Tuple[str, List[Dict]]:
        """Retrieve relevant fitness knowledge using RAG.
        Returns (context_string, retrieved_docs_with_scores)"""
        if not self.rag or not self.use_rag:
            return "", []
        
        try:
            context, docs = self.rag.retrieve_hybrid(query, kb_top_k=3, qa_top_k=2)
            return context, docs
        except Exception as e:
            print(f"⚠️ RAG retrieval failed: {e}")
            return "", []
    
    def generate_fitness_advice(
        self,
        query: str,
        user_profile: Optional[UserProfile] = None,
        max_new_tokens: int = 50,
        temperature: float = 0.7,
        top_p: float = 0.9,
        use_rag: bool = True,
        conversation_history: str = "",
    ) -> Dict:
        """Generate fitness advice for a user query with optional profile context and RAG.
        
        Args:
            query: The user's current question
            user_profile: Optional user profile for personalized prompts
            conversation_history: Formatted string of previous turns for context
        
        Returns:
            dict with keys: 'response' (str), 'rag_debug' (dict with confidence info)
        """
        
        # Create context-aware system prompt
        if user_profile:
            system_prompt = get_goal_specific_system_prompt(user_profile)
            print(f"📊 Personalized prompt generated for {user_profile.name} ({user_profile.primary_goal.value})")
            if user_profile.dietary_restrictions:
                print(f"   🥗 Dietary restrictions: {', '.join(user_profile.dietary_restrictions)}")
        else:
            system_prompt = (
                "You are FitVoice, a helpful fitness and nutrition coach. "
                "Answer the user's fitness question directly and concisely in 2-3 sentences. "
                "If reference information is provided below, use it to give an accurate answer. "
                "Speak naturally as if talking to someone — no bullet points or lists. "
                "Be specific with numbers (calories, reps, sets, grams) when relevant."
            )
            print(f"📝 Using generic system prompt (no user profile)")
        
        # Add conversation context instruction if history exists
        if conversation_history:
            system_prompt += (
                "\n\nYou are in an ongoing conversation. Use the previous exchanges "
                "to understand context. If the user refers to something from earlier "
                "(like 'what about that', 'how much more', 'and for lunch?'), "
                "answer based on the conversation history."
            )
        
        # Retrieve knowledge context if RAG enabled
        knowledge_context = ""
        rag_debug = {
            "rag_available": self.rag is not None,
            "rag_used": False,
            "num_docs": 0,
            "sources": [],
            "context_length": 0,
        }
        
        if use_rag and self.rag:
            knowledge_context, retrieved_docs = self._retrieve_context(query)
            if knowledge_context:
                system_prompt += "\n\n" + knowledge_context
                rag_debug["rag_used"] = True
                rag_debug["num_docs"] = len(retrieved_docs)
                rag_debug["context_length"] = len(knowledge_context)
                rag_debug["sources"] = [
                    {
                        "title": doc.get("title", doc.get("question", "N/A"))[:80],
                        "relevance": round(doc.get("relevance", 0), 3),
                        "type": doc.get("source", "kb"),
                    }
                    for doc in retrieved_docs
                ]
                top_rel = retrieved_docs[0].get("relevance", 0) if retrieved_docs else 0
                print(f"RAG: {len(retrieved_docs)} docs for '{query[:50]}' (top: {top_rel:.0%})")
            else:
                print(f"RAG: no relevant docs for '{query[:50]}'")
        
        # Build the full prompt using TinyLlama chat template
        SYS_TAG = "<" + "|system|" + ">"
        USR_TAG = "<" + "|user|" + ">"
        AST_TAG = "<" + "|assistant|" + ">"
        
        # Build multi-turn prompt if conversation history exists
        if conversation_history:
            # Inject history as previous turns in the chat template
            prompt = f"{SYS_TAG}\n{system_prompt}\n"
            # Parse and add previous turns
            for line in conversation_history.split("\n"):
                if line.startswith("User: "):
                    prompt += f"{USR_TAG}\n{line[6:]}\n"
                elif line.startswith("Assistant: "):
                    prompt += f"{AST_TAG}\n{line[11:]}\n"
            # Add current query
            prompt += f"{USR_TAG}\n{query}\n{AST_TAG}\n"
        else:
            prompt = f"{SYS_TAG}\n{system_prompt}\n{USR_TAG}\n{query}\n{AST_TAG}\n"
        
        # Generate response
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            output = self.model.generate(
                input_ids,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                repetition_penalty=1.3,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
        
        # Decode and extract response
        full_response = self.tokenizer.decode(output[0], skip_special_tokens=True)
        response = full_response[len(prompt):].strip()
        
        # Clean up response
        response = response.split(USR_TAG)[0].strip()
        response = response.split(SYS_TAG)[0].strip()
        
        # Validate response against dietary restrictions
        if user_profile and user_profile.dietary_restrictions:
            self._validate_dietary_recommendations(response, user_profile)
        
        return {"response": response, "rag_debug": rag_debug}
    
    def _validate_dietary_recommendations(self, response: str, user_profile) -> None:
        """Check if response respects user's dietary restrictions and log any violations."""
        response_lower = response.lower()
        restrictions_lower = [r.lower() for r in user_profile.dietary_restrictions]
        
        # Define prohibited foods for each restriction
        prohibition_map = {
            'vegan': ['meat', 'beef', 'chicken', 'fish', 'egg', 'dairy', 'milk', 'cheese', 'yogurt', 'butter'],
            'vegetarian': ['meat', 'beef', 'chicken', 'fish'],
            'gluten': ['gluten', 'wheat', 'barley', 'rye', 'bread', 'pasta', 'pizza'],
            'dairy': ['milk', 'cheese', 'yogurt', 'butter', 'cream', 'dairy'],
            'nut': ['nut', 'peanut', 'almond', 'walnut', 'cashew'],
            'keto': ['bread', 'pasta', 'rice', 'sugar', 'fruit', 'carb'],
        }
        
        violations = []
        for restriction in restrictions_lower:
            # Find matching prohibition list
            for key, prohibited_foods in prohibition_map.items():
                if key in restriction:
                    for food in prohibited_foods:
                        if food in response_lower:
                            violations.append(f"{restriction}: mentions '{food}'")
                    break
        
        if violations:
            print(f"⚠️ Dietary violation detected: {', '.join(violations)}")
            print(f"   Consider regenerating with stricter prompt")
        else:
            print(f"✅ Response respects dietary restrictions: {', '.join(restrictions_lower)}")
    
    def generate_personalized_advice(
        self,
        query: str,
        user_id: str,
        profile_manager,
        max_new_tokens: int = 50,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> Tuple[Dict, UserProfile]:
        """Generate advice using stored user profile."""
        
        profile = profile_manager.get_profile(user_id)
        if not profile:
            print(f"⚠️ User profile not found for {user_id}, using default behavior")
        
        result = self.generate_fitness_advice(
            query=query,
            user_profile=profile,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        
        return result, profile
    
    def batch_generate(
        self,
        queries: list,
        user_profile: Optional[UserProfile] = None,
        max_new_tokens: int = 50,
    ) -> list:
        """Generate responses for multiple queries."""
        responses = []
        for query in queries:
            result = self.generate_fitness_advice(
                query=query,
                user_profile=user_profile,
                max_new_tokens=max_new_tokens,
            )
            responses.append(result)
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
        result = fitness_llm.generate_fitness_advice(
            query=query,
            user_profile=test_profile,
            max_new_tokens=120,
        )
        print(f"💭 Response: {result['response']}")
        print(f"📊 RAG Debug: {result['rag_debug']}\n")
