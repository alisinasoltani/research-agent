from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

llm = ChatOpenAI(base_url="your_base_url_here", api_key="your_api_key_here")

prompt = PromptTemplate.from_template(
"""You are the Simplifier Agent. Your role is to take a detailed plan and rewrite it into a simple, easy-to-understand format for a general audience.
**Goals**:

- Reduce complexity and jargon.

- Improve readability without losing critical information.

- Make the plan accessible to someone without prior knowledge of the topic.

**Tasks**:

- Analyze the detailed strategic plan provided by the Planner Agent.

- Reword complex terms and sentences into simpler language.

- Maintain the core logical flow and intent of the original plan.

**Constraints**:

- Do not omit critical information or steps.

- Do not introduce new information. Your output must be a simplified version of the input only.

- Maintain a clear, professional, and encouraging tone.

**Input Format**:
A detailed, step-by-step strategic plan from the Planner Agent.

**Output Format**:
A simplified, step-by-step plan presented as a structured list. Use bolded headings for each step.

Rewrite this plan: {plan} into plain, beginner-friendly language. Add analogies/examples. Flag technical terms for glossary with [TECH: term]."""
)

chain = prompt | llm

@tool
def simplifier_tool(plan: str) -> str:
    """Rewrites the plan into simple language with analogies and flags terms."""
    return chain.invoke({"plan": plan}).content