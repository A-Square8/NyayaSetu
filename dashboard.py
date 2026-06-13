import os
import uuid
import gradio as gr
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.graph import build_graph

# Build the LangGraph
print("Initializing LangGraph pipeline...")
graph = build_graph()

def process_query(question):
    if not question.strip():
        return "Please enter a valid question.", "N/A", "N/A", "N/A", "N/A"
    
    session_id = str(uuid.uuid4())
    
    try:
        # Invoke LangGraph
        result = graph.invoke({
            "question": question,
            "retry_count": 0,
            "chat_history": [],
            "session_id": session_id,
            "web_search_used": False
        })
        
        answer = result.get("answer", "No answer generated.")
        sources = ", ".join(result.get("sources", [])) if result.get("sources") else "None"
        category = result.get("category", "Unknown")
        web_search = "Yes" if result.get("web_search_used", False) else "No"
        
        # Hallucination checking
        h_score = result.get("hallucination_score", 0.0)
        # Check if grading resulted in any documents
        has_docs = len(result.get("graded_docs", [])) > 0 or result.get("web_search_used", False)
        
        if not has_docs:
            hallucination_status = "No relevant context found. Advised emergency services."
        elif h_score >= 0.5:
            hallucination_status = f"Warning: Potential Hallucination Detected (Score: {h_score})"
        else:
            hallucination_status = "Grounded & Validated (Passes Hallucination Check)"
            
        return answer, category, web_search, hallucination_status, sources
    
    except Exception as e:
        return f"An error occurred: {str(e)}", "Error", "Error", "Error", "Error"

# Custom CSS for the orange-white theme and premium look
custom_css = """
.gradio-container {
    font-family: 'Inter', -apple-system, sans-serif;
}
button.primary {
    background-color: #ff6600 !important;
    border-color: #ff6600 !important;
    color: white !important;
}
button.primary:hover {
    background-color: #e05500 !important;
}
"""

with gr.Blocks() as demo:
    gr.Markdown("# 🧡 First Aid AI Assistant Dashboard")
    gr.Markdown("Type a medical emergency question below to retrieve step-by-step first aid procedures.")
    
    with gr.Row():
        with gr.Column(scale=2):
            question_input = gr.Textbox(
                label="Ask a First Aid Question", 
                placeholder="e.g., How to treat a minor burn? What to do for a snake bite?", 
                lines=3
            )
            submit_btn = gr.Button("Get First Aid Procedure", variant="primary")
            answer_output = gr.Textbox(
                label="Step-by-Step Procedure", 
                lines=10, 
                interactive=False
            )
            
        with gr.Column(scale=1):
            category_output = gr.Textbox(
                label="First Aid Category", 
                interactive=False
            )
            hallucination_output = gr.Textbox(
                label="Hallucination / Grounding Status", 
                interactive=False
            )
            web_search_output = gr.Textbox(
                label="Web Search Used?", 
                interactive=False
            )
            sources_output = gr.Textbox(
                label="Sources Reference", 
                interactive=False
            )
            
    submit_btn.click(
        fn=process_query,
        inputs=[question_input],
        outputs=[answer_output, category_output, web_search_output, hallucination_output, sources_output]
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0", 
        server_port=7860,
        theme=gr.themes.Default(primary_hue="orange", secondary_hue="orange"),
        css=custom_css
    )
