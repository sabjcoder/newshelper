#!/usr/bin/env python

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

    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeWebhookResult(req):
    result = req.get("result")
    parameters = result.get("parameters")
    keyword = parameters.get("keyword")
    
    er = EventRegistry(apiKey = "c9a7f5dc-9fe5-4943-a89f-6486536c9e01")
    q = QueryArticles(keywords = keyword)
    q.setRequestedResult(RequestArticlesInfo(count = 1))
    response = er.execQuery(q)
    print(response)
    
    title = response['articles']['results'][0]['title']
    
    speech = "Here is a headline for an article based on " + keyword + " : " + title
    
    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        #"data": {},
        # "contextOut": [],
        "source": "newshelper"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0') 



