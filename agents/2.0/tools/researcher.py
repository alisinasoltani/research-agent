from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
# Assume a search retriever (e.g., Tavily or SearXNG); install and configure accordingly
from langchain_community.tools.tavily_search import TavilySearchResults  # Example; replace as needed

llm = ChatOpenAI(base_url="your_base_url_here", api_key="your_api_key_here")

search = TavilySearchResults()  # Or SearXNG integration

prompt = PromptTemplate.from_template(
    "Summarize factual findings from these search results in bullet points, tagging technical terms with [TECH: term]. Search results: {search_results}"
)

chain = prompt | llm

@tool
def research_tool(query: str) -> str:
    """Searches the internet and summarizes factual findings concisely."""
    search_results = search.run(query)
    summary = chain.invoke({"search_results": search_results}).content
    return summary