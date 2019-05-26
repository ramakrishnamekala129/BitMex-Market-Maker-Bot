#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 26 03:34:35 2019

@author: kylekoshiyama
"""

import requests
import sched, time
import bitmex
import json

#////////////////////////////////// API CONFIG /////////////////////////////////////////////
key = 'q_wsxuSt070HEBqj3U4BmCYc'
secret = 'd36CwjxWmoXGwMN0yTgHjUxElETvZ0Mxtwbw-9wuXYlI-lRT'
client = bitmex.bitmex(test=True, api_key= key, api_secret= secret)
#////////////////////////////////// API CONFIG /////////////////////////////////////////////

s = sched.scheduler(time.time, time.sleep)
def stop_loss(sc):
    entry = client.Position.Position_get(filter=json.dumps({'symbol': 'XBTUSD'})).result()[0][0]['avgEntryPrice']
    r = requests.get('https://testnet.bitmex.com/api/v1/orderBook/L2?symbol=XBT&depth=1') #gets the current bid/ask spread
    data = r.json()
    sell = data[0]['price']
    s.enter(180, 1, stop_loss, (sc,))
    if entry > 0:    #to avoid a divide by zero error
        if (sell - entry)/entry < -.001:
            client.Order.Order_closePosition(symbol='XBTUSD',price=sell).result()
       
    print('yeet')
    return    

s.enter(180, 1, stop_loss, (s,))
s.run()