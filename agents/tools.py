import json
from langchain_core.tools import tool
from database import save_conversation, get_conversation # Import real database functions

@tool
def database_tool(action: str, data: dict = {}) -> str:
    """
    A tool to interact with the MySQL database.
    
    Args:
        action (str): The desired action ('save' or 'retrieve').
        data (dict): A dictionary containing the necessary data for the action.
                     For 'save', it needs 'thread_id', 'user_id', and 'history'.
                     For 'retrieve', it needs 'thread_id'.
    
    Returns:
        str: A message indicating the result of the database action.
    """
    print(f"💾 Executing database action: {action}")
    try:
        if action == "save":
            # Call the real database function to save the conversation
            thread_id = data.get('thread_id')
            user_id = data.get('user_id')
            history = data.get('history')
            if thread_id and user_id and history:
                save_conversation(thread_id, user_id, history)
                return f"Successfully saved conversation for thread {thread_id}."
            else:
                return "Error: Missing required data for 'save' action."
        
        elif action == "retrieve":
            # Call the real database function to retrieve the conversation
            thread_id = data.get('thread_id')
            if thread_id:
                history = get_conversation(thread_id)
                if history:
                    return json.dumps(history) # Return the retrieved history as a JSON string
                else:
                    return f"No conversation found for thread {thread_id}."
            else:
                return "Error: Missing 'thread_id' for 'retrieve' action."
        
        else:
            return "Unknown database action. Action must be 'save' or 'retrieve'."

    except Exception as e:
        return f"An error occurred during the database operation: {e}"
