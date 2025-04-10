from flask import Flask, render_template, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from DataController import DataController

app = Flask(__name__)
market = DataController(news_url='')  # initialize the DataController with the URL of the news module

scheduler = BackgroundScheduler()  # initialize the scheduler
# create a job to update stock data at defined time intervals
scheduler.add_job(
    market.start_market,
    trigger=CronTrigger(hour='0, 6, 12, 18', minute='0'),
    id='update_stock_data',
    replace_existing=True,
)
scheduler.start()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/liststock')
def send_liststock():
    """
    Send a list of filtered stocks to the endpoint as json.
    """
    json_data = [
        {"name": "Microsoft", "date": None, "rating": None, "sale": None},
        {"name": "Google", "date": None, "rating": None, "sale": None},
        {"name": "OpenAI", "date": None, "rating": None, "sale": None},
    ]
    return jsonify(json_data)


@app.route('/salestock')
def add_recommendations():
    """ 
    Add a recommendation "to sell" to those items
    that have a higher rating than the user-defined value. 
    Send the updated json to the endpoint
    """
    json_data = [
        {"name": "Microsoft", "date": None, "rating": None, "sale": 1},
        {"name": "Google", "date": None, "rating": None, "sale": 0},
        {"name": "OpenAI", "date": None, "rating": None, "sale": 0},
    ]
    return jsonify(json_data)



if __name__ == '__main__':
    app.run(debug=True)   # run the app