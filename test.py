from dotenv import load_dotenv
load_dotenv()

from src.nodes.query_analysis import query_analysis_node
from src.nodes.retrieval import retrieval_node

def test_pipeline():
    state = {"question": "how to treat a second-degree burn"}

    print(f"Original Question: {state['question']}")
    
    # Test Query Analysis Node
    print("\n--- Running Query Analysis Node ---")
    qa_result = query_analysis_node(state)
    state.update(qa_result)
    print(f"Rewritten Query: {qa_result['rewritten_query']}")
    print(f"First Aid Category: {qa_result['category']}")

    # Test Retrieval Node
    print("\n--- Running Retrieval Node ---")
    retrieval_result = retrieval_node(state)
    docs = retrieval_result["retrieved_docs"]
    
    print(f"Retrieved {len(docs)} documents.")
    for i, doc in enumerate(docs):
        print(f"\n[Document {i+1}] Source: {doc.metadata.get('source', 'Unknown')}")
        print(f"Preview: {doc.page_content[:200]}...")

if __name__ == "__main__":
    test_pipeline()
