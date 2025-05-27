from dotenv import load_dotenv
from google.adk.agents import Agent

# Load environment variables
from stock_agent.prompts import return_instructions_root
from stock_agent.sub_agents import analytics_agent
from stock_agent.tools import get_market_movers, get_stock_details, get_stock_news, get_earnings_call_news_highlights

load_dotenv()

# Create the agent
root_agent = Agent(
    name="stock_market_agent",
    model="gemini-2.0-flash",  # Or your preferred model
    global_instruction=(
        f"""
        You are an expert in the stock market using a Multi Agent System.
        """
    ),
    description=(
                """
                Your go-to expert for navigating the US stock market. 
                I provide real-time insights on top-performing and lagging stocks, 
                in-depth details on individual companies, the latest news affecting specific tickers, 
                and historical stock performance. Get a comprehensive understanding of market dynamics and 
                company specifics to inform your financial decisions.
                
                - make sure to use the analytics agent if the user asks question about plotting, creating charts, or any other data analytics question   
                """
    ),
    sub_agents=[analytics_agent],
    instruction=return_instructions_root(),
    tools=[get_market_movers, get_stock_details, get_stock_news, get_earnings_call_news_highlights],
)
