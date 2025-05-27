import datetime
import os
import requests
import yfinance as yf
import pandas as pd
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")


def get_market_movers(limit: int = 10) -> Dict[str, Any]:
    """Identifies and lists the top performing (gainers) and underperforming (losers) stocks in the US market at the present time.

    This tool queries a financial data API to fetch a real-time snapshot of the US stock market's biggest movers. It then processes this data to provide lists of the top gainers and losers, each limited to a specified number of entries. The information includes the stock's ticker symbol, company name, current price, the amount of price change, and the percentage of price change.

    Args:
        limit (int, optional): The maximum number of top gainers and top losers to retrieve and display. Defaults to 10.

    Returns:
        dict: A dictionary containing the status of the request and the market movers data.
              On success, the dictionary includes:
                - "status": "success"
                - "report": A formatted string report summarizing the top gainers and losers.
                - "gainers": A list of dictionaries, where each dictionary contains details of a top gainer (symbol, name, price, change, change_percent, volume).
                - "losers": A list of dictionaries, where each dictionary contains details of a top loser (symbol, name, price, change, change_percent, volume).
                - "last_updated": A timestamp indicating when the market movers data was last updated.
              On failure, the dictionary includes:
                - "status": "error"
                - "error_message": A message describing the error encountered during the process.
    """
    try:
        # Call Alpha Vantage API for top gainers
        gainers_url = f"https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey={ALPHA_VANTAGE_API_KEY}"
        response = requests.get(gainers_url)

        if response.status_code != 200:
            return {
                "status": "error",
                "error_message": f"API request failed with status code {response.status_code}"
            }

        data = response.json()

        # Process top gainers
        gainers = []
        if "top_gainers" in data:
            for stock in data["top_gainers"][:limit]:
                gainers.append({
                    "symbol": stock.get("ticker", ""),
                    "name": stock.get("name", ""),
                    "price": float(stock.get("price", "0").replace("$", "")),
                    "change": float(stock.get("change_amount", "0").replace("$", "")),
                    "change_percent": float(stock.get("change_percentage", "0%").replace("%", "")),
                    "volume": int(stock.get("volume", "0").replace(",", ""))
                })

        # Process top losers
        losers = []
        if "top_losers" in data:
            for stock in data["top_losers"][:limit]:
                losers.append({
                    "symbol": stock.get("ticker", ""),
                    "name": stock.get("name", ""),
                    "price": float(stock.get("price", "0").replace("$", "")),
                    "change": float(stock.get("change_amount", "0").replace("$", "")),
                    "change_percent": float(stock.get("change_percentage", "0%").replace("%", "")),
                    "volume": int(stock.get("volume", "0").replace(",", ""))
                })

        # Format the response
        gainers_report = "Top Gainers:\n"
        for idx, stock in enumerate(gainers, 1):
            gainers_report += f"{idx}. {stock['symbol']} ({stock['name']}): +{stock['change_percent']}%, ${stock['price']}\n"

        losers_report = "\nTop Losers:\n"
        for idx, stock in enumerate(losers, 1):
            losers_report += f"{idx}. {stock['symbol']} ({stock['name']}): {stock['change_percent']}%, ${stock['price']}\n"

        full_report = gainers_report + losers_report

        return {
            "status": "success",
            "report": full_report,
            "gainers": gainers,
            "losers": losers,
            "last_updated": data.get("last_updated", "Unknown")
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to retrieve market movers: {str(e)}"
        }


