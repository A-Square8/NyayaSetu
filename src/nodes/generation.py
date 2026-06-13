from langchain_google_genai import ChatGoogleGenerativeAI


def generation_node(state):
    q = state["question"]
    docs = state.get("graded_docs", [])

    if not docs:
        return {
            "answer": "I could not find relevant information in the available first aid manuals to answer your question. In a medical emergency, please contact professional emergency services immediately.",
            "sources": []
        }

    ctx = "\n\n---\n\n".join([d.page_content for d in docs])
    sources = list(set([d.metadata.get("source", "Unknown") for d in docs]))

    llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
    prompt = (
        f"You are a professional First Aid AI Assistant. "
        f"Based ONLY on the provided context, provide a clear, step-by-step first aid procedure "
        f"to address the user's situation.\n\n"
        f"Rules:\n"
        f"1. Structure your answer as a clear, numbered step-by-step procedure.\n"
        f"2. Use concise, direct, and active language that is easy to read quickly during an emergency.\n"
        f"3. Highlight critical safety warnings or precautions (e.g., 'DO NOT do X').\n"
        f"4. Cite the specific source document(s) supporting your instructions.\n"
        f"5. If the context does not contain enough information to safely perform the procedure, state that clearly and advise the user to contact emergency services immediately.\n\n"
        f"Question: {q}\n\n"
        f"Context:\n{ctx}"
    )
    res = llm.invoke(prompt)

    answer_content = res.content
    if isinstance(answer_content, list):
        answer_content = "".join([part.get("text", "") for part in answer_content if isinstance(part, dict) and "text" in part])
    elif not isinstance(answer_content, str):
        answer_content = str(answer_content)

    return {"answer": answer_content, "sources": sources}
