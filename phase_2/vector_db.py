import os
from typing import List
from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

class VectorStoreManager:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        # Using a fast, local HuggingFace embedding model for seamless testing
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectorstore = None

    def initialize_store(self, documents: List[Document] = None):
        """
        Initializes ChromaDB. If documents are provided, it creates a new index from them.
        Otherwise, it loads the existing index from disk.
        """
        if documents:
            print(f"Indexing {len(documents)} chunks into ChromaDB...")
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
            self.vectorstore.persist()
            print("Indexing complete!")
        else:
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
        return self.vectorstore

    def get_retriever(self, search_kwargs: dict = {"k": 3}):
        """
        Returns a base retriever.
        """
        if not self.vectorstore:
            self.initialize_store()
        return self.vectorstore.as_retriever(search_kwargs=search_kwargs)

    def hybrid_search(self, query: str, filter_metadata: dict = None, k: int = 5) -> List[Document]:
        """
        Performs semantic search with optional metadata filtering (hybrid search logic).
        """
        if not self.vectorstore:
            self.initialize_store()
        
        search_kwargs = {"k": k}
        if filter_metadata:
            # ChromaDB filter syntax: {"$and": [{"fund_name": {"$eq": "HDFC..."}}, ...]} or simple {"fund_name": "HDFC..."}
            search_kwargs["filter"] = filter_metadata
            
        docs = self.vectorstore.similarity_search(query, **search_kwargs)
        return docs
