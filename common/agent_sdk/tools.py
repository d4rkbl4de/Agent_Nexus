import json
from typing import Dict, Any, List

from common.data_sdk import VectorClient

def create_vector_search_tool(vector_client: VectorClient, collection_name: str):
    
    def vector_memory_search(query_text: str) -> str:
        """
        Tool used for retrieving relevant, up-to-date context from the shared Vector Memory 
        (Qdrant). This enables Retrieval-Augmented Generation (RAG).
        
        Args:
            query_text: The user's query or a synthesized query based on the LLM's internal
                        thought process (e.g., "Find notes about the EOD Friday task").
                        
        Returns:
            A JSON string containing the relevant memory snippets (text, score, metadata).
            The LLM will read this JSON and synthesize an answer.
        """
        print(f"\n[TOOL CALLED] Vector Search for collection: '{collection_name}'")
        print(f"[QUERY] {query_text}")
        
        results = vector_client.search(
            collection_name=collection_name, 
            query_text=query_text, 
            top_k=3
        )
        
        if not results:
            return "No relevant context found in Vector Memory for that query."

        formatted_results = []
        for i, item in enumerate(results):
            formatted_results.append({
                "id": i + 1,
                "score": round(item['score'], 4),
                "source": item['metadata'].get('source', 'Unknown'),
                "content_snippet": item['text']
            })
            
        return json.dumps(formatted_results, indent=2)

    tool_name = f"vector_memory_search_{collection_name.lower().replace('-', '_')}"
    vector_memory_search.__name__ = tool_name
    vector_memory_search.__doc__ = vector_memory_search.__doc__.strip()
    
    return vector_memory_search

if __name__ == "__main__":
    from common.ai_sdk import AIClient
    from common.data_sdk import VectorClient

    llm_client = AIClient(model_name="gpt-4o-mini")
    vector_client = VectorClient(ai_client=llm_client)

    COLLECTION_NAME = "test_tools_knowledge"
    
    rag_tool = create_vector_search_tool(vector_client, COLLECTION_NAME)

    test_data = [
        "The current roadmap requires all agent lobes to be async-ready by Week 8.",
        "Kakarot's favorite anime is One Piece, followed by Naruto."
    ]
    test_metadata = [
        {"source": "roadmap_v1"},
        {"source": "user_profile"}
    ]
    print("\n--- Ingesting Test Data for Tool ---")
    vector_client.upsert_documents(COLLECTION_NAME, test_data, test_metadata)

    test_query = "What is Kakarot's second favorite anime?"
    print(f"\n--- Testing Tool Execution: {rag_tool.__name__} ---")
    
    tool_output = rag_tool(query_text=test_query)
    
    print(f"\n[Tool Output (Raw JSON to be sent back to the LLM)]:\n{tool_output}")
    print("\n[TOOLS TEST COMPLETE]")