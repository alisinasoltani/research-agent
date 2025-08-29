from app.graph.state import GraphState

def route_after_classification(state: GraphState) -> str:
    """
    Determines the next step after the initial prompt classification.

    Args:
        state: The current graph state.

    Returns:
        A string representing the next node to execute.
    """
    print("---ROUTING AFTER CLASSIFICATION---")
    if state["classification"] == "conversation":
        return "conversational_response"
    else:
        return "check_clarity"

def route_after_clarity_check(state: GraphState) -> str:
    """
    Determines whether to ask clarifying questions or proceed to planning.

    Args:
        state: The current graph state.

    Returns:
        A string representing the next node to execute.
    """
    print("---ROUTING AFTER CLARITY CHECK---")
    clarification_rate = state.get("clarification_rate")
    if clarification_rate is None or clarification_rate < 8:
        print(f"Clarity rate ({clarification_rate}) is below threshold. Asking questions.")
        return "ask_clarifying_questions"
    else:
        print(f"Clarity rate ({clarification_rate}) is sufficient. Proceeding to planner.")
        return "strategic_planner"

def route_after_simplicity_check(state: GraphState) -> str:
    """
    Determines whether the plan needs simplification or is ready to be sent.

    Args:
        state: The current graph state.

    Returns:
        A string representing the next node to execute, or "__end__" to finish.
    """
    print("---ROUTING AFTER SIMPLICITY CHECK---")
    simplicity_rate = state.get("simplicity_rate")
    if simplicity_rate is None or simplicity_rate < 9:
        print(f"Simplicity rate ({simplicity_rate}) is below threshold. Simplifying.")
        return "simplify_plan"
    else:
        print(f"Simplicity rate ({simplicity_rate}) is sufficient. Ending.")
        return "__end__"
