class ConfigManager:

    def __init__(self, config_file: str):
        """
        Initializes the ConfigManager with a configuration file.

        Args:
            config_file (str): Path to the configuration file.
        """
        config = self._load_config(config_file)
        self.TIINGO_API_KEY        = config.get("tiingo_api_key", "")
        self.RATING_THRESHOLD      = config.get("rating_threshold", 0)
        self.LISTSTOCK_ENDPOINT    = config.get("liststock_endpoint", "http://localhost:5000/liststock")
        self.SALESTOCK_ENDPOINT    = config.get("salestock_endpoint", "http://localhost:5000/salestock")
        self.FAVOURITE_STOCKS_PATH = config.get("favourite_stocks_path", "./data/favourite_stocks.txt")
        self.SCHEDULE              = config.get("schedule", "0, 6, 12, 18")
        self.NEWS_URL              = config.get("news_module_url", "")

    def _load_config(self, config_file: str):
        """
        Loads the configuration from a JSON file.

        Args:
            config_file (str): Path to the configuration file.

        Returns:
            dict: Configuration settings.
        """
        import json
        try:
            with open(config_file, 'r') as file:
                config = json.load(file)
            return config
        except FileNotFoundError:
            raise Exception(f"Configuration file {config_file} not found.")
        except json.JSONDecodeError:
            raise Exception(f"Error decoding JSON from the configuration file {config_file}.")