def get_stock_details(symbol: str) -> Dict[str, Any]:
    """Fetches and formats comprehensive details for a given stock ticker symbol.

    This tool queries financial data APIs to retrieve real-time stock quotes
    and company overview information. It then compiles this information into
    a human-readable report, including price, daily change, sector, industry,
    market capitalization, key financial ratios, and more.

    Args:
        symbol (str): The stock ticker symbol (e.g., 'AAPL' for Apple, 'GOOGL' for Alphabet).

    Returns:
        dict: A dictionary containing the status of the request and the stock details.
              On success, the dictionary includes:
                - "status": "success"
                - "report": A detailed string report of the stock information.
                - "symbol": The stock ticker symbol.
                - "name": The name of the company.
                - "price": The current stock price.
                - "change": The change in stock price since the previous close.
                - "change_percent": The percentage change in stock price.
                - "sector": The industry sector the company belongs to.
                - "industry": The specific industry the company operates in.
                - "description": A brief description of the company.
              On failure, the dictionary includes:
                - "status": "error"
                - "error_message": A message describing the error.
    """
    try:
        # Get overview data
        overview_url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
        overview_response = requests.get(overview_url)

        if overview_response.status_code != 200:
            return {
                "status": "error",
                "error_message": f"API request failed with status code {overview_response.status_code}"
            }

        overview_data = overview_response.json()

        # Check if we got valid data
        if "Symbol" not in overview_data:
            return {
                "status": "error",
                "error_message": f"No data found for symbol {symbol}"
            }

        # Get quote data
        quote_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
        quote_response = requests.get(quote_url)

        if quote_response.status_code != 200:
            return {
                "status": "error",
                "error_message": f"API request failed with status code {quote_response.status_code}"
            }

        quote_data = quote_response.json().get("Global Quote", {})

        # Extract and format data
        price = float(quote_data.get("05. price", "0"))
        prev_close = float(quote_data.get("08. previous close", "0"))
        change = float(quote_data.get("09. change", "0"))
        change_percent = float(quote_data.get("10. change percent", "0%").replace("%", ""))

        # Format the report
        report = f"Stock Details for {symbol} ({overview_data.get('Name', symbol)}):\n"
        report += f"Price: ${price}\n"
        report += f"Change: {'+' if change >= 0 else ''}{change} ({'+' if change_percent >= 0 else ''}{change_percent}%)\n"
        report += f"Sector: {overview_data.get('Sector', 'Unknown')}\n"
        report += f"Industry: {overview_data.get('Industry', 'Unknown')}\n"
        report += f"Market Cap: ${float(overview_data.get('MarketCapitalization', '0')) / 1e9:.2f} billion\n"
        report += f"P/E Ratio: {overview_data.get('PERatio', 'N/A')}\n"
        report += f"Dividend Yield: {overview_data.get('DividendYield', 'N/A')}\n"
        report += f"52-week High: ${overview_data.get('52WeekHigh', 'N/A')}\n"
        report += f"52-week Low: ${overview_data.get('52WeekLow', 'N/A')}\n"
        report += f"Volume: {int(quote_data.get('06. volume', '0')):,}\n"

        return {
            "status": "success",
            "report": report,
            "symbol": symbol,
            "name": overview_data.get('Name', symbol),
            "price": price,
            "change": change,
            "change_percent": change_percent,
            "sector": overview_data.get('Sector', 'Unknown'),
            "industry": overview_data.get('Industry', 'Unknown'),
            "description": overview_data.get('Description', '')
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to retrieve stock details for {symbol}: {str(e)}"
        }


