# First, make sure you have the necessary library installed.
# You can install it using pip:
# pip install langchain-openai

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import os

# --- Configuration ---
# Replace these with your actual base URL and API key.
# The base URL should be the endpoint of your LLM server that supports the OpenAI protocol.
# The API key is required for authentication with the service.
BASE_URL = "https://ai.liara.ir/api/v1/68977890e6dcb068f229124b"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySUQiOiI2NjVmNWMxYzUzN2E5YmZiZTc3ZTk2ZDYiLCJ0eXBlIjoiYXV0aCIsImlhdCI6MTc1NDc1NzMyOH0.CeCfB-XhHjt7dKuhYxWLjTvsH9m0vUCMxsait_mNLKk"

# --- Main Logic ---
def run_llm_test():
    """
    Initializes a LangChain client and sends a test prompt to the LLM.
    """
    # Check if configuration is set
    if not BASE_URL or not API_KEY or "YOUR_" in BASE_URL or "YOUR_" in API_KEY:
        print("Error: Please update the BASE_URL and API_KEY variables with your actual credentials.")
        return

    print("Attempting to connect to the LLM...")

    try:
        # Initialize the ChatOpenAI client with the specified base URL and API key.
        # This setup is what allows LangChain to use the OpenAI protocol to communicate
        # with any compatible LLM server.
        llm = ChatOpenAI(
            openai_api_base=BASE_URL,
            openai_api_key=API_KEY,
            model="openai/gpt-5-nano",
        )

        # Create a simple test prompt.
        prompt = "Hello, user. I am a helpful AI assistant. What can I help you with today?"
        
        # Prepare the message in the format expected by the LLM.
        message = HumanMessage(content=prompt)

        # Send the message to the LLM and get a response.
        response = llm.invoke([message])

        # Print the response content.
        print("\n--- LLM Response ---")
        print(response.content)

        print("\nConnection successful!")

    except Exception as e:
        # Catch and print any errors that occur during the connection or invocation.
        print(f"\nAn error occurred: {e}")
        print("Please check your BASE_URL, API_KEY, and ensure the LLM server is running and accessible.")

if __name__ == "__main__":
    run_llm_test()