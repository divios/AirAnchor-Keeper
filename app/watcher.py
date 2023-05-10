
from pika import BlockingConnection, ConnectionParameters
import zmq

from pymongo import MongoClient
from datetime import datetime

import concurrent.futures

from sawtooth_sdk.protobuf.events_pb2 import EventSubscription, EventList
from sawtooth_sdk.protobuf.client_event_pb2 import ClientEventsSubscribeRequest, ClientEventsSubscribeResponse
from sawtooth_sdk.protobuf.validator_pb2 import Message
from sawtooth_sdk.messaging.stream import Stream

from air_anchor_tracker.data import MongoRepo

def _validate_tcp_url(url: str):
    return 'tcp://' + url if not url.startswith("tcp://") else url


class Watcher:
    
    def __init__(self, zmq_url, rabbit_url: str):
        url = _validate_tcp_url(zmq_url)
        print("Initilizating zmq in {}".format(url))
        self._connection = Stream(url)
        
        self.rabbit_url = rabbit_url
        self.rabbit_connection =  BlockingConnection(ConnectionParameters(host=rabbit_url))
        
        self.rabbit_connection.channel().queue_declare(
            queue="gateway_callback_queue", durable=True)
        
        
        
    def start(self):
        print("Sending subscribe message")
        future = self._send_subscribe_msg()
        
        self._validate_response_msg(future)
        print("Subscribe successful")
    
        print("Starting main loop...")
        self._start_receive_loop()
        
                
    def _send_subscribe_msg(self):
        subscription = EventSubscription(
            event_type="AirAnchor/create",
            filters=[])
        
        request = ClientEventsSubscribeRequest(
            subscriptions=[subscription]).SerializeToString()
        
        # Construct the message wrapper
        return self._connection.send(
            message_type=Message.CLIENT_EVENTS_SUBSCRIBE_REQUEST,
            content=request)
                
    def _validate_response_msg(self, future):
        msg = future.result()
        
        # Validate the response type
        if msg.message_type != Message.CLIENT_EVENTS_SUBSCRIBE_RESPONSE:
            print("Unexpected message type")
            exit(-1)

        # Parse the response
        response = ClientEventsSubscribeResponse()
        response.ParseFromString(msg.content)

        # Validate the response status
        if response.status != ClientEventsSubscribeResponse.OK:
            print("Subscription failed: {}".format(response.response_message))
            return
                
    def _start_receive_loop(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            while True:
                msg = self._connection.receive().result()
                print("received msg")

                executor.submit(self._handle_event_msg, msg)
                
    def _handle_event_msg(self, msg):
        # Validate the response type
        if msg.message_type != Message.CLIENT_EVENTS:
            print("Unexpected message type")
            return

        # Parse the response
        eventList = EventList()
        eventList.ParseFromString(msg.content)

        print("Received events ------")
        for event in eventList.events:
            print(event)
            for attribute in event.attributes:
                if (attribute.key) == 'key':
                    key_value = attribute.value
                if (attribute.key) == 'hash':
                    hash_value = attribute.value
                
            # Update document in mongo
            try:
                if not self.rabbit_connection or self.rabbit_connection.is_closed:
                    self.rabbit_connection = BlockingConnection(ConnectionParameters(host=self.rabbit_url))
                    
                channel = self.rabbit_connection.channel()
                
                channel.basic_publish(exchange='',
                                                routing_key='gateway_callback_queue',
                                                body=hash_value)
                
                print("Sended ack to route {}".format(hash_value))
                
            except Exception as e:
                print(e)
            
            