def get_stock_news(ticker: str, limit: int = 10, topics: list = [None]) -> Dict[str, Any]:
    """Retrieves and provides a list of recent news articles specifically related to a given stock ticker symbol, with optional filtering by topic.

    This tool interacts with a financial news API to fetch the latest news headlines and summaries for a particular company. It returns a structured list of articles, including their titles, URLs, sources, brief summaries, and publication times. Optionally, the results can be filtered by specific topics to narrow down the news retrieved. This allows for quick access to current information and sentiment surrounding a specific stock and specific areas of interest.

    Args:
        ticker (str): The stock ticker symbol for which to retrieve news (e.g., "AAPL", "GOOGL").
        limit (int, optional): The maximum number of most recent news articles to fetch and return. Defaults to 10.
        topics (list, optional): A comma-separated list of topics to filter the news articles (e.g., "technology,earnings")

        Below is the full list of supported topics:
        - Blockchain: blockchain
        - Earnings: earnings
        - IPO: ipo
        - Mergers & Acquisitions: mergers_and_acquisitions
        - Financial Markets: financial_markets
        - Economy - Fiscal Policy (e.g., tax reform, government spending): economy_fiscal
        - Economy - Monetary Policy (e.g., interest rates, inflation): economy_monetary
        - Economy - Macro/Overall: economy_macro
        - Energy & Transportation: energy_transportation
        - Finance: finance
        - Life Sciences: life_sciences
        - Manufacturing: manufacturing
        - Real Estate & Construction: real_estate
        - Retail & Wholesale: retail_wholesale
        - Technology: technology

    Returns:
        dict: A dictionary containing the status of the request and the retrieved news articles.
              On success, the dictionary includes:
                - "status": "success"
                - "ticker": The uppercase stock ticker symbol for which news was retrieved.
                - "articles": A list of dictionaries, where each dictionary represents a news article and contains the following keys:
                  - "title": The headline of the news article.
                  - "url": The URL to the full news article.
                  - "source": The source or publisher of the article.
                  - "summary": A brief summary or snippet of the article's content.
                  - "time_published": The timestamp indicating when the article was published.
              On failure, the dictionary includes:
                - "status": "error"
                - "error_message": A message detailing the reason for the failure (e.g., API error, network issue).
    """
    try:
        # Alpha Vantage API endpoint for news and sentiment
        # We filter by ticker to get news specifically for that company
        news_url = (
            f"https://www.alphavantage.co/query?"
            f"function=NEWS_SENTIMENT&"
            f"tickers={ticker.upper()}&" # Ensure ticker is uppercase as required by API
            f"limit={limit}&"
            f"apikey={ALPHA_VANTAGE_API_KEY}"
        )
        if topics:
            news_url += f"&topics={topics}"

        response = requests.get(news_url)

        # Check for successful API response
        if response.status_code != 200:
            return {
                "status": "error",
                "error_message": f"API request failed with status code {response.status_code}. Response: {response.text}"
            }

        data = response.json()

        # Alpha Vantage news data is typically in the 'feed' key
        news_articles = []
        # Check if 'feed' exists and is a list
        if "feed" in data and isinstance(data["feed"], list):
            for article in data["feed"]:
                # Extract relevant information, providing default empty strings if keys are missing
                news_articles.append({
                    "title": article.get("title", "No Title Available"),
                    "url": article.get("url", "#"),
                    "source": article.get("source", "Unknown Source"),
                    "summary": article.get("summary", "No summary available."),
                    "time_published": article.get("time_published", "Unknown Time")
                })

        return {
            "status": "success",
            "ticker": ticker.upper(),
            "articles": news_articles,
            "topics": topics,
            # "report": formatted_report # Uncomment if you want the formatted report
        }

    except requests.exceptions.RequestException as req_err:
        # Handle errors related to the HTTP request itself (e.g., network issues)
        return {
            "status": "error",
            "error_message": f"Request error fetching news for {ticker}: {str(req_err)}"
        }
    except Exception as e:
        # Handle any other unexpected errors during processing
        return {
            "status": "error",
            "error_message": f"Failed to retrieve news for {ticker}: {str(e)}"
        }


import requests
from typing import Dict, Any, List

# Assume ALPHA_VANTAGE_API_KEY is defined elsewhere in your environment
# from your existing agent setup.
# ALPHA_VANTAGE_API_KEY = "YOUR_ALPHA_VANTAGE_API_KEY"



