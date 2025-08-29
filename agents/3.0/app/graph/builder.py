from langgraph.graph import StateGraph, END
from app.graph.state import GraphState
from app.graph import nodes
from app.graph import edges

# To visualize the graph (optional, requires matplotlib and pygraphviz)
from PIL import Image
import io

def build_graph():
    """
    Builds the LangGraph agent.
    
    Returns:
        A compiled LangGraph app.
    """
    workflow = StateGraph(GraphState)

    # --- Add Nodes ---
    workflow.add_node("classify_input", nodes.classify_input)
    workflow.add_node("conversational_response", nodes.conversational_response)
    workflow.add_node("check_clarity", nodes.check_clarity)
    workflow.add_node("ask_clarifying_questions", nodes.ask_clarifying_questions)
    workflow.add_node("strategic_planner", nodes.strategic_planner)
    workflow.add_node("check_simplicity", nodes.check_simplicity)
    workflow.add_node("simplify_plan", nodes.simplify_plan)

    # --- Set Entry Point ---
    workflow.set_entry_point("classify_input")

    # --- Add Edges ---
    
    # Conditional edge after classification
    workflow.add_conditional_edges(
        "classify_input",
        edges.route_after_classification,
        {
            "conversational_response": "conversational_response",
            "check_clarity": "check_clarity"
        }
    )
    
    # Conditional edge after clarity check
    workflow.add_conditional_edges(
        "check_clarity",
        edges.route_after_clarity_check,
        {
            "ask_clarifying_questions": "ask_clarifying_questions",
            "strategic_planner": "strategic_planner"
        }
    )
    
    # Conditional edge after simplicity check
    workflow.add_conditional_edges(
        "check_simplicity",
        edges.route_after_simplicity_check,
        {
            "simplify_plan": "simplify_plan",
            "__end__": END
        }
    )

    # --- Add Normal Edges for Loops and Connections ---
    
    # Loop back from asking questions to checking clarity again
    workflow.add_edge("ask_clarifying_questions", "check_clarity")
    
    # Go from planner to simplicity check
    workflow.add_edge("strategic_planner", "check_simplicity")
    
    # Loop back from simplifying the plan to checking simplicity again
    workflow.add_edge("simplify_plan", "check_simplicity")
    
    # End after a conversational response
    workflow.add_edge("conversational_response", END)

    # --- Compile the Graph ---
    app = workflow.compile()
    print("Graph compiled successfully!")
    return app

def visualize_graph(graph_app):
    try:
        img_bytes = graph_app.get_graph().draw_mermaid_png()
        image = Image.open(io.BytesIO(img_bytes))
        image.show()
    except Exception as e:
        print(f"Error visualizing graph: {e}")
        print("Please ensure you have matplotlib, pygraphviz, and mermaid-cli installed.")

if __name__ == '__main__':
    app = build_graph()
    visualize_graph(app)
