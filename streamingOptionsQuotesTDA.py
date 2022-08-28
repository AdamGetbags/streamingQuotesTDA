# -*- coding: utf-8 -*-
"""
Real Time Equity Option Streaming Data
@author: Adam Getbags
@author: https://github.com/alexgolec/tda-api
shout out to Part Time Larry!!!
"""

from tda.auth import easy_client
from tda import auth, client
from tda.client import Client
from tda.streaming import StreamClient
import time as t
import TDAsecrets

import asyncio
import json

#for asyncio use in jupyter/spyder/ipython envs
import nest_asyncio
nest_asyncio.apply()

#authentication for HTTP client
try:
    c = auth.client_from_token_file(TDAsecrets.token_path, TDAsecrets.api_key)
except FileNotFoundError:
    from selenium import webdriver
    with webdriver.Chrome() as driver:
        c = auth.client_from_login_flow(
            driver, TDAsecrets.api_key, TDAsecrets.redirect_uri,
            TDAsecrets.token_path)

#get call options
r = c.get_option_chain(symbol = 'AAPL',
                        contract_type = c.Options.ContractType.CALL)

# dictionary of contract specific data for CALLS
print(json.dumps(r.json()['callExpDateMap'][
# specific expiration
        list(r.json()['callExpDateMap'].keys())[0]][
# specific strike
        list(r.json()['callExpDateMap'][
        list(r.json()['callExpDateMap'].keys())[0]].keys())[62]][0], indent = 4))            
            
#creating queue class
class Queue:

    #intitializing queue as an empty list
    def __init__(self):
        self.queue = []

    #is the queue empty
    def isEmpty(self):
        return True if len(self.queue) == 0 else False

    #element at front of queue
    def front(self):
        return self.queue[-1]

    #element at back of queue
    def rear(self):
        return self.queue[0]

    #add to queue - specify queue length
    def enqueue(self, x):
        if len(self.queue) <= 14:
            self.x = x
            self.queue.insert(0, x) 
        else: 
            self.dequeue()
            self.x = x
            self.queue.insert(0, x) 
            
    #remove from queue
    def dequeue(self):
        self.queue.pop()

#data storage queue
testQueue = Queue()

#authentication for stream client
client = easy_client(
        api_key=TDAsecrets.api_key,
        redirect_uri=TDAsecrets.redirect_uri,
        token_path=TDAsecrets.token_path)
stream_client = StreamClient(client, account_id=TDAsecrets.accountID)

#to access streaming data
async def read_stream():
    await stream_client.login()
    await stream_client.quality_of_service(StreamClient.QOSLevel.EXPRESS)

    def print_message(message):
      print(json.dumps(message, indent=4))
      testQueue.enqueue((message))
      
    # Always add handlers before subscribing because many streams start sending
    # data immediately after success, and messages with no handlers are dropped.
    stream_client.add_level_one_option_handler(print_message)
    await stream_client.level_one_option_subs(["AAPL_061722C130"])

    while True:
        await stream_client.handle_message()
        
async def close_stream():
    await stream_client.level_one_option_unsubs(["AAPL_061722C130"])

asyncio.run(read_stream())
#asyncio.run(close_stream())

optionSpecs = testQueue.queue[0]['content'][0]
bidPrice = testQueue.queue[0]['content'][0]['BID_PRICE']
askPrice = testQueue.queue[0]['content'][0]['ASK_PRICE']
