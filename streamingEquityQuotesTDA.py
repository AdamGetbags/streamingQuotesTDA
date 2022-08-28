# -*- coding: utf-8 -*-
"""
TD API Streaming Data
@author: https://github.com/alexgolec/tda-api
shout out to Part Time Larry!!!
"""

from tda.auth import easy_client
from tda.client import Client
from tda.streaming import StreamClient
import time as t
import secretsTDA

import asyncio
import json

#for asyncio use in jupyter/spyder/ipython envs
import nest_asyncio
nest_asyncio.apply()

#authentication for stream client
client = easy_client(
        api_key=secretsTDA.api_key,
        redirect_uri=secretsTDA.redirect_uri,
        token_path=secretsTDA.token_path)
stream_client = StreamClient(client, account_id=secretsTDA.accountID)

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

#to access streaming data
async def read_stream():
    await stream_client.login()
    await stream_client.quality_of_service(StreamClient.QOSLevel.EXPRESS)

    def print_message(message):
      print(json.dumps(message, indent=4))
      testQueue.enqueue((message))
      
    # Always add handlers before subscribing because many streams start sending
    # data immediately after success, and messages with no handlers are dropped.
    stream_client.add_level_one_equity_handler(print_message)
    await stream_client.level_one_equity_subs(["GOOG"])

    while True:
        await stream_client.handle_message()
        
async def close_stream():
    await stream_client.level_one_equity_unsubs(["GOOG"])

asyncio.run(read_stream())
#asyncio.run(close_stream())
