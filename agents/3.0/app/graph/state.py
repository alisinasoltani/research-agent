from typing import TypedDict, List, Optional
from langchain_core.messages import BaseMessage

class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        prompt: The initial user prompt.
        conversation_history: The history of the conversation for context.
        classification: The type of user prompt ('conversation' or 'strategic_plan').
        clarification_rate: A score (1-10) of how clear the user's request is.
        plan: The generated strategic plan, which may be refined through loops.
        simplicity_rate: A score (1-10) of how simple and jargon-free the plan is.
        generation: The final response to be shown to the user.
    """
    prompt: str
    conversation_history: List[BaseMessage]
    classification: str
    clarification_rate: Optional[int]
    plan: Optional[str]
    simplicity_rate: Optional[int]
    generation: str
