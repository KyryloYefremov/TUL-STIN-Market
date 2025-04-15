import pytest
from unittest.mock import MagicMock, patch, mock_open
from DataController import DataController

@pytest.fixture
def mock_dependencies():
    stock_market = MagicMock()
    stock_market.get_recent_prices.return_value = [100, 101, 102, 103, 104]
    logger = MagicMock()
    config = MagicMock()
    config.RATING_THRESHOLD = 3
    config.RATING_MIN = 1
    config.RATING_MAX = 5
    config.NEWS_URL = "http://news.local"
    config.LISTSTOCK_ENDPOINT = "/list"
    config.SALESTOCK_ENDPOINT = "/sale"
    config.FAVOURITE_STOCKS_PATH = "mock_favourites.txt"
    return stock_market, logger, config

def test_update_and_get_favourites(mock_dependencies):
    stock_market, logger, config = mock_dependencies
    controller = DataController(stock_market, logger, config)

    with patch("builtins.open", mock_open(read_data="Test,TEST\n")) as m:
        favourites = controller.get_favourite_stocks()
        assert favourites == [("Test", "TEST")]

    with patch("builtins.open", mock_open()) as m:
        controller.update_favourite_stocks(("NewCorp", "NEW"))
        m().write.assert_called_with("NewCorp,NEW\n")

def test_remove_favourite_stock(mock_dependencies):
    stock_market, logger, config = mock_dependencies
    controller = DataController(stock_market, logger, config)

    mock_data = "Apple,AAPL\nTesla,TSLA\n"
    with patch("builtins.open", mock_open(read_data=mock_data)) as m:
        controller.remove_favourite_stocks("TSLA")
        m().write.assert_called_once_with("Apple,AAPL\n")

def test_filter_stocks_applies_all_filters(mock_dependencies):
    stock_market, logger, config = mock_dependencies
    controller = DataController(stock_market, logger, config)
    stocks = [("Test", "TST")]

    filtered = controller.filter_stocks(stocks)
    assert filtered == ["TST"]

def test_pack_stock_data(mock_dependencies):
    stock_market, logger, config = mock_dependencies
    controller = DataController(stock_market, logger, config)
    result = controller.pack_stock_data(["TST"])
    assert isinstance(result, list)
    assert result[0]["name"] == "TST"
    assert "date" in result[0]

def test_validate_stocks(mock_dependencies):
    stock_market, logger, config = mock_dependencies
    controller = DataController(stock_market, logger, config)

    stock_data = [{"name": "Test", "date": 1234567890, "rating": 3}]
    result = controller.validate_stocks(stock_data)
    assert result == stock_data

def test_validate_stocks_errors(mock_dependencies):
    stock_market, logger, config = mock_dependencies
    controller = DataController(stock_market, logger, config)

    with pytest.raises(ValueError):
        controller.validate_stocks([])

    with pytest.raises(TypeError):
        controller.validate_stocks([123])

    with pytest.raises(ValueError):
        controller.validate_stocks([{"name": "X", "date": 0, "rating": 999}])

def test_add_recommendations(mock_dependencies):
    stock_market, logger, config = mock_dependencies
    controller = DataController(stock_market, logger, config)
    controller.stocks = [{"name": "Test", "rating": 4}]
    controller.add_recommendations()
    assert controller.stocks[0]["sale"] == 1