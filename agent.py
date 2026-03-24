import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from models import CricketReport

def get_cricket_agent():
    # Primary model is 2.5 Flash for GA stability
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.1
    )
    
    search = TavilySearchResults(
        tavily_api_key=os.getenv("TAVILY_API_KEY"),
        include_domains=["espncricinfo.com", "cricbuzz.com"],
        max_results=3
    )
    
    return create_agent(
        model=llm,
        tools=[search],
        response_format=CricketReport,
        system_prompt="You are a professional cricket analyst. Provide structured stats."
    )