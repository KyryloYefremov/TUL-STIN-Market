from flask import Flask, render_template, jsonify, request, redirect, url_for
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from DataController import DataController
from log_streamer import LogStreamer
from StockMarketController import StockMarketController


app = Flask(__name__)
market = DataController(news_url='')  # initialize the DataController with the URL of the news module
logger = LogStreamer()  # initialize the logger
stock_market_controller = StockMarketController()  # initialize the stock market controller
scheduler = BackgroundScheduler()  # initialize the scheduler
# create a job to update stock data at defined time intervals
scheduler.add_job(
    market.start_market,
    trigger=CronTrigger(hour='0, 6, 12, 18', minute='0'),
    id='update_stock_data',
    replace_existing=True,
)
scheduler.start()


# Global list to store favorite companies
favorites = []

# Example company data (for the sake of simplicity)
COMPANIES = [
    {"ticker": "AAPL", "name": "Apple Inc."},
    {"ticker": "GOOGL", "name": "Alphabet Inc. (Google)"},
    {"ticker": "AMZN", "name": "Amazon.com, Inc."},
    {"ticker": "MSFT", "name": "Microsoft Corporation"},
    {"ticker": "TSLA", "name": "Tesla, Inc."},
]


# Route for streaming logs
@app.route('/logs')
def logs():
    return logger.stream()


# Route for the home page
@app.route('/')
def home():
    return render_template('index.html', companies=COMPANIES, favorites=favorites)


@app.route('/start_app', methods=['POST'])
def start_app():
    """
    Start the application manually. Trigger the main pipeline.
    """
    # update_stock_data()
    logger.log("Application started manually")
    return redirect(url_for('home'))


# Route for search functionality
@app.route('/search_stock', methods=['GET'])
def search_stock():
    query = request.args.get('query', '')

    logger.log(f"Searching for stock: {query}")
    
    if query:
        query = query.lower()
        try:
            # Simulate search by filtering companies based on the query
            search_results = [company for company in COMPANIES if query.lower() in company['name'].lower()]
        except Exception as e:
            # if no query/bad query will be provided, return empty results -> will be displayed in the UI as "No results found."
            search_results = []   
        
    return jsonify(search_results)


# Route for adding a company to the favorites list
@app.route('/add_favorite_stock', methods=['POST'])
def add_favorite_stock():
    ticker = request.form.get('ticker')
    name = request.form.get('name')
    
    # Check if the company is already in the favorites list
    if all(fav['ticker'] != ticker for fav in favorites):
        favorites.append({'ticker': ticker, 'name': name})
        logger.log(f"Adding favorite stock: {ticker}")

    return redirect(url_for('home'))


# Route for removing a company from the favorites list
@app.route('/delete_favorite_stock', methods=['POST'])
def delete_favorite_stock():
    ticker = request.form.get('ticker')

    logger.log(f"Removing favorite stock: {ticker}")
    
    # Remove the company from the favorites list
    global favorites
    favorites = [fav for fav in favorites if fav['ticker'] != ticker]

    return redirect(url_for('home'))


# Endpoint to send the list of stocks 
@app.route('/liststock')
def send_liststock():
    """
    Send a list of filtered stocks to the endpoint as json.
    """
    logger.log("Endpoint /liststock was triggered")

    json_data = [
        {"name": "Microsoft", "date": None, "rating": None, "sale": None},
        {"name": "Google", "date": None, "rating": None, "sale": None},
        {"name": "OpenAI", "date": None, "rating": None, "sale": None},
    ]
    return jsonify(json_data)


# Endpoint to send the list of stocks with a recommendation to sell
@app.route('/salestock')
def add_recommendations():
    """ 
    Add a recommendation "to sell" to those items
    that have a higher rating than the user-defined value. 
    Send the updated json to the endpoint
    """
    logger.log("Endpoint /salestock was triggered")

    json_data = [
        {"name": "Microsoft", "date": None, "rating": None, "sale": 1},
        {"name": "Google", "date": None, "rating": None, "sale": 0},
        {"name": "OpenAI", "date": None, "rating": None, "sale": 0},
    ]
    return jsonify(json_data)


if __name__ == '__main__':
    app.run(debug=True)   # run the app