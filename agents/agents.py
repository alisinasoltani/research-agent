# File: main.py
import os
import uuid
import json
import re
import time
import mysql.connector
from typing import List, Dict, TypedDict
from dotenv import load_dotenv
from openai import OpenAI, APIStatusError, RateLimitError
from pydantic.v1 import BaseModel, Field, ValidationError

# Load environment variables
load_dotenv()

# --- Configuration ---
base_url = os.getenv("BASE_URL")
api_key = os.getenv("API_KEY")
mysql_host = os.getenv("MYSQL_HOST")
mysql_user = os.getenv("MYSQL_USER")
mysql_password = ""
mysql_database = os.getenv("MYSQL_DATABASE")

if not all([base_url, api_key, mysql_host, mysql_user, mysql_database]):
    # print([liara_base_url, liara_api_key, mysql_host, mysql_user, mysql_password, mysql_database])
    raise ValueError("All database and API variables must be set in the .env file.")

client = OpenAI(
    base_url=base_url,
    api_key=api_key,
)

# --- Database Integration ---
def get_db_connection():
    """Establishes and returns a MySQL database connection."""
    try:
        connection = mysql.connector.connect(
            host=mysql_host,
            user=mysql_user,
            password=mysql_password,
            database=mysql_database
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

def create_conversations_table():
    """Creates the conversations table if it doesn't exist."""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    thread_id VARCHAR(255) PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    history JSON NOT NULL
                )
            """)
            connection.commit()
            print("Conversations table ensured.")
        except mysql.connector.Error as err:
            print(f"Error creating table: {err}")
        finally:
            cursor.close()
            connection.close()

def save_conversation(thread_id, user_id, history):
    """Saves or updates the conversation history for a given thread_id."""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT thread_id FROM conversations WHERE thread_id = %s", (thread_id,))
            exists = cursor.fetchone()
            history_json = json.dumps(history)

            if exists:
                cursor.execute(
                    "UPDATE conversations SET history = %s, last_updated = CURRENT_TIMESTAMP WHERE thread_id = %s",
                    (history_json, thread_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO conversations (thread_id, user_id, history) VALUES (%s, %s, %s)",
                    (thread_id, user_id, history_json)
                )
            connection.commit()
            print(f"Conversation {thread_id} saved successfully.")
        except mysql.connector.Error as err:
            print(f"Error saving conversation: {err}")
        finally:
            cursor.close()
            connection.close()

# --- State Definition ---
class GraphState(TypedDict):
    """
    Represents the state of our graph.
    """
    user_prompt: str
    thread_id: str
    initial_thoughts: str
    tasks: List[Dict[str, str]]
    agent_outputs: Dict[str, str]
    simplified_outputs: Dict[str, str]
    final_answer: str
    simplification_loop_count: int
    validation_scores: Dict[str, int]

# --- Agent Output Schema for Pydantic Validation ---
class ArchitectAgentOutput(BaseModel):
    """Output format for the Architect Agent."""
    thought: str = Field(description="The agent's reflective thoughts on the problem.")
    tasks: List[Dict[str, str]] = Field(description="A list of three tasks for the downstream agents.")


# --- Agent Functions (now simple Python functions) ---

def call_architect_agent(state: GraphState) -> GraphState:
    """
    The initial reasoning agent that plans the entire workflow.
    """
    print("--- 🏛️ Architect-Agent: Initializing reasoning and task delegation ---")
    messages = [
        {"role": "system", "content": """You are Eleanor, a highly skilled, Thoughtful, analytical and empathetic problem solver. Your task is to take a user prompt and perform a deep web search using your built-in search tool to gather all relevant information. 
        After searching, write your own detailed thoughts based on the search results and your opinion on how to solve this problem "step by step". 
        then break down the problem into three distinct tasks for three specialized agents. you should define these tasks so each agent can gather information and provide its own solutions "step by step". 
        Your final output must be a single, raw JSON object. Do not add any other text before or after the JSON. The JSON object must have two keys: "thought" and "tasks". The "tasks" key must contain a list of three dictionaries, each with "agent_name" and "task" keys.
        The three tasks should be as follows:
        1. A task for a highly factual agent (Temperature 0) called Isaac.
        2. A task for a creative-factual mix agent (Temperature 0.7) called Layla.
        3. A task for a highly creative and exploratory agent (Temperature 2) called Nova.
        """},
        {"role": "user", "content": state["user_prompt"]}
    ]
    completion = client.chat.completions.create(
        model="openai/gpt-5-nano",
        messages=messages,
        # tools=[{"type": "browser_search"}],
        temperature=0.1,
        # max_tokens=8192
    )
    raw_response = completion.choices[0].message.content
    print(f"Raw model response: {raw_response}")
    response_data = json.loads(raw_response)
    state["initial_thoughts"] = response_data["thought"]
    state["tasks"] = [
        {"agent_name": "Isaac", "task": response_data["tasks"][0]["task"]},
        {"agent_name": "Layla", "task": response_data["tasks"][1]["task"]},
        {"agent_name": "Nova", "task": response_data["tasks"][2]["task"]},
    ]
    print(f"--- 🏛️ Architect-Agent: Tasks created. Thoughts: {response_data['thought']}")
    
    return state


def call_task_agents(state: GraphState) -> GraphState:
    """
    Runs the three task-specific agents in sequence.
    """
    print("--- 🚀 Running Task-Specific Agents ---")
    agent_outputs = {}
    
    tasks = state["tasks"]

    # agent_temperatures = {
    #     "Isaac 🧐": 0.0,
    #     "Layla 🤔": 0.7,
    #     "Nova 💡": 2.0,
    # }
    agent_temperatures = {
        "Isaac": 0.0,
        "Layla": 0.7,
        "Nova": 2.0,
    }
    
    agent_system_prompts = {
        "Isaac": """You are Isaac — a meticulous, trustworthy research assistant.  
        Your role: To produce an evidence-backed report for the user based ONLY on **valid, verifiable, publicly available sources from the web**. You never guess, speculate, or provide unverified information.  
        You always **cite your sources** (URLs or proper references) clearly in a Sources section.  

        Follow this thinking process:
        1. Carefully read the sub-task provided to you.
        2. Use the provided web search results and/or context to extract only the most **reliable, relevant, and recent** facts.
        3. Ignore anything that is not directly backed by a credible source.
        4. Summarize the key points in clear, human-readable language.
        5. Present the information in a way that a curious reader with no background knowledge can understand.

        Tone:  
        - Calm, professional, and precise  
        - No unnecessary filler or fluff  
        - Trustworthiness is your top priority  

        Your output must be in JSON with keys:
        - "summary": A short, friendly paragraph summarizing your findings for a layperson.
        - "details": A longer section (2–5 paragraphs) with all key facts.
        - "sources": A list of source objects, each containing {"title": "...", "url": "..."}

        Never output anything outside of this JSON.
        """,
        "Layla": """You are Layla — a pragmatic but imaginative problem solver.  
        Your role: To take the given sub-task and create **realistic, implementable ideas** that combine solid reasoning with light creativity.  
        Your goal is to propose improvements or solutions that could plausibly be adopted in the next 2–5 years.  

        Follow this thinking process:
        1. Read the sub-task carefully and identify the underlying challenge.
        2. Look at current facts (from search results or provided context) to anchor your ideas in reality.
        3. Brainstorm a few possible approaches — aim for balance between feasibility and originality.
        4. Select the best 2–4 ideas and explain why they are realistic, what resources they require, and who might implement them.
        5. Highlight both benefits and potential challenges for each idea.

        Tone:  
        - Friendly, encouraging, and clear  
        - Practical yet slightly inspirational  
        - Speak as if giving advice to a motivated city planner, entrepreneur, or policy maker  

        Your output must be in JSON with keys:
        - "summary": A concise, friendly paragraph summarizing your best ideas.
        - "ideas": A list of objects, each {"idea": "Title", "description": "Explanation with reasoning", "benefits": [...], "challenges": [...]}

        Never output anything outside of this JSON.
        """,
        "Nova": """
        You are Nova — a visionary, daring thinker who thrives on imagining the unexpected.  
        Your role: To explore bold, unconventional, and futuristic ideas that push the boundaries of what is possible.  
        You do NOT have to be practical or limited by current technology — instead, focus on what could be possible in the next 10–50 years.

        Follow this thinking process:
        1. Read the sub-task carefully and imagine the world decades into the future.
        2. Let go of current constraints — think like a sci-fi inventor or a radical futurist.
        3. Brainstorm surprising, fun, and awe-inspiring possibilities.
        4. Describe each idea in vivid, human language that sparks curiosity and excitement.
        5. Do NOT include sources — your role is vision, not verification.

        Tone:  
        - Excited, bold, and inspiring  
        - Sometimes playful, but always imaginative  
        - Make the reader say “Wow, I never thought of that!”  

        Your output must be in JSON with keys:
        - "summary": A short, engaging overview of your most exciting ideas.
        - "ideas": A list of objects, each {"idea": "Title", "description": "A vivid, inspiring paragraph"}

        Never output anything outside of this JSON.
        """
    }

    for task_info in tasks:
        agent_name = task_info["agent_name"]
        print(task_info["agent_name"])
        task_prompt = task_info["task"]
        temperature = agent_temperatures.get(agent_name, 0.5)

        messages = [
            {"role": "system", "content": f"""
            {agent_system_prompts[task_info["agent_name"]]}
            Your task is: {task_prompt}"""},
            {"role": "user", "content": f"Based on the user prompt: '{state['user_prompt']}', and the initial thoughts: '{state['initial_thoughts']}', provide your response."}
        ]

        try:
            completion = client.chat.completions.create(
                model="openai/gpt-5-nano",
                messages=messages,
                temperature=temperature
            )
            response_text = completion.choices[0].message.content
            agent_outputs[agent_name] = response_text
            print(f"--- ✅ {agent_name} completed task. ---")
        except Exception as e:
            print(f"Error running agent {agent_name}: {e}")
            agent_outputs[agent_name] = "Error in execution."
    
    state["agent_outputs"] = agent_outputs
    return state

def call_simplifier_agent(state: GraphState) -> GraphState:
    """Simplifies the outputs from the task-specific agents that need revision."""
    print("--- 📝 Simplifier-Agent: Simplifying outputs ---")
    simplified_outputs_new = state.get("simplified_outputs", {}).copy()
    scores = state.get("validation_scores", {})
    
    # Iterate over the agent names to get their outputs
    agent_names = [task['agent_name'] for task in state.get("tasks", [])]
    
    for agent_name in agent_names:
        # On the first pass, simplify the raw agent outputs
        # On subsequent passes, only simplify if the validation score was low
        should_simplify = (state.get("simplification_loop_count", 0) == 0) or (scores.get(agent_name, 0) < 8)

        if should_simplify:
            output_text = state["agent_outputs"].get(agent_name, "")
            
            messages = [
                {"role": "system", "content": """You are the Simplifier Agent.
                Your goal: Rewrite the provided text so that it is easily understandable for a high school student.

                Instructions:
                - explain more and very clearly all jargon, technical terms, and complex words.   
                - Break down long or complex sentences into explanations and simpler statements.   
                - explain ambiguous concepts with clear explanations.   
                - Use everyday language without losing the original meaning.  
                - Keep the tone friendly but factual.  
                - add any new information or example if needed.

                Input Text:
                {input_text}
                Output:
                A rewritten version of the text that is clear, direct, and suitable for a high school reader."""},
                {"role": "user", "content": f"Simplify the following text:\n\n{output_text}"}
            ]
            
            try:
                completion = client.chat.completions.create(
                    model="openai/gpt-5-nano",
                    messages=messages,
                    temperature=0.3
                )
                simplified_text = completion.choices[0].message.content
                simplified_outputs_new[agent_name] = simplified_text
                print(f"--- 📝 Simplifier-Agent simplified output for {agent_name}. ---")
            except Exception as e:
                print(f"Error simplifying output for {agent_name}: {e}")
                simplified_outputs_new[agent_name] = "Error simplifying text."
    
    state["simplified_outputs"] = simplified_outputs_new
    return state



def call_validator_agent(state: GraphState) -> GraphState:
    """Validates the simplified outputs with a score."""
    print("--- 💯 Validator-Agent: Rating simplified outputs ---")
    scores = {}
    
    for agent_name, simplified_text in state["simplified_outputs"].items():
        messages = [
            {"role": "system", "content": """You are the Validator Agent.
            Your goal: Evaluate the clarity and simplicity of the provided text.

            Instructions:
            - Rate the text's clarity on a scale from 1 to 10.  
            - 1 means "very confusing, hard to understand".  
            - 10 means "perfectly clear and easy to understand".  
            - Consider sentence structure, vocabulary difficulty, and overall readability.  
            - Respond with a SINGLE numerical digit (1–10).  
            - Do not include any words, symbols, or explanations—only the number.

            Text to Evaluate:
            {input_text}
            Output:
            A single digit from 1 to 10 representing your clarity rating."""},
            {"role": "user", "content": f"Rate the following text:\n\n{simplified_text}"}
        ]
        
        try:
            completion = client.chat.completions.create(
                model="openai/gpt-5-nano",
                messages=messages,
                temperature=0.1
            )
            score_response = completion.choices[0].message.content
            score = int("".join(filter(str.isdigit, score_response)))
            scores[agent_name] = score
            print(f"--- 💯 Validator-Agent scored output for {agent_name} with a {score}. ---")
        except (ValueError, IndexError):
            print(f"Could not parse score for {agent_name}. Defaulting to 1.")
            scores[agent_name] = 1
        except Exception as e:
            print(f"Error calling validator agent for {agent_name}: {e}")
            scores[agent_name] = 1

    state["validation_scores"] = scores
    state["simplification_loop_count"] = state.get("simplification_loop_count", 0) + 1
    return state


def call_final_aggregator_agent(state: GraphState) -> GraphState:
    """Aggregates all results into a final answer."""
    print("--- 🎓 Final-Synthesizer: Aggregating all results ---")
    
    final_prompt = f"""User Prompt: {state['user_prompt']}

    Architect Agent's Initial Thoughts: {state['initial_thoughts']}

    Simplified Answers:
    1. Isaac 🧐: {state['simplified_outputs'].get('Isaac', '')}
    2. Layla 🤔: {state['simplified_outputs'].get('Layla', '')}
    3. Nova 💡: {state['simplified_outputs'].get('Nova', '')}
    """
    messages = [
        {"role": "system", "content": """You are the Final Aggregator Agent.
        Your goal: Synthesize multiple inputs into a single, comprehensive, and polished final answer.

        You will receive:
        1. The user's original prompt.
        2. The initial thoughts from the Architect Agent.
        3. Three simplified answers from downstream agents.

        Instructions:
        - Read all inputs carefully.
        - Merge them into one clear, logically organized, and complete response.  
        - Ensure the final answer directly and thoroughly addresses the original user prompt.  
        - The tone must be professional, informative, and easy to follow.  
        - Avoid redundancy—if multiple sources say the same thing, combine them into one statement.  
        - Ensure smooth flow between sections.

        Inputs:
        Original Prompt: {user_prompt}
        Architect Agent's Thoughts: {architect_thoughts}
        Simplified Answer 1: {simplified_1}
        Simplified Answer 2: {simplified_2}
        Simplified Answer 3: {simplified_3}
        Output:
        A polished, well-structured final answer that integrates all the above information into a cohesive whole."""},
        {"role": "user", "content": final_prompt}
    ]

    try:
        completion = client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=messages,
            temperature=0.5
        )
        final_answer = completion.choices[0].message.content
        state["final_answer"] = final_answer
        print("--- 🎓 Final-Synthesizer: Final answer generated. ---")
    except Exception as e:
        print(f"Error generating final answer: {e}")
        state["final_answer"] = "Error generating final answer."
    
    return state


def run_conversation(user_prompt: str, thread_id: str, user_id: str):
    """
    Runs the entire multi-agent conversation for a given prompt without LangGraph.
    """
    initial_state = GraphState(
        user_prompt=user_prompt,
        thread_id=thread_id,
        initial_thoughts="",
        tasks=[],
        agent_outputs={},
        simplified_outputs={},
        final_answer="",
        simplification_loop_count=0,
        validation_scores={}
    )

    current_state = call_architect_agent(initial_state)

    if not current_state["tasks"]:
        print("Architect agent failed to generate tasks. Aborting.")
        return

    current_state = call_task_agents(current_state)
    while True:
        current_state = call_simplifier_agent(current_state)
        current_state = call_validator_agent(current_state)

        scores = current_state.get("validation_scores", {})
        loop_count = current_state.get("simplification_loop_count", 0)

        if any(score < 8 for score in scores.values()) and loop_count < 3:
            print(f"--- 🔄 Simplification Loop: Score below 8, looping back. Loop count: {loop_count} ---")
            time.sleep(1)
        else:
            print("--- ✅ Simplification Loop: All scores are good or max loops reached. Proceeding. ---")
            break

    current_state = call_final_aggregator_agent(current_state)
    
    print("\n--- ✅ Final Answer ---")
    print(current_state["final_answer"])
    
    save_conversation(thread_id, user_id, current_state)


if __name__ == "__main__":
    create_conversations_table()
    print("Welcome to the Advanced Agentic System!")
    user_id = str(uuid.uuid4())
    print(f"Your User ID is: {user_id}")
    while True:
        prompt = input("\nEnter your prompt (or 'exit' to quit): ")
        if prompt.lower() == 'exit':
            break

        thread_id = str(uuid.uuid4())
        run_conversation(prompt, thread_id, user_id)
