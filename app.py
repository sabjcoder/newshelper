# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import urllib
import json
import os

from eventregistry import *

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    print("Request:")
    print(json.dumps(req, indent=4))
    if req.get("result").get("action") == "yahooWeatherForecast":
        baseurl = "https://query.yahooapis.com/v1/public/yql?"
        yql_query = makeYqlQuery(req)
        if yql_query is None:
            return {}
        yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
        result = urlopen(yql_url).read()
        data = json.loads(result)
        res = makeWebhookResult(data)
    elif req.get("result").get("action") == "getNews":
        data = req
        res = makeWebhookResultForGetNews(data)
    elif req.get("result").get("action") == "getChemicalSymbol":
        data = req
        res = makeWebhookResultForGetChemicalSymbol(data)
    else:
        return {}
    return res

def makeWebhookResultForGetChemicalSymbol(data):
    element = data.get("result").get("parameters").get("elementname")
    chemicalSymbol = 'Unknown'
    if element == 'Carbon':
        chemicalSymbol = 'C'
    elif element == 'Hydrogen':
        chemicalSymbol = 'H'
    elif element == 'Nitrogen':
        chemicalSymbol = 'N'
    elif element == 'Oxygen':
        chemicalSymbol = 'O'
    speech = 'The chemial symbol of '+element+' is '+chemicalSymbol

    return {
        "speech": speech,
        "displayText": speech,
        "source": "webhookdata"
    }

def makeWebhookResultForGetNews(data):
    result = req.get("result")
    parameters = result.get("parameters")
    keyword = parameters.get("keyword")
   
    er = EventRegistry(apiKey = "c9a7f5dc-9fe5-4943-a89f-6486536c9e01")
    q = QueryArticles(keywords = keyword)
    q.setRequestedResult(RequestArticlesInfo(count = 1))
    response = er.execQuery(q)
    print(response)
    
    title = response['articles']['results'][0]['title']
    url = response['articles']['results'][0]['url']
    
    speech = "Here is an article based on " + keyword + " : <" + url + "|" + title + ">"
    
    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        "source": "webhookdata"
    }


def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None
    
    u = 'c'
    unt = parameter.get("unit")
    if unt == 'fahrenheit':
        u = 'f'
        
    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "') and u='"+c+"'"


def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
             ", the temperature is " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
