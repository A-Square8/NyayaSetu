from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

class QueryAnalysisOutput(BaseModel):
    rewritten_query: str = Field(description="The rewritten query for better semantic search")
    category: str = Field(description="The first aid/medical situation category (e.g., CPR, burns, bleeding, fractures, poisoning, choking, etc.)")

def query_analysis_node(state):
    q = state["question"]
    llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
    structured_llm = llm.with_structured_output(QueryAnalysisOutput)
    
    prompt = f"Rewrite this query for better semantic retrieval of medical first aid manuals and classify its first aid category: {q}"
    res = structured_llm.invoke(prompt)
    
    return {"rewritten_query": res.rewritten_query, "category": res.category}
