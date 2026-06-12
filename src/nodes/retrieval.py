from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

def retrieval_node(state):
    q = state["rewritten_query"]
    emb = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma(persist_directory="data/chroma", embedding_function=emb)
    
    docs = db.similarity_search(q, k=5)
    return {"retrieved_docs": docs}
