import pytest
import requests
from unittest.mock import patch, MagicMock
from StockMarketController import StockMarketController

@pytest.fixture
def controller():
    return StockMarketController(api_key="fake_api_key")

@patch("requests.get")
def test_search_ticker_success(mock_get, controller):
    mock_get.return_value = MagicMock(status_code=200)
    mock_get.return_value.json.return_value = [
        {"name": "Test Inc.", "ticker": "TST"}
    ]
    result = controller.search_ticker("test")
    assert result == [("Test Inc.", "TST")]

@patch("requests.get")
def test_search_ticker_failure(mock_get, controller):
    mock_get.return_value = MagicMock(status_code=500, text="Internal Server Error")
    with pytest.raises(Exception, match="Tiingo API request failed"):
        controller.search_ticker("test")

@patch("requests.get")
def test_get_recent_prices_success(mock_get, controller):
    mock_get.return_value = MagicMock(status_code=200)
    mock_get.return_value.json.return_value = [
        {"close": 100.0},
        {"close": 101.5},
        {"close": 99.3},
        {"close": 102.4},
        {"close": 104.0},
        {"close": 105.1}
    ]
    prices = controller.get_recent_prices("TST")
    assert prices == [100.0, 101.5, 99.3, 102.4, 104.0, 105.1]

@patch("requests.get")
def test_get_recent_prices_failure(mock_get, controller):
    mock_get.return_value = MagicMock(status_code=400, text="Bad Request")
    with pytest.raises(Exception, match="Tiingo API request failed"):
        controller.get_recent_prices("TST")