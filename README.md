# Forked from

https://github.com/RashRAJ/stockAIAgent


# US Stock Market Agent

A Python agent built with Google's Agent Development Kit (ADK) that provides real-time information about top performing stocks in the US market. This agent can retrieve current market movers (top gainers and losers) and provide detailed information about specific stocks.

## Features

- **Top Market Movers**: Get the current day's top gaining and losing stocks
- **Stock Details**: Retrieve comprehensive information about a specific stock
- **Easy Integration**: Built with Google's ADK for seamless integration with conversational AI systems
- **Clean API**: Well-documented functions with clear inputs and outputs

## Prerequisites

- Python 3.8 or higher
- An Alpha Vantage API key (free tier available)
- Google's Agent Development Kit (ADK)

## Installation

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate
   ```

2. Install the required packages:
   ```
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your Alpha Vantage API key:
   ```
   GOOGLE_GENAI_USE_VERTEXAI=1

   ALPHA_VANTAGE_API_KEY = <>>
   
   GOOGLE_CLOUD_PROJECT=<>>
   GOOGLE_CLOUD_LOCATION=us-central1
   ```
   You can get a free API key from [Alpha Vantage](https://www.alphavantage.co/support/#api-key).

### Running in ADK Web UI

```bash
# From the parent directory
adk web
```
### Example Queries

Once the agent is running, you can ask it questions like:

- "What are today's top market movers?"
- "Show me the biggest stock gainers and losers"
- "Tell me about AAPL stock"
- "What's the current price of Microsoft stock?"


## Deploy to Cloud Run:

```shell
export GOOGLE_CLOUD_PROJECT="<>"
export GOOGLE_CLOUD_LOCATION="australia-southeast1" # Example location
export AGENT_PATH="./stock_agent"
export SERVICE_NAME="adk-stock-agent"
export APP_NAME="adk-stock-agent"
```

```shell
adk deploy cloud_run \
--project=$GOOGLE_CLOUD_PROJECT \
--region=$GOOGLE_CLOUD_LOCATION \
--service_name=$SERVICE_NAME \
--app_name=$APP_NAME \
--with_ui $AGENT_PATH
```

