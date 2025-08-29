from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

llm = ChatOpenAI(base_url="your_base_url_here", api_key="your_api_key_here")

prompt = PromptTemplate.from_template(
    """You are the Planner Agent. Your role is to design a logical, step-by-step strategic plan based on a provided factual research summary.
    Using this research: {research_input}, produce a step-by-step roadmap for the goal. 
    Ensure logical sequencing and clear dependencies.
    
    **Goals**:
    - Create a clear, executable plan.

    - Ensure all steps are logically ordered and build upon one another.

    - Translate the research into a series of actionable steps.

    **Tasks**:

    - Analyze the factual research summary provided.

    - Break down the user's original goal into a sequence of smaller, manageable steps.

    - Identify any dependencies between the steps.

    **Constraints**:

    - Do not introduce any new facts or information not present in the research summary.

    - Keep the plan concise and professional.

    - Ensure the steps are ordered correctly to achieve the desired outcome.

    **Input Format**:
    - A factual research summary provided by the Research Agent.

    **Output Format**:
    - A structured, numbered list of steps. Each step must include the following sub-headings:

    - Action to take: A clear, concise instruction.

    - Dependencies: List any steps that must be completed before this one (e.g., "Step 1"). If none, state "None."

    - Expected outcome: A brief description of what should be achieved after completing the step."""
)

chain = prompt | llm

@tool
def planner_tool(research_input: str) -> str:
    """Produces a step-by-step roadmap based on research input."""
    return chain.invoke({"research_input": research_input}).content