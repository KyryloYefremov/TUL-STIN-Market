import requests
from datetime import datetime
from typing import Tuple

from StockMarketController import StockMarketController
from log_streamer import LogStreamer
from config_manager import ConfigManager
from filters import *


class DataController:
    def __init__(self, stock_market: StockMarketController, logger: LogStreamer, config_manager: ConfigManager):
        """
        Initializes the DataController with paths to data files.
        Stock data is stored in 'data' folder as a stock_data.json file in the following format:
            [
                {"name": str, "date": timestamp, "rating": int}, 
                ...
            ].
        Favourite stocks are stored in 'data' folder as a favourite_stocks.txt file in the following format:
            name,ticker\n
            ...
        """

        self.RATING_THRESHOLD = config_manager.RATING_THRESHOLD  # user-defined rating threshold for selling stocks
        self.RATING_MIN =  config_manager.RATING_MIN # minimum rating value
        self.RATING_MAX = config_manager.RATING_MAX  # maximum rating value

        # endpoints of module "News"
        self.news_url = config_manager.NEWS_URL
        self.liststock_endpoint = self.news_url + config_manager.LISTSTOCK_ENDPOINT
        self.salestock_endpoint = self.news_url + config_manager.SALESTOCK_ENDPOINT

        # paths to data files
        # self.stock_data_path = config_manager.STOCK_DATA_PATH
        self.favourite_stocks_path = config_manager.FAVOURITE_STOCKS_PATH

        # initialize filters
        self.filters = [
            # Filter3Days(),
            # Filter5Days(),
        ]
        # initialize stock market controller
        self.stock_market = stock_market
        self.logger = logger

        self.stocks = []


    def start_market(self, mode="scheduled"):
        """
        Function to start our market - update stock data. This function will be called by the scheduler or manually from UI.
        The function will trigger the pipeline:
        1. Get favourite stocks from the user file.
        2. Filter the stocks by the defined filters based on price from API.
        3. Send filtered stocks to module "News" to get ratings for requested companies stocks based on their latest news.
        4. Based on the ratings, add a recommendation to the user favourite stocks either to sell, or keep them.
        5. Send the updated stock data to the module "News" in order to sell it or buy.
        """
        try:
            self.logger.log(f"Market started {mode}")

            favourite_stocks = self.get_favourite_stocks()
            self.logger.log(f"Receiving favourite stocks: {len(favourite_stocks)}")

            filtered_stocks = self.filter_stocks(favourite_stocks)
            self.logger.log(f"Filtered stocks: {len(filtered_stocks)}")

            if len(filtered_stocks) == 0:
                self.logger.log(f"No stocks to process")
                return

            self.pack_stock_data(filtered_stocks)  # pack stock data to json self.stocks

            self.send_to_news_module(self.liststock_endpoint)
            self.logger.log(f"Sending stocks to News: {self.liststock_endpoint}")

            self.get_stocks_rating()  # stocks ratings are saved to self.stocks
            self.logger.log(f"Getting stocks rating from News")

            self.add_recommendations()
            self.logger.log(f"Adding recommendations to stocks")

            self.send_to_news_module(self.salestock_endpoint)
            self.logger.log(f"Sending stocks to News: {self.salestock_endpoint}")

            self.logger.log(f"Market finished successfully")
        except Exception as e:
            self.logger.log(f"Market failed.")
            self.logger.log(f"Error: {e}")

    def update_favourite_stocks(self, new_stock: Tuple[str, str]):
        """
        Triggers when the user adds a new stock to the favourite stocks.
        The function will add the new stock to the file.

        @param new_stock: tuple (name, ticker)
        """
        with open(self.favourite_stocks_path, "a") as file:
            file.write(f"{new_stock[0]},{new_stock[1]}\n")

    def remove_favourite_stocks(self, stock: str):
        """
        Triggers when the user removes a stock from the favourite stocks.
        The function will remove the stock from the file.

        @param stock: str name of the stock
        """
        with open(self.favourite_stocks_path, "r") as file:
            lines = file.readlines()
        with open(self.favourite_stocks_path, "w") as file:
            for line in lines:
                if line.strip("\n").split(',')[1] != stock:
                    file.write(line)

    def get_favourite_stocks(self) -> list[Tuple[str, str]]:
        """
        Reads the favourite stocks from the file and returns them as a list of tuples.
        Each tuple contains the name and ticker of the stock.

        @return: `list` of tuples (name, ticker)
        """
        stocks = []
        with open(self.favourite_stocks_path, "r") as file:
            for line in file:
                line = line.rstrip().split(",")
                stocks.append((line[0], line[1]))
        return stocks
    
    def filter_stocks(self, stocks: list[Tuple[str, str]]) -> list[str]:
        """
        Filters the stocks based on the defined filters.

        @param stocks: list of tuples (name, ticker)

        @return: list of filtered stock tickers
        """
        filtered_stocks = []

        # per favourite stock
        for stock in stocks:
            ticker = stock[1]  # get the ticker
            prices = self.stock_market.get_recent_prices(ticker)  # get the last 5 prices

            # apply filters
            # if all filter was satisfied, add the stock to the filtered list
            if all(filter.apply(prices) for filter in self.filters):
                filtered_stocks.append(ticker)
        return filtered_stocks
    
    def pack_stock_data(self, stocks: list[str]):
        """
        Packs the stock data into a JSON object.
        The JSON object contains the stock name, date, rating, and sale status.
        """
        date = datetime.now().timestamp()
        self.stocks = [{"name": stock, "date": date, "rating": 0, "sale": 0} for stock in stocks]
    
    def send_to_news_module(self, endpoint: str):
        """
        Sends the filtered stocks to the module "News".
        The stocks data is sent as a JSON object.

        @param endpoint: `str` endpoint of the module "News"

        @raises: `ConnectionError` if the request fails.
        """
        try:
            response = requests.post(endpoint, json=self.stocks, verify="cert.pem")
            response.raise_for_status()
            # return response.json()
        except requests.RequestException as e:
            raise ConnectionError(f"An error occurred while sending data to the News module: {e}")

    def get_stocks_rating(self) -> dict:
        """
        Sends a request to the rating endpoint to get ratings for the provided stocks data.
        Apply basic validation:
            1. Checks if endpoint didn't send an empty data file.
            2. Validates the response JSON: if some of the stocks have invalid attributes, skip it.

        @raises: `ConnectionError` if the request fails or the response status code is not 200.
        """
        try:
            response = requests.get(self.liststock_endpoint, json=self.stocks)
            valid_stocks = []

            if response.status_code == 200:
                response_stocks_data = response.json()
                # validation:
                # 1. check if response json isn't empty
                if not response_stocks_data:
                    raise ValueError("The response JSON is empty.")
                # 2. validate response json: if some of the stocks have invalid attributes, skip it
                for stock in response_stocks_data:
                    # TODO: add more complex validation
                    # validace vstupních dat
                    if all(attr in stock for attr in ["name", "date", "rating", "sale"]):
                        if isinstance(stock["rating"], int) and self.RATING_MIN <= stock["rating"] <= self.RATING_MAX:
                            valid_stocks.append(stock)

                # save the valid stocks to self.stocks
                self.stocks = valid_stocks
            
            else:
                raise ConnectionError(f"Failed to get stock ratings. Status code: {response.status_code}, Response: {response.text}")
        except requests.RequestException as e:
            raise ConnectionError(f"An error occurred while requesting stock ratings: {e}")
        

    def add_recommendations(self) -> dict:
        """
        Adds recommendations to the stocks data based on the ratings.
        If rating > self.RATING_THRESHOLD, add recommendation to sell.
        
        @raises: `ValueError` if the rating value is invalid.
        """
        for stock in self.stocks:
            if stock["rating"] > self.RATING_THRESHOLD:
                stock["sale"] = 1
            elif stock["rating"] <= self.RATING_THRESHOLD:
                stock["sale"] = 0
            else:
                raise ValueError("Invalid rating value.")