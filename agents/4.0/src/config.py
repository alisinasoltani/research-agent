import os

# LLM Model
LLM_MODEL = "gpt-4o"

# Temperatures
INTENT_CLASSIFIER_TEMP = 0.0
CONVERSATIONAL_RESPONDER_TEMP = 0.2
PLAN_INTENT_CLARIFIER_TEMP = 0.3
CLARIFIER_QUESTIONS_TEMP = 0.2
SAMPLER_TEMP = 0.8
RATER_TEMP = 0.2
SIMPLIFIER_TEMP = 0.2
FINAL_RESPONDER_TEMP = 0.2
TERMINATION_CHECK_TEMP = 0.2  # If using LLM for termination

# Max Iterations
MAX_TOT_ITERATIONS = 30

# API Keys (placeholders; load from env in production)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-key-here")
# Add other API keys if needed, e.g., for search tools
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY", "your-search-key-here")  # Placeholder for tools like DuckDuckGo or similar

# Other Constants
MAX_CLARIFYING_QUESTIONS = 7
TOOL_TIMEOUT_SECONDS = 5