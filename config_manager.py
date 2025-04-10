class ConfigManager:

    def __init__(self, config_file: str):
        """
        Initializes the ConfigManager with a configuration file.

        Args:
            config_file (str): Path to the configuration file.
        """
        config = self._load_config(config_file)
        self.TIINGO_API_KEY        = config.get("tiingo_api_key")
        self.RATING_THRESHOLD      = config.get("rating_threshold")
        self.RATING_MIN            = config.get("rating_min")
        self.RATING_MAX            = config.get("rating_max")
        self.LISTSTOCK_ENDPOINT    = config.get("liststock_endpoint")
        self.SALESTOCK_ENDPOINT    = config.get("salestock_endpoint")
        self.FAVOURITE_STOCKS_PATH = config.get("favourite_stocks_path")
        self.SCHEDULE              = config.get("schedule")
        self.NEWS_URL              = config.get("news_module_url")

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