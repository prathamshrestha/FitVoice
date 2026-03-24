#!/usr/bin/env python3
"""
FitVoice RAG Setup Script
Generates fitness knowledge base and prepares RAG system

Usage:
    python setup_rag.py
"""

import os
import sys
from pathlib import Path

def main():
    print("=" * 70)
    print("🚀 FitVoice RAG System Setup")
    print("=" * 70)
    
    # Change to be directory
    be_dir = Path(__file__).parent
    os.chdir(be_dir)
    
    print(f"\n📍 Working directory: {be_dir}\n")
    
    # Step 1: Generate knowledge base
    print("Step 1️⃣: Generating Fitness Knowledge Base...")
    print("-" * 70)
    try:
        from fitness_knowledge_base import FitnessKnowledgeBase
        
        kb = FitnessKnowledgeBase()
        num_docs = kb.save_to_jsonl("fitness_knowledge_base.jsonl")
        print(f"✅ Generated {num_docs} knowledge documents\n")
    except Exception as e:
        print(f"❌ Failed to generate knowledge base: {e}\n")
        return False
    
    # Step 2: Check for required packages
    print("Step 2️⃣: Checking dependencies...")
    print("-" * 70)
    required_packages = ['chromadb', 'sentence-transformers']
    missing = []
    
    for pkg in required_packages:
        try:
            __import__(pkg.replace('-', '_'))
            print(f"✅ {pkg} is installed")
        except ImportError:
            print(f"❌ {pkg} is NOT installed")
            missing.append(pkg)
    
    if missing:
        print(f"\n📦 Installing missing packages: {', '.join(missing)}")
        import subprocess
        for pkg in missing:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        print("\n✅ Packages installed\n")
    else:
        print()
    
    # Step 3: Initialize RAG system
    print("Step 3️⃣: Initializing RAG System...")
    print("-" * 70)
    try:
        from fitness_rag_system import HybridFitnessRAG
        
        print("Creating RAG system...")
        rag = HybridFitnessRAG()
        
        # Load knowledge base into Chroma
        print("Loading knowledge base into vector database...")
        num_loaded = rag.load_knowledge_base()
        
        # Get stats
        stats = rag.get_full_stats()
        print(f"\n✅ RAG System Ready!")
        print(f"   • Knowledge documents: {stats['total_documents']}")
        print(f"   • Q&A examples: {stats['qa_examples']}")
        print(f"   • Vector DB: {stats['embedding_model']}\n")
        
    except Exception as e:
        print(f"❌ Failed to initialize RAG: {e}\n")
        return False
    
    # Step 4: Test RAG
    print("Step 4️⃣: Testing RAG System...")
    print("-" * 70)
    try:
        test_query = "How much protein should I eat to build muscle?"
        print(f"Test Query: \"{test_query}\"\n")
        
        retrieved, context = rag.retrieve_and_format(test_query, top_k=3)
        print(context)
        
        if retrieved:
            print(f"\n✅ RAG retrieval working! Found {len(retrieved)} relevant documents\n")
        else:
            print("⚠️ No documents retrieved\n")
        
    except Exception as e:
        print(f"❌ RAG test failed: {e}\n")
        return False
    
    # Step 5: Test integration with LLM
    print("Step 5️⃣: Testing LLM with RAG Integration...")
    print("-" * 70)
    try:
        from app.fitness_llm_inference import FitnessLLMInference
        
        print("Loading fitness LLM...")
        llm = FitnessLLMInference(use_rag=True)
        
        if llm.rag:
            print("✅ LLM loaded with RAG support\n")
            
            # Test query
            test_q = "What's a good workout for weight loss?"
            print(f"Test LLM Query: \"{test_q}\"")
            print("Generating response (this may take a moment)...\n")
            
            response = llm.generate_fitness_advice(test_q, use_rag=True)
            print(f"LLM Response:\n{response}\n")
            print("✅ LLM generation successful!\n")
        else:
            print("⚠️  LLM loaded but RAG not available\n")
        
    except Exception as e:
        print(f"⚠️ LLM test skipped (normal at this point): {e}\n")
    
    # Success message
    print("=" * 70)
    print("✅ FitVoice RAG Setup Complete!")
    print("=" * 70)
    print("\n📚 Knowledge Base Features:")
    print("   ✓ Nutrition guidelines (macros, micros, meal timing)")
    print("   ✓ Workout programs (strength, cardio, flexibility)")
    print("   ✓ Health & wellness (sleep, injury prevention, recovery)")
    print("   ✓ Goal-specific advice (weight loss, muscle building, etc.)")
    print("\n🚀 Next Steps:")
    print("   1. Start the backend: uvicorn server:app --reload")
    print("   2. Start the frontend: npm run dev")
    print("   3. Test voice chat with RAG-enhanced responses")
    print("\n💡 Tips:")
    print("   • First query may be slow (model loading + RAG retrieval)")
    print("   • Responses use retrieved fitness knowledge for accuracy")
    print("   • Hybrid RAG pulls from both KB and Q&A examples")
    print("\n" + "=" * 70 + "\n")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
