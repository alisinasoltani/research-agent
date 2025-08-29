from typing import TypedDict, List, Dict, Optional

# The state object that will be passed around the LangGraph
class GraphState(TypedDict):
    """
    Represents the state of our graph.
    Each key is an attribute of the state.
    """
    user_prompt: str
    thread_id: str
    initial_thoughts: str
    tasks: List[Dict[str, str]]
    agent_outputs: Dict[str, str]
    simplified_outputs: Dict[str, str]
    final_answer: str
    simplification_loop_count: int
