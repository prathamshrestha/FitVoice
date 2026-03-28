"""
RAG System with Chroma Vector Database
Retrieves relevant fitness knowledge for context-aware responses
"""

import json
import os
from typing import List, Dict, Tuple
import numpy as np

# Lazy imports for optional dependencies
try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    print("⚠️ Chroma not installed. Install with: pip install chromadb")

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("⚠️ sentence-transformers not installed. Install with: pip install sentence-transformers")


class FitnessRAGSystem:
    """Retrieval-Augmented Generation for fitness advice"""
    
    def __init__(self, knowledge_base_path: str = "fitness_knowledge_base.jsonl", collection_name: str = "fitness_kb", persist_dir: str = "./chroma_db"):
        """
        Initialize RAG system with Chroma vector database
        
        Args:
            knowledge_base_path: Path to JSONL knowledge base file
            collection_name: Name of the Chroma collection
        """
        if not CHROMA_AVAILABLE or not EMBEDDINGS_AVAILABLE:
            raise RuntimeError("Chroma and sentence-transformers required. Install with: pip install chromadb sentence-transformers")
        
        self.knowledge_base_path = knowledge_base_path
        self.collection_name = collection_name
        
        # Initialize embedding model
        print("🔄 Loading embedding model...")
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")  # Fast, lightweight (~22MB)
        
        # Initialize Chroma client with persistent storage
        print("🔄 Initializing Chroma database...")
        self.persist_dir = persist_dir
        try:
            self.chroma_client = chromadb.PersistentClient(path=persist_dir)
            print(f"   📁 Persistent storage: {os.path.abspath(persist_dir)}")
        except Exception as e:
            print(f"⚠️ PersistentClient failed ({e}), falling back to in-memory")
            self.chroma_client = chromadb.Client()
        
        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        self.loaded = False
    
    def load_knowledge_base(self, force_reload: bool = False) -> int:
        """
        Load and embed knowledge base into Chroma.
        Skips re-embedding if data already exists in persistent DB.
        
        Args:
            force_reload: Force reload even if already loaded
            
        Returns:
            Number of documents loaded
        """
        # Check if data already exists in persistent storage
        existing_count = self.collection.count()
        if existing_count > 0 and not force_reload:
            print(f"✅ Knowledge base already loaded from disk ({existing_count} documents)")
            self.loaded = True
            return existing_count
        
        if not os.path.exists(self.knowledge_base_path):
            raise FileNotFoundError(f"Knowledge base not found: {self.knowledge_base_path}")
        
        # Clear existing data if force reloading
        if force_reload and existing_count > 0:
            self.chroma_client.delete_collection(self.collection_name)
            self.collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        
        # Load documents
        documents = []
        metadatas = []
        ids = []
        
        print(f"📖 Loading knowledge base from {self.knowledge_base_path}...")
        with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                doc = json.loads(line)
                documents.append(doc['content'])
                metadatas.append({
                    'title': doc['title'],
                    'category': doc['category'],
                })
                ids.append(f"doc_{i}")
        
        if not documents:
            raise ValueError("No documents loaded from knowledge base")
        
        print(f"🔄 Generating embeddings for {len(documents)} documents...")
        embeddings = self.embedder.encode(documents, show_progress_bar=True)
        
        # Add to collection
        print("🔄 Storing in Chroma...")
        self.collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
            documents=documents
        )
        
        self.loaded = True
        print(f"✅ Loaded {len(documents)} documents into Chroma (persisted to disk)")
        return len(documents)
    
    def retrieve(self, query: str, top_k: int = 5, min_distance: float = 0.3) -> List[Dict]:
        """
        Retrieve relevant knowledge documents
        
        Args:
            query: User query or fitness question
            top_k: Number of results to return
            min_distance: Minimum similarity threshold (0-1)
            
        Returns:
            List of relevant documents with relevance scores
        """
        if not self.loaded:
            raise RuntimeError("Knowledge base not loaded. Call load_knowledge_base() first")
        
        # Generate query embedding
        query_embedding = self.embedder.encode(query)
        
        # Search Chroma
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )
        
        # Format results
        retrieved = []
        if results['ids'] and len(results['ids']) > 0:
            for i, doc_id in enumerate(results['ids'][0]):
                # Chroma returns distances, convert to similarity (0-1)
                distance = results['distances'][0][i] if results['distances'] else 0
                similarity = 1 - distance  # For cosine distance
                
                # Only include if above threshold
                if similarity >= min_distance:
                    retrieved.append({
                        'id': doc_id,
                        'content': results['documents'][0][i],
                        'title': results['metadatas'][0][i].get('title', 'Unknown'),
                        'category': results['metadatas'][0][i].get('category', 'unknown'),
                        'relevance': float(similarity),
                    })
        
        return retrieved
    
    def format_retrieved_context(self, retrieved_docs: List[Dict]) -> str:
        """
        Format retrieved documents into LLM context prompt
        
        Args:
            retrieved_docs: List of retrieved documents
            
        Returns:
            Formatted context string for LLM
        """
        if not retrieved_docs:
            return ""
        
        context = "📚 **Fitness Knowledge Base:**\n"
        for i, doc in enumerate(retrieved_docs, 1):
            context += f"\n{i}. **{doc['title']}** (Category: {doc['category']}, Relevance: {doc['relevance']:.1%})\n"
            context += f"   {doc['content'][:200]}...\n" if len(doc['content']) > 200 else f"   {doc['content']}\n"
        
        return context
    
    def retrieve_and_format(self, query: str, top_k: int = 5) -> Tuple[List[Dict], str]:
        """
        Retrieve documents and format context in one call
        
        Args:
            query: User query
            top_k: Number of results
            
        Returns:
            Tuple of (retrieved_docs, formatted_context)
        """
        retrieved = self.retrieve(query, top_k=top_k)
        context = self.format_retrieved_context(retrieved)
        return retrieved, context
    
    def get_stats(self) -> Dict:
        """Get collection statistics"""
        count = self.collection.count()
        return {
            'total_documents': count,
            'collection_name': self.collection_name,
            'embedding_model': 'all-MiniLM-L6-v2',
            'vector_dimension': 384,
        }


