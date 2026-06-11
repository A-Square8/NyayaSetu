from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

class QueryAnalysisOutput(BaseModel):
    rewritten_query: str = Field(description="The rewritten query for better semantic search")
    category: str = Field(description="The legal category (e.g. consumer protection, labour rights, etc.)")

def query_analysis_node(state):
    q = state["question"]
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    structured_llm = llm.with_structured_output(QueryAnalysisOutput)
    
    prompt = f"Rewrite this query for better retrieval and classify its legal category: {q}"
    res = structured_llm.invoke(prompt)
    
    return {"rewritten_query": res.rewritten_query, "category": res.category}
