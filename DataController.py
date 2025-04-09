import requests
import json
from datetime import datetime
from typing import Tuple
from StockMarketController import StockMarketController

class DataController:
    def __init__(self):
        """
        Initializes the DataController with paths to data files.
        Stock data is stored in 'data' folder as a stock_data.json file in the following format:
        [{"nazev": str,
          "datum": str,
          "rating": int}, ...].
        Favourite stocks are stored in 'data' folder as a favourite_stocks.txt file in the following format:
        name,ticker\n
        ...
        """
        self.stock_data_path = "./data/stock_data.json"
        self.favourite_stocks_path = "./data/favourite_stocks.txt"

    @staticmethod
    def filter_stocks(stocks: list[Tuple[str, str]]) -> list[str]:

        def filter_3_days(stock_prices: list[float]) -> bool:
            for i in range(1, len(stock_prices)):
                if stock_prices[i - 1] > stock_prices[i]:
                    return False
            return True

        def filter_5_days(stock_prices: list[float]) -> bool:
            declines = 0
            for i in range(1, len(stock_prices)):
                if stock_prices[i - 1] > stock_prices[i]:
                    declines += 1
            if declines > 1:
                return False
            return True

        stock_market = StockMarketController()
        filtered_stocks = []
        for stock in stocks:
            ticker = stock[1]
            prices = stock_market.get_recent_prices(ticker)
            if filter_3_days(prices[2:]) and filter_5_days(prices):
                filtered_stocks.append(ticker)
        return filtered_stocks

    def update_stock_data(self):

        favourite_stocks = self.get_favourite_stocks()
        filtered_stocks = self.filter_stocks(favourite_stocks)
        today = datetime.now().isoformat()
        filtered_stocks_data = [{"nazev": stock, "datum": today, "rating": None} for stock in filtered_stocks]


    def update_favourite_stocks(self, new_stock: Tuple[str, str]) -> 1:
        with open(self.favourite_stocks_path, "a") as file:
            file.write(f"{new_stock[0]},{new_stock[1]}\n")
        return 1

    def get_stock_data(self, ticker: str) -> 1:
        ...

    def get_favourite_stocks(self) -> list[Tuple[str, str]]:
        stocks = []
        with open(self.favourite_stocks_path, "r") as file:
            for line in file:
                line = line.rstrip().split(",")
                stocks.append((line[0], line[1]))
        return stocks

