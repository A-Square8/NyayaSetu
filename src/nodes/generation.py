from langchain_google_genai import ChatGoogleGenerativeAI


def generation_node(state):
    q = state["question"]
    docs = state.get("graded_docs", [])

    if not docs:
        return {
            "answer": "I could not find relevant information in the available legal documents to answer your question.",
            "sources": []
        }

    ctx = "\n\n---\n\n".join([d.page_content for d in docs])
    sources = list(set([d.metadata.get("source", "Unknown") for d in docs]))

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    prompt = (
        f"You are NyayaSetu, a legal assistant for Indian law. "
        f"Answer the following question using ONLY the provided context. "
        f"Cite which document(s) support your answer. "
        f"If the context doesn't fully answer the question, say so.\n\n"
        f"Question: {q}\n\n"
        f"Context:\n{ctx}"
    )
    res = llm.invoke(prompt)

    return {"answer": res.content, "sources": sources}
