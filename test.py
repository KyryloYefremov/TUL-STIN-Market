import pprint as pp
import requests

token = '8609c2c26a80e86d5152eca2870972168cec868f'
asset = 'AAPL'

headers = {
    'Content-Type': 'application/json'
}
requestResponse = requests.get(f"https://api.tiingo.com/tiingo/daily/{asset}?token={token}", headers=headers)
result = requestResponse.json()
pp.pprint(result)