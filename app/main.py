from flask import Flask
from flask_caching import Cache

import requests
import json
from datetime import datetime, timedelta
from dateutil.parser import isoparse

config = {
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
}
app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)

STATUS_KEY="whistler_status"

def grab_status():
    res = requests.get("https://www.whistlerblackcomb.com/the-mountain/mountain-conditions/terrain-and-lift-status.aspx")
    text = res.text
    text = text.split('\n')
    text = [t for t in text if t.find('TerrainStatusFeed')>-1]
    text = text[-1]
    text = text[text.find('=')+1:-2]
    return json.loads(text)

def update_status():
    status = grab_status()
    cache.set(STATUS_KEY, status)
    return status

def grab_status_cached():
    status = cache.get(STATUS_KEY)
    if status is None or 'Date' not in status or status['Date'] is None:
        return update_status()
    
    date = status['Date']
    date = isoparse(date)
    now = datetime.now(date.tzinfo)
    delta = now - date
    if delta>timedelta(minutes=5):
        return update_status()
    
    return status

@app.route("/")
def whistler_status():
    return grab_status_cached()