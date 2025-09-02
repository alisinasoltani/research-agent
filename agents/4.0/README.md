# Agentic Planning System

This project implements a LangGraph-based agentic system for interactive strategic planning. It uses a graph with nodes for intent classification, clarification, Tree-of-Thought planning, simplification, and response generation. The system handles conversational queries and detailed strategic plans, with checkpoints for threading and history.

## Setup Instructions

1. **Install dependencies** (requires Python 3.10+):
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

2. **Set up environment variables**:
   - Add your OpenAI API key: \`export OPENAI_API_KEY="your-key-here"\` (or use a .env file with python-dotenv if added later).

3. **Run tests** (once implemented):
   \`\`\`bash
   pytest
   \`\`\`

4. **Run the application** (entry point for testing the graph):
   \`\`\`bash
   python main.py
   \`\`\`

## Project Structure
- \`src/\`: Core source code, including nodes, subgraphs, tools, and the main graph.
- \`tests/\`: Unit and integration tests.
- \`main.py\`: Entry point for running the system.

For more details on the system specification, refer to the internal prompts and graph definitions in \`src/\`.