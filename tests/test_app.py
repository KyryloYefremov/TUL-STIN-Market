import pytest
from unittest.mock import patch, MagicMock
from app import app as flask_app

@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client

@patch("app.module_market.get_favourite_stocks")
def test_home_page(mock_get_favourites, client):
    mock_get_favourites.return_value = [("Test Company", "TEST")]
    response = client.get("/")
    assert response.status_code == 200
    assert b"Test Company" in response.data

@patch("app.module_market.get_favourite_stocks", side_effect=FileNotFoundError)
def test_home_page_file_not_found(mock_get_favourites, client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"No results found" not in response.data  # Still renders

@patch("app.module_market.start_market")
def test_start_app_route(mock_start_market, client):
    response = client.post("/start_app")
    assert response.status_code == 302  # Should redirect

@patch("app.stock_market.search_ticker")
@patch("app.logger.log")
def test_search_stock_success(mock_log, mock_search_ticker, client):
    mock_search_ticker.return_value = [("Test Company", "TEST")]
    response = client.get("/search_stock?query=test")
    assert response.status_code == 200
    assert b"TEST" in response.data

@patch("app.stock_market.search_ticker", side_effect=Exception("API failure"))
@patch("app.logger.log")
def test_search_stock_failure(mock_log, mock_search_ticker, client):
    response = client.get("/search_stock?query=test")
    assert response.status_code == 200
    assert response.json == []

@patch("app.module_market.get_favourite_stocks", return_value=[])
@patch("app.module_market.update_favourite_stocks")
@patch("app.logger.log")
def test_add_favourite_stock(mock_log, mock_update_fav, mock_get_fav, client):
    response = client.post("/add_favourite_stock", data={"name": "Test", "ticker": "TST"})
    assert response.status_code == 302

@patch("app.module_market.remove_favourite_stocks")
@patch("app.logger.log")
def test_delete_favourite_stock(mock_log, mock_remove_fav, client):
    response = client.post("/delete_favourite_stock", data={"ticker": "TST"})
    assert response.status_code == 302

# @patch("app.module_market.second_step_market")
# @patch("app.logger.log")
# def test_receive_rating_post_success(mock_log, mock_second_step, client):
#     response = client.post("/rating", json={"name": "Test", "rating": 5, "date": 1234567890})
#     assert response.status_code == 200
#     assert response.json["status"] == "success"

def test_receive_rating_wrong_method(client):
    response = client.get("/rating")
    assert response.status_code == 405