def get_earnings_call_news_highlights(
    ticker: str, limit: int = 10
) -> Dict[str, Any]:
    """Retrieves recent news articles specifically related to a given stock ticker's earnings calls.

    This tool utilizes the Alpha Vantage News & Sentiment API to fetch news articles
    filtered by the 'earnings' topic for a specified stock. It provides headlines,
    URLs, sources, summaries, and publication times for these articles.
    While it does not return the full earnings call transcript or structured
    highlights from the transcript text itself, it offers relevant news coverage
    and summaries surrounding the company's earnings events.

    Args:
        ticker (str): The stock ticker symbol for which to retrieve earnings news (e.g., "AAPL", "GOOGL").
        limit (int, optional): The maximum number of most recent news articles about earnings calls to fetch and return. Defaults to 10.

    Returns:
        dict: A dictionary containing the status of the request and the retrieved news articles.
              On success, the dictionary includes:
                - "status": "success"
                - "ticker": The uppercase stock ticker symbol.
                - "articles": A list of dictionaries, where each dictionary represents a news article and contains the following keys:
                  - "title": The headline of the news article.
                  - "url": The URL to the full news article.
                  - "source": The source or publisher of the article.
                  - "summary": A brief summary or snippet of the article's content.
                  - "time_published": The timestamp indicating when the article was published.
                - "note": A note clarifying that this provides news *about* earnings, not the transcript text itself.
              On failure, the dictionary includes:
                - "status": "error"
                - "error_message": A message detailing the reason for the failure.
    """
    try:
        # Alpha Vantage API endpoint for news and sentiment
        # Filter by ticker and specifically by the 'earnings' topic
        news_url = (
            f"https://www.alphavantage.co/query?"
            f"function=NEWS_SENTIMENT&"
            f"tickers={ticker.upper()}&"  # Ensure ticker is uppercase
            f"topics=earnings&"  # Filter specifically for earnings news
            f"limit={limit}&"
            f"apikey={ALPHA_VANTAGE_API_KEY}"
        )

        response = requests.get(news_url)

        # Check for successful API response
        if response.status_code != 200:
            return {
                "status": "error",
                "ticker": ticker.upper(),
                "error_message": f"API request failed with status code {response.status_code}. Response: {response.text}"
            }

        data = response.json()

        # Alpha Vantage news data is typically in the 'feed' key
        news_articles = []
        # Check if 'feed' exists and is a list
        if "feed" in data and isinstance(data["feed"], list):
            for article in data["feed"]:
                # Extract relevant information, providing default empty strings if keys are missing
                news_articles.append({
                    "title": article.get("title", "No Title Available"),
                    "url": article.get("url", "#"),
                    "source": article.get("source", "Unknown Source"),
                    "summary": article.get("summary", "No summary available."),
                    "time_published": article.get("time_published", "Unknown Time")
                })

        return {
            "status": "success",
            "ticker": ticker.upper(),
            "articles": news_articles,
            "topic_filtered": "earnings", # Indicate the specific topic used
            "note": "Results show news articles related to earnings calls, not the full transcript text.",
        }

    except requests.exceptions.RequestException as req_err:
        # Handle errors related to the HTTP request itself (e.g., network issues)
        return {
            "status": "error",
            "ticker": ticker.upper(),
            "error_message": f"Request error fetching earnings news for {ticker}: {str(req_err)}"
        }
    except Exception as e:
        # Handle any other unexpected errors during processing
        return {
            "status": "error",
            "ticker": ticker.upper(),
            "error_message": f"Failed to retrieve earnings news for {ticker}: {str(e)}"
        }

# Example usage (requires setting ALPHA_VANTAGE_API_KEY):
# if __name__ == "__main__":
#     # Replace with your actual API key or ensure the variable is set
#     # ALPHA_VANTAGE_API_KEY = "YOUR_REAL_API_KEY"
#
#     # Example for Apple Inc.
#     aapl_earnings_news = get_earnings_call_news_highlights(ticker="AAPL", limit=5)
#     print(aapl_earnings_news)
#
#     # Example for a non-existent ticker or error case
#     # invalid_news = get_earnings_call_news_highlights(ticker="INVALIDTICKER123")
#     # print(invalid_news)


