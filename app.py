from flask import Flask, render_template, jsonify, request, redirect, url_for
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import json

from DataController import DataController
from log_streamer import LogStreamer
from StockMarketController import StockMarketController
from config_manager import ConfigManager


app = Flask(__name__)  # initialize the Flask app
config_manager = ConfigManager(config_file='config.json')  # initialize the config manager
logger = LogStreamer()  # initialize the logger
stock_market = StockMarketController(api_key=config_manager.TIINGO_API_KEY)  # initialize the stock market controller
scheduler = BackgroundScheduler()  # initialize the scheduler

# initialize the DataController with the URL of the news module, the stock market controller, and the logger
module_market = DataController(
    stock_market=stock_market,
    logger=logger,    
    config_manager=config_manager,
)  
# create a job to update stock data at defined time intervals
scheduler.add_job(
    module_market.start_market,
    trigger=CronTrigger(hour=config_manager.SCHEDULE, minute='0'),
    id='start_market',
    replace_existing=True,
)
scheduler.start()


# Route for streaming logs
@app.route('/logs')
def logs():
    return logger.stream()


# Route for the home page
@app.route('/')
def home():
    try:
        favourites = module_market.get_favourite_stocks()
    except FileNotFoundError:
        favourites = []
    return render_template('index.html', favourites=favourites)


@app.route('/start_app', methods=['POST'])
def start_app():
    """
    Start the application manually. Trigger the main pipeline.
    """
    module_market.start_market(mode='manually')  # start the market
    return redirect(url_for('home'))


# Route for search functionality
@app.route('/search_stock', methods=['GET'])
def search_stock():
    query = request.args.get('query', '')

    logger.log(f"Searching for stock: {query}")
    
    if query:
        query = query.lower()
        try:
            # search for requested company using Stock Market
            search_results = stock_market.search_ticker(query)
        except Exception as e:
            # if no query/bad query will be provided, return empty results -> will be displayed in the UI as "No results found."
            search_results = []   
        
    return jsonify(search_results)


# Route for adding a company to the favourites list
@app.route('/add_favourite_stock', methods=['POST'])
def add_favourite_stock():
    ticker = request.form.get('ticker')
    name = request.form.get('name')

    try:
        favourites = module_market.get_favourite_stocks()
    except FileNotFoundError:
        favourites = []
    
    # Check if the company is already in the favourites list
    if all(fav[1] != ticker for fav in favourites):
        new_stock = (name, ticker)
        module_market.update_favourite_stocks(new_stock)  # add the company to the favourites list
        logger.log(f"Added favourite stock: {ticker}")

    return redirect(url_for('home'))


# Route for removing a company from the favourites list
@app.route('/delete_favourite_stock', methods=['POST'])
def delete_favourite_stock():
    ticker = request.form.get('ticker')

    logger.log(f"Removed favourite stock: {ticker}")
    
    # Remove the company from the favourites list
    module_market.remove_favourite_stocks(ticker)

    return redirect(url_for('home'))


@app.route('/rating', methods=['POST'])
def receive_rating():
    """
    The endpoint to receive ratings from the News module. 
    This endpoint saves received JSON to DataController attribute.
    """
    logger.log("Endpoint `/rating` was triggered")

    if request.method == 'POST':
        # get the JSON data from the request
        data = request.get_json()
        data = json.loads(data)
        logger.log(f"Received rating: {data}")

        # valid_data = module_market.validate_stocks(data)
        # logger.log(f"After validation stocks: {valid_data}")
        #
        # # save the received valid data to DataController
        # module_market.stocks = valid_data
        module_market.second_step_market(data)
    
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Invalid request method'}), 400
    
    
### TEST ROUTES FOR SIMULATING THE NEWS MODULE ###
@app.route('/liststock', methods=['GET', 'POST'])
def list_stocks():
    """
    Route for listing stocks.
    """
    # Assuming the request was successful, return a JSON response
    return jsonify({"message": "Stocks listed successfully."}), 200


@app.route('/salestock', methods=['GET', 'POST'])
def sale_stock():
    """
    Route for selling stocks.
    """
    # Assuming the request was successful, return a JSON response
    return jsonify({"message": "Stock sold successfully."}), 200
##################################################


if __name__ == '__main__':
    app.run()   # run the app