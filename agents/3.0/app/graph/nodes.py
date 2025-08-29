import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain.agents import AgentExecutor, create_tool_calling_agent
from dotenv import load_dotenv

from app.graph.state import GraphState
from app.tools.web_search import web_search
from pydantic import SecretStr

# Load environment variables
load_dotenv()

# Initialize the LLM
model = ChatOpenAI(
    base_url=os.environ["BASE_URL"],
    api_key=SecretStr(os.environ["API_KEY"]),
    model="openai/gpt-5-nano",
    temperature=0.0
)

# --- NODE 1: Classify Input ---
def classify_input(state: GraphState) -> dict:
    """
    Classifies the user's input as either a 'conversation' or a 'strategic_plan' request.
    
    Args:
        state: The current graph state.
        
    Returns:
        A dictionary with the classification.
    """
    print("---CLASSIFYING INPUT---")
    prompt = ChatPromptTemplate.from_template(
        """
        You are an expert at classifying user prompts. Your goal is to determine if the user is asking for a strategic plan or just having a casual conversation.
        The user's prompt is: {prompt}
        
        Return a JSON object with a single key "classification" which can be one of two values: 'strategic_plan' or 'conversation'.
        """
    )
    
    chain = prompt | model | JsonOutputParser()
    result = chain.invoke({"prompt": state["prompt"]})
    
    return {"classification": result["classification"]}

# --- NODE 2: Conversational Response ---
def conversational_response(state: GraphState) -> dict:
    """
    Generates a conversational response to the user.
    
    Args:
        state: The current graph state.
        
    Returns:
        A dictionary with the generated response.
    """
    print("---GENERATING CONVERSATIONAL RESPONSE---")
    prompt = ChatPromptTemplate.from_template("You are a friendly conversational AI. Respond to the user's message: {prompt}")
    
    chain = prompt | model | StrOutputParser()
    generation = chain.invoke({"prompt": state["prompt"]})
    
    return {"generation": generation}
    
# --- NODE 3: Check Clarity ---
def check_clarity(state: GraphState) -> dict:
    """
    Checks if the user's request for a strategic plan is clear enough to proceed.
    
    Args:
        state: The current graph state.
        
    Returns:
        A dictionary with the clarity rating.
    """
    print("---CHECKING CLARITY---")
    prompt = ChatPromptTemplate.from_template(
        """
        You are a precision analysis tool. Your task is to evaluate the user's request for a strategic plan based on the conversation history.
        Rate the clarity on a scale of 1 to 10, where 1 is extremely vague and 10 is perfectly clear.
        
        Conversation History:
        {conversation_history}
        
        Return a JSON object with a single key "clarification_rate" containing the integer rating.
        """
    )
    
    chain = prompt | model | JsonOutputParser()
    result = chain.invoke({"conversation_history": state["conversation_history"]})
    
    return {"clarification_rate": int(result["clarification_rate"])}

# --- NODE 4: Ask Clarifying Questions ---
def ask_clarifying_questions(state: GraphState) -> dict:
    """
    Asks the user clarifying questions to get more details about their request.
    
    Args:
        state: The current graph state.
        
    Returns:
        A dictionary with the generated questions.
    """
    print("---ASKING CLARIFYING QUESTIONS---")
    prompt = ChatPromptTemplate.from_template(
        """
        You are an expert strategist. The user's request is not clear enough. 
        Based on the conversation history, ask clarifying questions to understand their goals, scope, and constraints for the strategic plan they want.
        
        Conversation History:
        {conversation_history}
        """
    )
    
    chain = prompt | model | StrOutputParser()
    generation = chain.invoke({"conversation_history": state["conversation_history"]})
    
    return {"generation": generation}
    
# --- NODE 5: Strategic Planner ---
def strategic_planner(state: GraphState) -> dict:
    """
    Generates a step-by-step strategic plan using a tool-enabled agent.
    
    Args:
        state: The current graph state.
        
    Returns:
        A dictionary containing the generated plan.
    """
    print("---GENERATING STRATEGIC PLAN---")
    tools = [web_search]
    
    # Corrected to use ChatPromptTemplate for compatibility with tool-calling agents
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are an expert strategist. You have access to a `web_search` tool. Your goal is to create a clear, step-by-step strategic plan based on the user's request. If you need more information, use the web search tool. Generate a step-by-step plan that guarantees the user can achieve their goal."),
            ("human", "User Request & Conversation:\n{conversation_history}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )
    
    agent = create_tool_calling_agent(model, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    result = agent_executor.invoke({"conversation_history": state["conversation_history"]})
    
    return {"plan": result["output"]}

# --- NODE 6: Check Simplicity ---
def check_simplicity(state: GraphState) -> dict:
    """
    Evaluates the generated plan for simplicity and jargon.
    
    Args:
        state: The current graph state.
        
    Returns:
        A dictionary with the simplicity rating.
    """
    print("---CHECKING SIMPLICITY---")
    prompt = ChatPromptTemplate.from_template(
        """
        You are a quality assurance tool for text simplification. Your task is to evaluate a strategic plan to see if it's simple enough for a high-school-level audience.
        Does the plan use any professional terminology or advanced concepts? If so, are they defined properly?
        Rate the plan's simplicity on a scale of 1 to 10, where 1 is full of undefined jargon and 10 is perfectly simple and clear.

        Plan to Analyze:
        {plan}
        
        Return a JSON object with a single key "simplicity_rate" containing the integer rating.
        """
    )
    
    chain = prompt | model | JsonOutputParser()
    result = chain.invoke({"plan": state["plan"]})
    
    return {"simplicity_rate": int(result["simplicity_rate"])}

# --- NODE 7: Simplify Plan ---
def simplify_plan(state: GraphState) -> dict:
    """
    Simplifies the plan by defining jargon and clarifying complex steps.
    
    Args:
        state: The current graph state.
        
    Returns:
        A dictionary with the simplified plan.
    """
    print("---SIMPLIFYING PLAN---")
    prompt = ChatPromptTemplate.from_template(
        """
        You are an expert editor. Your task is to simplify the following strategic plan.
        Your guiding principles are:
        1.  Do not change the plan's structure or the meaning of the steps.
        2.  Identify any advanced concepts or professional terminology.
        3.  Add definitions in parentheses right after any such term is used. don't limit yourself with explainin. explain everything needed for this plan.
        4.  Rewrite sentences to be clearer and more direct.

        The goal is to make the plan understandable to someone with no prior expertise in the subject.

        Original Plan:
        {plan}

        Simplified Plan:
        """
    )
    
    chain = prompt | model | StrOutputParser()
    simplified_plan = chain.invoke({"plan": state["plan"]})
    
    return {"plan": simplified_plan}