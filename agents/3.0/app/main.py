import os
from dotenv import load_dotenv
from app.graph.builder import build_graph
from app.graph.state import GraphState
from langchain_core.messages import HumanMessage, AIMessage

# Load environment variables from .env file
load_dotenv()

def main():
    """
    The main function to run the strategic planner agent.
    """
    # Check for necessary API keys
    if not os.getenv("API_KEY") or not os.getenv("BASE_URL"):
        print("Error: API_KEY and BASE_URL must be set in the .env file.")
        return

    # Build the compiled graph
    app = build_graph()

    # Maintain conversation history
    conversation_history = []

    print("Strategic Planner Agent is ready. Type 'exit' to end the conversation.")
    print("-" * 50)

    while True:
        try:
            # Get user input from the command line
            user_input = input("You: ")

            if user_input.lower() == 'exit':
                print("Agent shutting down. Goodbye!")
                break

            # Append user message to history
            conversation_history.append(HumanMessage(content=user_input))

            # Prepare the input for the graph.
            # We construct a full GraphState object with type-compatible initial values.
            graph_input: GraphState = {
                "prompt": user_input,
                "conversation_history": conversation_history,
                "classification": "",
                "clarification_rate": 0,
                "plan": "",
                "simplicity_rate": 0,
                "generation": "",
            }

            # Invoke the graph
            final_state = app.invoke(graph_input)

            # The final response can be in 'generation' or 'plan'
            agent_response = final_state.get("generation") or final_state.get("plan")
            
            if agent_response:
                print(f"Agent: {agent_response}")
                # Append agent's response to history
                conversation_history.append(AIMessage(content=agent_response))
            else:
                print("Agent: I'm not sure how to respond to that.")


        except KeyboardInterrupt:
            print("\nAgent shutting down. Goodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break

if __name__ == "__main__":
    main()
