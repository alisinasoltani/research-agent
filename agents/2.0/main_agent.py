import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from tools.planner import planner_tool
from tools.simplifier import simplifier_tool
from tools.definition import definition_tool
from tools.evaluator import evaluator_tool
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary
from sqlalchemy.orm import declarative_base, sessionmaker
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI

load_dotenv()

# MySQL Database Configuration
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = ""  # Replace with your MySQL password
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DB = os.getenv("MYSQL_DATABASE")
CONNECTION_STRING = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"

# SQLAlchemy setup
Base = declarative_base()

class MessageStore(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), nullable=False)
    message = Column(LargeBinary, nullable=False)
    type = Column(String(255), nullable=False)

engine = create_engine(CONNECTION_STRING)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Initialize LLM
llm = ChatOpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
    model="openai/gpt-5-nano",
    tools=[{"type": "browser_search"}],
)

# Define the system prompt template with explicit input variables
system_prompt = PromptTemplate(
    input_variables=[
        "personality_prompt",
        "tone_of_voice_prompt",
        "documents_and_attachments",
        "agent_scratchpad",  # REQUIRED for tool-calling agents
        "chat_history",
        "user_prompt",
        "output_structure"
    ],
    template="""
    {personality_prompt}
    {tone_of_voice_prompt}
    {documents_and_attachments}
    {agent_scratchpad}
    {chat_history}
    {user_prompt}
    {output_structure}
    """
)

# Personality and tone boilerplate
personality_prompt = """ou are the Main Agent, an expert AI orchestrator. Your role is to coordinate a team of specialized AI agents to generate high-quality, comprehensive, and accurate responses to user queries. Your primary goal is to ensure the user receives a well-structured and meticulously researched answer.

**Personality**
You are a meticulous, highly professional, and precise orchestrator. You do not generate creative content or opinions. Your focus is on orchestrating the workflow and ensuring the final output is of the highest quality.
**Core Workflow**:
You must analyze the user's prompt to determine the correct course of action. The following conditions are checked in order. Stop and execute the first one that applies.
1.  **Is the prompt a greeting, social nicety, or small talk?**
    * **Yes:** Respond directly with a professional greeting or conversational reply. Do not ask questions or call any tools. The process ends here.
2.  **Is the request ambiguous or incomplete?**
    * **Yes:** Ask a single, clarifying question to the user. Do not proceed until you have a complete and unambiguous request.
3.  **Is the request a simple, factual query that can be answered directly from your knowledge base?**
    * **Yes:** Answer the user's request directly. Do not call any tools.
4.  **Is the request a complex subject that requires external research and a multi-step plan?**
    * **Yes:** Initiate the full agentic workflow by first calling the **Research Agent**. Then, call the **Planner Agent**, **Simplifier Agent**, **Definition Agent**, and finally the **Evaluator Agent** in sequential order.
"""
tone_of_voice_prompt = "Professional, direct, and authoritative."
documents_and_attachments = ""
# output_structure = "Your final output should be a single, well-structured response that directly addresses the user's request using the information provided by the agentic workflow. The response must be clear, professional, and easy to read."
output_structure = "Your final output should be a single, well-structured response that matches your tone of voice."

# Tools
tools = [planner_tool, simplifier_tool, definition_tool, evaluator_tool]

# 3) Define the LLM node: bind tools at call time
def call_model(state: MessagesState):
    # state["messages"] is a list like [("system", "..."), ("user", "..."), ...]
    resp = llm.bind_tools(tools).invoke(state["messages"])
    return {"messages": [resp]}

# 4) Tool execution node (no llm arg here)
tool_node = ToolNode(tools)

# 5) Routing: if the LLM asked for a tool, go to tools; else end
def should_continue(state: MessagesState):
    last = state["messages"][-1]
    # LangChain message objects have .tool_calls; tuples don’t. Handle both.
    tool_calls = getattr(last, "tool_calls", None)
    if tool_calls:
        return "tools"
    return "end"

# 6) Build the graph
graph = StateGraph(MessagesState)
graph.add_node("agent", call_model)
graph.add_node("tools", tool_node)

graph.add_edge(START, "agent")
graph.add_conditional_edges(
    "agent", should_continue, {"tools": "tools", "end": END}
)
graph.add_edge("tools", "agent")

# 7) Attach memory
checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)

def get_memory(user_id: str, thread_id: str):
    """Retrieve or initialize persistent memory from MySQL database."""
    chat_history = SQLChatMessageHistory(
        session_id=f"{user_id}_{thread_id}",
        connection=engine,  # UPDATED: use `connection` instead of deprecated `connection_string`
        table_name="message_store"
    )
    return ConversationBufferMemory(
        chat_memory=chat_history,
        memory_key="chat_history",
        return_messages=True
    )

def run_main_agent(user_input: str, user_id: str, thread_id: str):
    # Build a dynamic system prompt from your components
    system_prompt = "\n".join([
        "You are a helpful AI assistant focused on building strategic workflows.",
        "Respond in a professional, clear, and concise manner.",
        "No documents or attachments provided.",
        "Structure your output with sections: Plan, Simplified Version, Glossary, Evaluation Report."
    ])

    # Persist memory per thread
    config = {"configurable": {"thread_id": f"{user_id}_{thread_id}"}}

    # Turn 1: ask clarifying questions
    clarifying_result = app.invoke(
        {"messages": [("system", system_prompt),
                      ("user", f"{user_input}")]},
        config=config
    )
    clarifying_text = clarifying_result["messages"][-1].content
    print("Clarifying Questions:", clarifying_text)

    # Simulate user clarification (replace with real input in production)
    clarified_input = input("User clarification: ")

    # Turn 2: process clarified input (memory is auto‑recalled)
    final_result = app.invoke(
        {"messages": [("user", clarified_input)]},
        config=config
    )
    response_text = final_result["messages"][-1].content

    # Your original branching logic
    if "simple factual" in response_text.lower():
        return response_text
    else:
        plan_output7 = planner_tool(response_text)
        simplified_output = simplifier_tool(plan_output)
        definitions_output = definition_tool(simplified_output)
        evaluation_output = evaluator_tool(plan_output)

        final_response = f"""
        Strategic Plan: {plan_output}
        Simplified Version: {simplified_output}
        Glossary of Technical Terms: {definitions_output}
        Evaluation Report: {evaluation_output}
        """
        return final_response


if __name__ == "__main__":
    user_query = "Hi!"
    user_id = "user123"
    thread_id = "thread456"
    print(run_main_agent(user_query, user_id, thread_id))
