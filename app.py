from flask import Flask, render_template, jsonify


app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/liststock')
def send_liststock():
    """
    Send a list of filterd stocks to the endpoint as json.
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
    that have a higher rainging than the user-defined value. 
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