#
# def get_historical_yahoo_finance(
#     ticker: str,
#     period: str = '1y', # Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
#     interval: str = '1d' # Valid intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
# ) -> Dict[str, Any]:
#     """Fetches historical time series data for a specified stock ticker from Yahoo Finance.
#
#     This tool leverages the Yahoo Finance API (via a library) to retrieve historical stock price and volume data over a defined period and at a specific frequency. It provides a structured dataset that can be used for various analyses, such as trend identification, charting, and backtesting.
#
#     Args:
#         ticker (str): The stock ticker symbol for which to retrieve historical data (e.g., "AAPL", "MSFT").
#         period (str, optional): The time range for the historical data.
#                       Valid options include: '1d' (1 day), '5d' (5 days), '1mo' (1 month), '3mo' (3 months),
#                       '6mo' (6 months), '1y' (1 year), '2y' (2 years), '5y' (5 years), '10y' (10 years),
#                       'ytd' (year-to-date), and 'max' (maximum available history). Defaults to '1y'.
#         interval (str, optional): The frequency of the data points within the specified period.
#                         Valid options include: '1m' (1 minute), '2m' (2 minutes), '5m' (5 minutes),
#                         '15m' (15 minutes), '30m' (30 minutes), '60m' (60 minutes or 1 hour),
#                         '90m' (90 minutes), '1h' (1 hour), '1d' (daily), '5d' (5 days), '1wk' (weekly),
#                         '1mo' (monthly), and '3mo' (3 months). Defaults to '1d'.
#
#     Returns:
#         dict: A dictionary containing the status of the request and the historical data.
#               On success, the dictionary includes:
#                 - "status": "success"
#                 - "ticker": The uppercase stock ticker symbol for which historical data was retrieved.
#                 - "period": The specified historical data period.
#                 - "interval": The specified data frequency interval.
#                 - "data": A list of dictionaries, where each dictionary represents a historical data point and typically includes fields like 'date_time', 'Open', 'High', 'Low', 'Close', and 'Volume'. The 'date_time' field is formatted as 'YYYY-MM-DD HH:MM:SS'.
#               On failure, the dictionary includes:
#                 - "status": "error"
#                 - "error_message": A message detailing the reason for the failure, such as an invalid ticker, unsupported period or interval, or network issues.
#     """
#     try:
#         # Create a Ticker object
#         stock = yf.Ticker(ticker)
#
#         # Get historical data using the period parameter
#         # The history method returns a pandas DataFrame
#         hist_data = stock.history(period=period, interval=interval)
#
#         # Check if the DataFrame is empty
#         if hist_data.empty:
#             return {
#                 "status": "error",
#                 "error_message": f"No historical data found for ticker {ticker} with the specified period ({period}) and interval ({interval})."
#             }
#
#
#
#         # Convert the pandas DataFrame to a list of dictionaries for easier processing
#         # The index (Date/Datetime) is included as a column
#         historical_data_list = hist_data.reset_index().to_dict('records')
#
#         # Rename the date column for consistency if needed (yfinance uses 'Date' or 'Datetime')
#         # We'll check for both 'Date' and 'Datetime' and rename to 'date_time'
#         for data_point in historical_data_list:
#             if 'Date' in data_point:
#                 # Convert Timestamp to string for JSON serialization if needed later
#                 data_point['date_time'] = data_point.pop('Date').strftime('%Y-%m-%d %H:%M:%S') if isinstance(data_point['Date'], pd.Timestamp) else str(data_point['Date'])
#             elif 'Datetime' in data_point:
#                  # Convert Timestamp to string for JSON serialization if needed later
#                  data_point['date_time'] = data_point.pop('Datetime').strftime('%Y-%m-%d %H:%M:%S') if isinstance(data_point['Datetime'], pd.Timestamp) else str(data_point['Datetime'])
#
#
#         return {
#             "status": "success",
#             "ticker": ticker.upper(),
#             "period": period,
#             "interval": interval,
#             "data": historical_data_list
#         }
#
#     except Exception as e:
#         # Catch any exceptions during the process (e.g., network errors, invalid ticker)
#         return {
#             "status": "error",
#             "error_message": f"Failed to retrieve historical data for {ticker} ({period}, {interval}): {str(e)}"
#         }


