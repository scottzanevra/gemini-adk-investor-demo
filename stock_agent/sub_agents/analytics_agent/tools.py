import yfinance as yf
import pandas as pd
from typing import Dict, Any, List



def get_historical_yahoo_finance(
    ticker: str,
    period: str = '1y', # Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    interval: str = '1d' # Valid intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
) -> Dict[str, Any]:
    """Fetches historical time series data for a specified stock ticker from Yahoo Finance.

    This tool leverages the Yahoo Finance API (via a library) to retrieve historical stock price and volume data over a defined period and at a specific frequency. It provides a structured dataset that can be used for various analyses, such as trend identification, charting, and backtesting.

    Args:
        ticker (str): The stock ticker symbol for which to retrieve historical data (e.g., "AAPL", "MSFT").
        period (str, optional): The time range for the historical data.
                      Valid options include: '1d' (1 day), '5d' (5 days), '1mo' (1 month), '3mo' (3 months),
                      '6mo' (6 months), '1y' (1 year), '2y' (2 years), '5y' (5 years), '10y' (10 years),
                      'ytd' (year-to-date), and 'max' (maximum available history). Defaults to '1y'.
        interval (str, optional): The frequency of the data points within the specified period.
                        Valid options include: '1m' (1 minute), '2m' (2 minutes), '5m' (5 minutes),
                        '15m' (15 minutes), '30m' (30 minutes), '60m' (60 minutes or 1 hour),
                        '90m' (90 minutes), '1h' (1 hour), '1d' (daily), '5d' (5 days), '1wk' (weekly),
                        '1mo' (monthly), and '3mo' (3 months). Defaults to '1d'.

    Returns:
        dict: A dictionary containing the status of the request and the historical data.
              On success, the dictionary includes:
                - "status": "success"
                - "ticker": The uppercase stock ticker symbol for which historical data was retrieved.
                - "period": The specified historical data period.
                - "interval": The specified data frequency interval.
                - "data": A list of dictionaries, where each dictionary represents a historical data point and typically includes fields like 'date_time', 'Open', 'High', 'Low', 'Close', and 'Volume'. The 'date_time' field is formatted as 'YYYY-MM-DD HH:MM:SS'.
              On failure, the dictionary includes:
                - "status": "error"
                - "error_message": A message detailing the reason for the failure, such as an invalid ticker, unsupported period or interval, or network issues.
    """
    try:
        # Create a Ticker object
        stock = yf.Ticker(ticker)

        # Get historical data using the period parameter
        # The history method returns a pandas DataFrame
        hist_data = stock.history(period=period, interval=interval)

        # Check if the DataFrame is empty
        if hist_data.empty:
            return {
                "status": "error",
                "error_message": f"No historical data found for ticker {ticker} with the specified period ({period}) and interval ({interval})."
            }



        # Convert the pandas DataFrame to a list of dictionaries for easier processing
        # The index (Date/Datetime) is included as a column
        historical_data_list = hist_data.reset_index().to_dict('records')

        # Rename the date column for consistency if needed (yfinance uses 'Date' or 'Datetime')
        # We'll check for both 'Date' and 'Datetime' and rename to 'date_time'
        for data_point in historical_data_list:
            if 'Date' in data_point:
                # Convert Timestamp to string for JSON serialization if needed later
                data_point['date_time'] = data_point.pop('Date').strftime('%Y-%m-%d %H:%M:%S') if isinstance(data_point['Date'], pd.Timestamp) else str(data_point['Date'])
            elif 'Datetime' in data_point:
                 # Convert Timestamp to string for JSON serialization if needed later
                 data_point['date_time'] = data_point.pop('Datetime').strftime('%Y-%m-%d %H:%M:%S') if isinstance(data_point['Datetime'], pd.Timestamp) else str(data_point['Datetime'])


        return {
            "status": "success",
            "ticker": ticker.upper(),
            "period": period,
            "interval": interval,
            "data": historical_data_list
        }

    except Exception as e:
        # Catch any exceptions during the process (e.g., network errors, invalid ticker)
        return {
            "status": "error",
            "error_message": f"Failed to retrieve historical data for {ticker} ({period}, {interval}): {str(e)}"
        }