class HybridFitnessRAG(FitnessRAGSystem):
    """Hybrid RAG: Knowledge retrieval + Semantic Q&A retrieval"""
    
    def __init__(self, 
                 knowledge_base_path: str = "fitness_knowledge_base.jsonl",
                 qa_pairs_path: str = "training_data/fitness_data.jsonl"):
        """
        Initialize hybrid RAG with both knowledge base and Q&A pairs
        
        Args:
            knowledge_base_path: Path to knowledge base
            qa_pairs_path: Path to training Q&A pairs
        """
        super().__init__(knowledge_base_path, collection_name="fitness_kb")
        
        self.qa_pairs_path = qa_pairs_path
        self.qa_collection = None
        self._load_qa_collection()
    
    def _load_qa_collection(self):
        """Load Q&A examples collection. Skips if already persisted."""
        if not self.qa_pairs_path or not os.path.exists(self.qa_pairs_path):
            print(f"⚠️ Q&A pairs not found: {self.qa_pairs_path}")
            return
        
        self.qa_collection = self.chroma_client.get_or_create_collection(
            name="fitness_qa_pairs",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Skip if data already exists in persistent storage
        existing_count = self.qa_collection.count()
        if existing_count > 0:
            print(f"✅ Q&A pairs already loaded from disk ({existing_count} pairs)")
            return
        
        # Load Q&A pairs
        qa_documents = []
        qa_metadatas = []
        qa_ids = []
        
        print(f"📖 Loading Q&A pairs from {self.qa_pairs_path}...")
        with open(self.qa_pairs_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                qa = json.loads(line)
                # Use question as searchable text
                qa_documents.append(qa['question'])
                qa_metadatas.append({
                    'question': qa['question'],
                    'answer': qa['answer'],
                })
                qa_ids.append(f"qa_{i}")
        
        if qa_documents:
            print(f"🔄 Embedding {len(qa_documents)} Q&A pairs...")
            qa_embeddings = self.embedder.encode(qa_documents, show_progress_bar=True)
            
            print("🔄 Storing Q&A pairs in Chroma...")
            BATCH_SIZE = 5000
            qa_embeddings_list = qa_embeddings.tolist()
            for start in range(0, len(qa_documents), BATCH_SIZE):
                end = min(start + BATCH_SIZE, len(qa_documents))
                self.qa_collection.add(
                    ids=qa_ids[start:end],
                    embeddings=qa_embeddings_list[start:end],
                    metadatas=qa_metadatas[start:end],
                    documents=qa_documents[start:end]
                )
                print(f"   Added batch {start//BATCH_SIZE + 1} ({end}/{len(qa_documents)})")
            print(f"✅ Loaded {len(qa_documents)} Q&A pairs (persisted to disk)")
    
    def retrieve_hybrid(self, query: str, kb_top_k: int = 3, qa_top_k: int = 2) -> Tuple[str, List[Dict]]:
        """
        Retrieve from both knowledge base and Q&A pairs
        
        Args:
            query: User query
            kb_top_k: Number of knowledge documents to retrieve
            qa_top_k: Number of Q&A examples to retrieve
            
        Returns:
            Tuple of (formatted_context, all_retrieved_docs)
        """
        # Retrieve from knowledge base
        kb_docs = self.retrieve(query, top_k=kb_top_k)
        
        # Retrieve similar Q&A examples
        qa_examples = []
        if self.qa_collection and self.qa_collection.count() > 0:
            query_embedding = self.embedder.encode(query)
            qa_results = self.qa_collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=qa_top_k
            )
            
            if qa_results['ids'] and len(qa_results['ids']) > 0:
                for i, qa_id in enumerate(qa_results['ids'][0]):
                    distance = qa_results['distances'][0][i] if qa_results['distances'] else 0
                    similarity = 1 - distance
                    
                    if similarity >= 0.2:  # Lower threshold for examples
                        qa_examples.append({
                            'id': qa_id,
                            'question': qa_results['metadatas'][0][i]['question'],
                            'answer': qa_results['metadatas'][0][i]['answer'],
                            'relevance': float(similarity),
                        })
        
        # Format combined context
        context = "📚 **Fitness Knowledge Base & Examples:**\n"
        
        # Add knowledge base
        if kb_docs:
            context += "\n**Key Knowledge:**\n"
            for doc in kb_docs:
                context += f"  • **{doc['title']}**: {doc['content'][:150]}...\n"
        
        # Add Q&A examples
        if qa_examples:
            context += "\n**Similar Q&A Examples:**\n"
            for example in qa_examples:
                context += f"  • Q: {example['question']}\n"
                context += f"    A: {example['answer'][:150]}...\n"
        
        all_docs = kb_docs + qa_examples
        return context, all_docs
    
    def get_full_stats(self) -> Dict:
        """Get statistics for both collections"""
        stats = super().get_stats()
        stats['qa_examples'] = self.qa_collection.count() if self.qa_collection else 0
        return stats


if __name__ == "__main__":
    # Example usage
    print("🚀 Testing Fitness RAG System...\n")
    
    try:
        # Initialize hybrid RAG
        rag = HybridFitnessRAG()
        
        # Load knowledge base
        rag.load_knowledge_base()
        
        # Test retrieval
        query = "How much protein should I eat for muscle building?"
        print(f"\n🔍 Query: '{query}'\n")
        
        retrieved, context = rag.retrieve_and_format(query)
        print(context)
        
        # Test hybrid retrieval
        print("\n" + "="*60)
        print("HYBRID RETRIEVAL TEST")
        print("="*60)
        query2 = "I want to gain muscle but also improve my cardiovascular fitness"
        print(f"\n🔍 Query: '{query2}'\n")
        
        context, docs = rag.retrieve_hybrid(query2)
        print(context)
        
        print("\n📊 Stats:", rag.get_full_stats())
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure to:")
        print("  1. Run: pip install chromadb sentence-transformers")
        print("  2. Generate knowledge base: python fitness_knowledge_base.py")