# def get_and_plot_stock_data(
#     ticker: str,
#     period: str = '1y', # Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
#     interval: str = '1d' # Valid intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
# ):
#     """Retrieves historical time series data for a given stock ticker using Yahoo Finance
#        and plots the closing price.
#
#     Args:
#         ticker (str): The stock ticker symbol (e.g., "AAPL", "MSFT").
#         period (str): The duration of the historical data.
#                       Valid options: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'.
#                       Defaults to '1y'.
#         interval (str): The desired frequency of the data.
#                         Valid options: '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h',
#                         '1d' (daily), '5d', '1wk' (weekly), '1mo' (monthly), '3mo'.
#                         Defaults to '1d'.
#     """
#     try:
#         # Create a Ticker object
#         stock = yf.Ticker(ticker)
#
#         # Get historical data using the period parameter
#         hist_data = stock.history(period=period, interval=interval)
#
#         # Check if the DataFrame is empty
#         if hist_data.empty:
#             print(f"Error: No historical data found for ticker {ticker} with the specified period ({period}) and interval ({interval}).")
#             return
#
#         # Extract dates and closing prices
#         # The index of the DataFrame is the Date/Datetime
#         dates = hist_data.index
#         closing_prices = hist_data['Close'] # Use 'Close' as yfinance column name
#
#         # Create the plot
#         plt.figure(figsize=(12, 6)) # Set the figure size
#         plt.plot(dates, closing_prices, label=f'{ticker} Closing Price')
#
#         # Add title and labels
#         plt.title(f'{ticker} Stock Price History ({period}, {interval})')
#         plt.xlabel('Date')
#         plt.ylabel('Closing Price')
#
#         # Add a legend
#         plt.legend()
#
#         # Improve date formatting on the x-axis
#         plt.gcf().autofmt_xdate()
#
#         # Add grid for better readability
#         plt.grid(True)
#
#         # Show the plot
#         plt.show()
#
#     except Exception as e:
#         # Catch any exceptions during the process (e.g., network errors, invalid ticker)
#         print(f"Error: Failed to retrieve or plot historical data for {ticker}: {str(e)}")


#
#
# def plot_stock_data(historical_data: List[Dict[str, Any]], ticker: str, interval: str):
#     """Plots the closing price of historical stock data.
#
#     Args:
#         historical_data (List[Dict[str, Any]]): A list of dictionaries containing historical data points,
#                                                 as returned by get_historical_yahoo_finance.
#         ticker (str): The stock ticker symbol for the plot title.
#         interval (str): The data interval for the plot title.
#     """
#     if not historical_data:
#         print("No data to plot.")
#         return
#
#     # Extract dates and closing prices
#     # Convert 'date_time' strings back to datetime objects for proper plotting
#     dates = [datetime.datetime.strptime(dp['date_time'], '%Y-%m-%d %H:%M:%S') for dp in historical_data]
#     closing_prices = [dp['Close'] for dp in historical_data] # Use 'Close' as yfinance column name
#
#     # Create the plot
#     plt.figure(figsize=(12, 6)) # Set the figure size
#     plt.plot(dates, closing_prices, label=f'{ticker} Closing Price')
#
#     # Add title and labels
#     plt.title(f'{ticker} Stock Price History ({interval})')
#     plt.xlabel('Date')
#     plt.ylabel('Closing Price')
#
#     # Add a legend
#     plt.legend()
#
#     # Improve date formatting on the x-axis
#     plt.gcf().autofmt_xdate()
#
#     # Add grid for better readability
#     plt.grid(True)
#
#     # Show the plot
#     plt.show()


if __name__ == "__main__":
    ticker = 'GOOG'
    get_stock_details(ticker)