import pytest
import tempfile
import json
from config_manager import ConfigManager

def test_load_valid_config():
    config_data = {
        "tiingo_api_key": "test_key",
        "rating_threshold": 3,
        "rating_min": 1,
        "rating_max": 5,
        "liststock_endpoint": "/list",
        "salestock_endpoint": "/sale",
        "favourite_stocks_path": "favourites.txt",
        "schedule": "12",
        "news_module_url": "http://news.local"
    }

    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as tmp:
        json.dump(config_data, tmp)
        tmp.seek(0)
        config = ConfigManager(tmp.name)

    assert config.TIINGO_API_KEY == "test_key"
    assert config.RATING_THRESHOLD == 3
    assert config.RATING_MIN == 1
    assert config.RATING_MAX == 5
    assert config.LISTSTOCK_ENDPOINT == "/list"
    assert config.SALESTOCK_ENDPOINT == "/sale"
    assert config.FAVOURITE_STOCKS_PATH == "favourites.txt"
    assert config.SCHEDULE == "12"
    assert config.NEWS_URL == "http://news.local"

def test_missing_file():
    with pytest.raises(Exception, match="Configuration file"):
        ConfigManager("nonexistent.json")

def test_invalid_json():
    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as tmp:
        tmp.write("{invalid: true")
        tmp.seek(0)
        tmp.flush()

        with pytest.raises(Exception, match="Error decoding JSON"):
            ConfigManager(tmp.name)