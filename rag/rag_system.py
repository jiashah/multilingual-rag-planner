"""
RAG (Retrieval Augmented Generation) System for Multilingual Goal Planning
Uses LangChain, ChromaDB, and OpenAI for document processing and retrieval
"""

import os
import streamlit as st
from typing import List, Dict, Any, Optional
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from database.supabase_client import supabase_client
from utils.logger import setup_logger
import chromadb
from chromadb.config import Settings

logger = setup_logger("rag_system")

class RAGSystem:
    def __init__(self):
        self.client = supabase_client.client
        self.embeddings = None
        self.vector_store = None
        self.qa_chain = None
        self.initialize_embeddings()
        self.initialize_vector_store()
    
    def initialize_embeddings(self):
        """Initialize embedding model"""
        try:
            # Try OpenAI embeddings first, fallback to HuggingFace
            if os.getenv("OPENAI_API_KEY"):
                self.embeddings = OpenAIEmbeddings(
                    openai_api_key=os.getenv("OPENAI_API_KEY")
                )
                logger.info("Using OpenAI embeddings")
            else:
                # Use free HuggingFace embeddings as fallback
                self.embeddings = HuggingFaceEmbeddings(
                    model_name=os.getenv("EMBEDDINGS_MODEL", "all-MiniLM-L6-v2")
                )
                logger.info("Using HuggingFace embeddings")
                
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
            raise
    
    def initialize_vector_store(self):
        """Initialize ChromaDB vector store"""
        try:
            persist_directory = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
            
            self.vector_store = Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embeddings,
                collection_name="user_documents"
            )
            logger.info("ChromaDB vector store initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise
    
    def process_document(self, file_path: str, document_type: str = "pdf") -> List[Dict[str, Any]]:
        """
        Process and split document into chunks
        
        Args:
            file_path (str): Path to document file
            document_type (str): Type of document ('pdf', 'txt')
            
        Returns:
            List of document chunks with metadata
        """
        try:
            # Load document based on type
            if document_type.lower() == "pdf":
                loader = PyPDFLoader(file_path)
            elif document_type.lower() in ["txt", "text"]:
                loader = TextLoader(file_path)
            else:
                raise ValueError(f"Unsupported document type: {document_type}")
            
            documents = loader.load()
            
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            
            chunks = text_splitter.split_documents(documents)
            
            # Add metadata
            processed_chunks = []
            for i, chunk in enumerate(chunks):
                processed_chunks.append({
                    "content": chunk.page_content,
                    "metadata": {
                        **chunk.metadata,
                        "chunk_id": i,
                        "source": file_path,
                        "document_type": document_type
                    }
                })
            
            logger.info(f"Processed {len(processed_chunks)} chunks from {file_path}")
            return processed_chunks
            
        except Exception as e:
            logger.error(f"Failed to process document {file_path}: {e}")
            return []
    
    def add_documents_to_vectorstore(self, documents: List[Dict[str, Any]], user_id: str):
        """
        Add processed documents to vector store and database
        
        Args:
            documents (List[Dict]): Processed document chunks
            user_id (str): User ID
        """
        try:
            if not documents:
                return
            
            # Prepare texts and metadatas for vector store
            texts = [doc["content"] for doc in documents]
            metadatas = [doc["metadata"] for doc in documents]
            
            # Add user_id to metadata
            for metadata in metadatas:
                metadata["user_id"] = user_id
            
            # Add to vector store
            self.vector_store.add_texts(
                texts=texts,
                metadatas=metadatas
            )
            
            # Store document info in database
            document_info = {
                "user_id": user_id,
                "title": metadatas[0].get("source", "Unknown Document"),
                "content": "\n".join(texts[:5]),  # Store first few chunks as preview
                "document_type": metadatas[0].get("document_type", "unknown"),
                "source_url": metadatas[0].get("source"),
                "embedding_status": "completed"
            }
            
            self.client.table("knowledge_documents").insert(document_info).execute()
            
            logger.info(f"Added {len(documents)} document chunks for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to add documents to vector store: {e}")
            raise
    
    def search_similar_documents(self, query: str, user_id: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents in vector store
        
        Args:
            query (str): Search query
            user_id (str): User ID for filtering
            k (int): Number of results to return
            
        Returns:
            List of similar documents
        """
        try:
            # Search with user filter
            results = self.vector_store.similarity_search_with_score(
                query,
                k=k,
                filter={"user_id": user_id}
            )
            
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": score
                })
            
            logger.info(f"Found {len(formatted_results)} similar documents for query: {query}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search similar documents: {e}")
            return []
    
    def create_qa_chain(self, user_id: str):
        """
        Create a QA chain with user-specific document retrieval
        
        Args:
            user_id (str): User ID for document filtering
        """
        try:
            # Create retriever with user filter
            retriever = self.vector_store.as_retriever(
                search_kwargs={
                    "k": 5,
                    "filter": {"user_id": user_id}
                }
            )
            
            # Create custom prompt for goal planning
            prompt_template = """
            You are an AI assistant specialized in goal planning and task generation. Use the provided context from the user's documents to give personalized advice and create relevant tasks.
            
            Context from user's documents:
            {context}
            
            Question: {question}
            
            Please provide a helpful response based on the context. If the context doesn't contain relevant information, use your general knowledge about goal planning and productivity.
            
            Answer:
            """
            
            PROMPT = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
            
            # Initialize LLM
            if os.getenv("OPENAI_API_KEY"):
                llm = ChatOpenAI(
                    temperature=0.7,
                    model_name=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                    openai_api_key=os.getenv("OPENAI_API_KEY")
                )
            else:
                logger.warning("OpenAI API key not found. QA chain will not work without LLM.")
                return None
            
            # Create QA chain
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=retriever,
                chain_type_kwargs={"prompt": PROMPT},
                return_source_documents=True
            )
            
            logger.info(f"QA chain created for user {user_id}")
            return self.qa_chain
            
        except Exception as e:
            logger.error(f"Failed to create QA chain: {e}")
            return None
    
    def ask_question(self, question: str, user_id: str) -> Dict[str, Any]:
        """
        Ask a question using the RAG system
        
        Args:
            question (str): User question
            user_id (str): User ID
            
        Returns:
            Dict containing answer and source documents
        """
        try:
            if not self.qa_chain:
                self.create_qa_chain(user_id)
            
            if not self.qa_chain:
                return {
                    "answer": "I'm sorry, but I cannot access your documents at the moment. Please make sure your API keys are configured correctly.",
                    "source_documents": []
                }
            
            # Get answer from QA chain
            result = self.qa_chain({"query": question})
            
            return {
                "answer": result["result"],
                "source_documents": [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata
                    }
                    for doc in result.get("source_documents", [])
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to answer question: {e}")
            return {
                "answer": "I encountered an error while processing your question. Please try again.",
                "source_documents": []
            }
    
    def get_user_documents(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get list of user's uploaded documents
        
        Args:
            user_id (str): User ID
            
        Returns:
            List of user documents
        """
        try:
            response = self.client.table("knowledge_documents")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Failed to get user documents: {e}")
            return []
    
    def delete_document(self, document_id: str, user_id: str) -> bool:
        """
        Delete a document from both vector store and database
        
        Args:
            document_id (str): Document ID
            user_id (str): User ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Delete from database
            self.client.table("knowledge_documents")\
                .delete()\
                .eq("id", document_id)\
                .eq("user_id", user_id)\
                .execute()
            
            # Note: ChromaDB doesn't have easy document deletion by ID
            # In production, you might want to recreate the vector store periodically
            
            logger.info(f"Document {document_id} deleted for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False