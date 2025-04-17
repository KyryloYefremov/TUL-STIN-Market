import requests
from datetime import datetime
import time
from typing import Tuple
import json

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
            Filter3Days(),
            Filter5Days(),
        ]
        # initialize stock market controller
        self.stock_market = stock_market
        self.logger = logger

        self.stocks = None


    def start_market(self, mode="by scheduler"):
        """
        Function to start our market - update stock data. This function will be called by the scheduler or manually from UI.
        The function will trigger the pipeline:
        1. Get favourite stocks from the user file.
        2. Filter the stocks by the defined filters based on price from API.
        3. Send filtered stocks to module "News" to get ratings for requested companies stocks based on their latest news.
        """
        self.stocks = None  # reset stocks data
        try:
            self.logger.log(f"Market started {mode}")

            favourite_stocks = self.get_favourite_stocks()
            self.logger.log(f"Received {len(favourite_stocks)} favourite stocks", optional_data=favourite_stocks)

            filtered_stocks = self.filter_stocks(favourite_stocks)
            self.logger.log(f"Filtered stocks: {len(filtered_stocks)}", optional_data=filtered_stocks)

            if len(filtered_stocks) == 0:
                self.logger.log(f"No stocks to process")
                return

            json_data = self.pack_stock_data(filtered_stocks)  # pack stock data to json

            # self.logger.log(f"Sending stocks to News: {self.liststock_endpoint}", optional_data=json_data)
            self.send_to_news_module(self.liststock_endpoint, json_data)
            
            self.wait_for_news_response()  # wait for the response from News module
        except Exception as e:
            self.logger.log(f"Market failed")
            self.logger.log(f"Error: {e}")

    def second_step_market(self, data: dict):
        """
        Second part of the market pipeline where 3 final steps are completed:
        4. Validate received data from News module
        5. Based on the ratings, add a recommendation to the user favourite stocks either to sell, or keep them.
        6. Send the updated stock data to the module "News" in order to sell it or buy.

        @param data: dict, stocks data received from the News module

        """
        try:
            valid_data = self.validate_stocks(data)
            self.logger.log(f"After validation stocks: {valid_data}")

            # save the received valid data to DataController
            self.stocks = valid_data
            self.logger.log(f"Adding recommendations to stocks", optional_data=self.stocks)
            self.add_recommendations()

            # self.logger.log(f"Sending stocks to News: {self.salestock_endpoint}", optional_data=self.stocks)
            self.send_to_news_module(self.salestock_endpoint, self.stocks)

            self.logger.log(f"Market finished successfully")
        except Exception as e:
            self.logger.log(f"Market failed")
            self.logger.log(f"Error: {e}")



    def update_favourite_stocks(self, new_stock: Tuple[str, str]):
        """
        Triggers when the user adds a new stock to the favourite stocks.
        The function will add the new stock to the file.

        @param new_stock: tuple (name, ticker)
        """
        # check if the file exists, if not create it
        try:
            with open(self.favourite_stocks_path, "a") as file:
                file.write(f"{new_stock[0]},{new_stock[1]}\n")
        except FileNotFoundError:
            # create the file if it doesn't exist
            with open(self.favourite_stocks_path, "w") as file:
                file.write(f"{new_stock[0]},{new_stock[1]}\n")     
        except Exception as e:
            self.logger.log(f"Error updating favourite stocks: {e}")

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

            self.logger.log(f"Filtering stock: {ticker}", optional_data=prices)
            self.logger.log(f"Applied filters: {[ filter.__class__.__name__ for filter in self.filters]}")
            # apply filters
            # if all filter was satisfied, add the stock to the filtered list
            if all(filter.apply(prices) for filter in self.filters):
                filtered_stocks.append(ticker)
        return filtered_stocks
    
    def pack_stock_data(self, stocks: list[str]) -> list[dict]:
        """
        Packs the stock data into a JSON object.
        The JSON object contains the stock name, date.
        """
        date = int(datetime.now().timestamp())
        return [{"name": stock, "date": date, "rating": 0, "sale": 0} for stock in stocks]
    
    def send_to_news_module(self, endpoint: str, json_data: list[dict] = None):
        """
        Sends the filtered stocks to the module "News".
        The stocks data is sent as a JSON object.

        @param endpoint: `str` endpoint of the module "News"
        @param json_data: `list` of stocks data to be sent to the module "News"

        @raises: `ConnectionError` if the request fails.
        """
        self.logger.log(f"Sending data to the News module: {endpoint}", optional_data=json_data)
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(endpoint, json=json.dumps(json_data), headers=headers)
            # check if the response is successful
            # if response.status_code != 200:
            #     raise ConnectionError(f"Failed to send data to the News module. Status code: {response.status_code}. Response: {response.text}")
            # self.logger.log(f"Data sent to the News module successfully: {response.status_code}")
        except requests.RequestException as e:
            raise ConnectionError(f"An error occurred while sending data to the News module: {e}")
        

    def wait_for_news_response(self):
        """
        Waits for the response from the News module.
        The function will wait for 5 seconds before checking the response.

        @raises: `TimeoutError` if the response is not received within the timeout period.
        """
        timeout = 60  # seconds
        interval = 5
        elapsed = 0
        # wait for ratings callback (e.g., max 10 seconds, check every 0.5 sec)
        while elapsed < timeout:
            self.logger.log(f"Waiting for News response... stocks: {self.stocks}")
            # if the self.stocks was updated by the News module, break the loop
            if self.stocks is not None:
                self.logger.log(f"Received stocks rating from News", optional_data=self.stocks)
                return
            # else wait for the next check
            time.sleep(interval)
            elapsed += interval

        self.logger.log("Didn't receive the response from the News module in one minute.")
        # raise TimeoutError("Timeout waiting for the News module response.")
        

    def validate_stocks(self, stock_data: list[dict]) -> list[dict]:
        """
        Validates the stocks data received from the News module.
        It checks if the response JSON isn't empty and if the stocks have valid attributes.
        If some of the stocks have invalid attributes, skip it.
            @param stock_data: `dict` stocks data received from the News module

            @return: `list` of valid stocks

            @raises: `ValueError` if the response JSON is empty.
            @raises: `TypeError` if the stock data is not a list.
            @raises: `KeyError` if the stock data doesn't contain the required attributes.
            @raises: `ValueError` if the rating value is invalid.
            @raises: `ValueError` if the response JSON is empty after the validation.
        """
        valid_stocks = []
        # validation:
        # 1. check if response json isn't empty
        if not stock_data:
            raise ValueError("The response JSON is empty.")
        # 2. validate response json: if some of the stocks have invalid attributes, skip it
        for stock in stock_data:
            self.logger.log(f"Validating stock: {stock} and type: {type(stock)}")
            # check if the stock is a dictionary
            if not isinstance(stock, dict):
                raise TypeError("The stock data is not a dictionary.")
            # check if the stock has the required attributes
            if all(attr in stock for attr in ["name", "date", "rating"]):
                # check if the stock has a valid rating
                if isinstance(stock["rating"], int) and self.RATING_MIN <= stock["rating"] <= self.RATING_MAX:
                    valid_stocks.append(stock)
        
        # 3. check if the response JSON is empty after the validation
        if len(valid_stocks) == 0:
            raise ValueError("The response JSON is empty after the validation.")

        return valid_stocks

    def add_recommendations(self) -> dict:
        """
        Adds recommendations to the stocks data based on the ratings.
        If rating > self.RATING_THRESHOLD, add recommendation to sell.
        
        @raises: `ValueError` if the rating value is invalid.
        @raises: `KeyError` if the stock data doesn't contain the required attributes.
        """
        try:
            for stock in self.stocks:
                if self.RATING_MAX >= stock["rating"] > self.RATING_THRESHOLD:
                    stock["sale"] = 1
                elif self.RATING_MIN <= stock["rating"] <= self.RATING_THRESHOLD:
                    stock["sale"] = 0
                else:
                    raise ValueError("Invalid rating value.")
        except KeyError as e:
            raise KeyError(f"Missing required attribute `rating` in stock data: {e}")