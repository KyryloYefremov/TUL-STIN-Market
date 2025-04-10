import requests
from datetime import datetime, timedelta
from typing import Tuple


class StockMarketController:
    """
    A controller for retrieving stock market data using the Tiingo API.

    This class provides methods to:
    - Search for stock tickers by query.
    - Retrieve the closing prices of a stock for the last 5 trading days.
    """

    def __init__(self):
        """
        Initializes the StockMarketController with an API key from 'key_tiingo.txt'
        and sets up the necessary Tiingo API endpoints.

        Raises:
            Exception: If the API key is missing or invalid.
        """
        try:
            with open("key_tiingo.txt", "r") as file:
                key = file.read().strip()
                if not key:
                    raise ValueError("API key is missing. Please check 'key_tiingo.txt'.")
                self.api_key = key
        except FileNotFoundError:
            raise FileNotFoundError("The 'key_tiingo.txt' file was not found.")

        self.base_price_url = "https://api.tiingo.com/tiingo/daily/"
        self.base_search_url = "https://api.tiingo.com/tiingo/utilities/search?query="
        self.headers = {'Content-Type': 'application/json'}

    def search_ticker(self, query: str) -> list[Tuple[str, str]]:
        """
        Searches for stock tickers matching a given query.

        Args:
            query (str): The search term for the stock (e.g., "Tesla").

        Returns:
            list: A list of tuples of stock names and tickers matching the query.

        Raises:
            Exception: If the API request fails or returns an empty response.
        """
        query = query.strip().lower()
        request_url = f"{self.base_search_url}{query}&token={self.api_key}"
        response = requests.get(request_url, headers=self.headers)

        if response.status_code != 200:
            raise Exception(f"Tiingo API request failed: {response.text}")

        results = response.json()
        if not results:
            raise Exception("No tickers found for the given query.")

        return [(company["name"], company["ticker"]) for company in results]

    def get_recent_prices(self, ticker: str) -> list[float]:
        """
        Retrieves the closing prices of a stock for the last 5 trading days.

        Args:
            ticker (str): The stock ticker.

        Returns:
            list[tuple[datetime, float]]: A list of tuples, where each tuple contains:
                - A `datetime` object representing the date.
                - A `float` representing the closing price.

        Raises:
            Exception: If the API request fails or returns an empty response.
        """
        today = datetime.now().date()
        start_date = today - timedelta(days=14)  # Ensures we fetch at least 6 trading days
        start_date_str = start_date.strftime("%Y-%m-%d")

        request_url = (
            f"{self.base_price_url}{ticker}/prices?"
            f"startDate={start_date_str}&resampleFreq=daily"
            f"&columns=close&token={self.api_key}"
        )

        response = requests.get(request_url, headers=self.headers)
        if response.status_code != 200:
            raise Exception(f"Tiingo API request failed: {response.text}")

        price_data = response.json()[-6:]  # Extract last 6 trading days
        if not price_data:
            raise Exception("No price data found for the given ticker.")

        return [ float(entry["close"]) for entry in price_data ]


if __name__ == "__main__":
    # testing
    controller = StockMarketController()
    tickers = controller.search_ticker("microsoft")
    ticker = tickers[0][1]
    prices = controller.get_recent_prices(ticker)
    print(prices)

