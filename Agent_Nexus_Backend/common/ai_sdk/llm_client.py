import os
from typing import List, Optional, Dict, Any, Union

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.language_models import BaseChatModel, BaseEmbeddings

class EmbeddingProvider:
    
    def __init__(self, model_name: str = "text-embedding-3-large"):
        self.model = model_name
        self._provider = OpenAIEmbeddings(model=model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._provider.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._provider.embed_query(text)

    def get_dimension(self) -> int:
        return 3072

class AIClient:
    
    def __init__(self, model_name: str = "gpt-4o"):
        self.default_model = model_name
        
        self._embedding_provider = EmbeddingProvider()
        print(f"AIClient initialized. Default Chat Model: {self.default_model}")
        print(f"Embedding Model: {self._embedding_provider.model} ({self._embedding_provider.get_dimension()} dim)")

    def get_chat_model(self, model_name: Optional[str] = None, temperature: float = 0.7) -> BaseChatModel:
        
        model_to_use = model_name if model_name else self.default_model
        
        return ChatOpenAI(
            model=model_to_use, 
            temperature=temperature,
        )

    def get_embedding_provider(self) -> EmbeddingProvider:
        
        return self._embedding_provider

if __name__ == "__main__":
    ai_client = AIClient(model_name="gpt-4o-mini")
    
    chat_model = ai_client.get_chat_model()
    
    print("\n--- Testing Chat Model Invocation (Brain function) ---")
    response = chat_model.invoke("Explain the difference between LangChain and LangGraph in two sentences.")
    print(f"LLM Response: {response.content}")
    
    embedder = ai_client.get_embedding_provider()
    
    print("\n--- Testing Embedding Provider (Memory Encoding function) ---")
    query = "What is the key to mastering ultra instinct?"
    vector = embedder.embed_query(query)
    
    print(f"Original Query: '{query}'")
    print(f"Generated Vector Dimension: {len(vector)}")
    print(f"Vector Snippet: [{vector[0]:.4f}, {vector[1]:.4f}, ...]")