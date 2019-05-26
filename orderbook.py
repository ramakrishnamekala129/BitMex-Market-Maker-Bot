#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 26 03:29:23 2019

@author: kylekoshiyama
"""
import requests
import sched, time
import bitmex
import json

#////////////////////////////////// API CONFIG /////////////////////////////////////////////
key = ''
secret = ''
client = bitmex.bitmex(test=False, api_key= key, api_secret= secret)
#////////////////////////////////// API CONFIG /////////////////////////////////////////////


def open_long(leverage, position_size, last_buy):
    
    margin = client.User.User_getMargin().result()[0] # Get the current account balance
    balance = margin['walletBalance'] * 0.00000001

    client.Position.Position_updateLeverage(symbol='XBTUSD', leverage=leverage) #sets leverage

    OrderQuantity = leverage * balance * position_size * last_buy
    client.Order.Order_new(symbol='XBTUSD', orderQty=OrderQuantity, side='Buy', ordType='Limit',price = last_buy).result()[0]
    return



s = sched.scheduler(time.time, time.sleep)
def order_book(sc):
   position = client.Position.Position_get(filter=json.dumps({'symbol': 'XBTUSD'})).result()[0][0]
   print(position['openOrderBuyQty']) #get current position info in respect to the order book 
   print(position['openOrderSellQty']) #get current position info in respect to the order book 
   s.enter(120, 1, order_book, (sc,)) #run every 2 min
   if position['openOrderBuyQty'] or position['openOrderSellQty'] != 0:
        r = requests.get('https://testnet.bitmex.com/api/v1/orderBook/L2?symbol=XBT&depth=1') #gets the current bid/ask spread
        data = r.json()
        print(data)
        buy = data[-1]['price']
        sell = data[0]['price']
        if position['openOrderBuyQty'] > 0: #checks if we are in the order book rn, attempting to go long
            client.Order.Order_cancelAll().result()
            open_long(8, 1, buy) #eight times leverage and 100% of the portfolio
            print('Adjust Buy')
        if position['openOrderSellQty'] > 0: #check if we currently have a sell order in order book 
            client.Order.Order_cancelAll().result() #cancels our old order 
            client.Order.Order_closePosition(symbol='XBTUSD',price=sell).result() #moves closer to the current bid/ask spread
            print('Adjust Sell') 
   return 
s.enter(120, 1, order_book, (s,))
s.run()