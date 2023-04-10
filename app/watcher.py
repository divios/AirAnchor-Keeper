
import zmq

from pymongo import MongoClient

import concurrent.futures

from sawtooth_sdk.protobuf.events_pb2 import EventSubscription, EventList
from sawtooth_sdk.protobuf.client_event_pb2 import ClientEventsSubscribeRequest, ClientEventsSubscribeResponse
from sawtooth_sdk.protobuf.validator_pb2 import Message

class Watcher:
    
    def __init__(self, zmq_url, mongo_url, mongo_document, mongo_collection):
        ctx = zmq.Context()
        self._socket = ctx.socket(zmq.DEALER)
        self._socket.connect(zmq_url)
        
        client = MongoClient(mongo_url)
        db = client[mongo_document]
        self._collection = db[mongo_collection]
        
        
    def start(self):
        print("Sending subscribe message")
        self._send_subscribe_msg()
        
        self._validate_response_msg()
        print("Subscribe succesfull")
    
        print("Starting main loop...")
        self._start_receive_loop()
        
                
    def _send_subscribe_msg(self):
        subscription = EventSubscription(
            event_type="AirAnchor/create",
            filters=[])
        
        request = ClientEventsSubscribeRequest(
            subscriptions=[subscription]).SerializeToString()
        
        # Construct the message wrapper
        correlation_id = "123" # This must be unique for all in-process requests
        msg = Message(
            correlation_id=correlation_id,
            message_type=Message.CLIENT_EVENTS_SUBSCRIBE_REQUEST,
            content=request)

        # Send the request
        self._socket.send_multipart([msg.SerializeToString()])
                
    def _validate_response_msg(self):
        resp = self._socket.recv_multipart()[-1]

        # Parse the message wrapper
        msg = Message()
        msg.ParseFromString(resp)
        
        # Validate the response type
        if msg.message_type != Message.CLIENT_EVENTS_SUBSCRIBE_RESPONSE:
            print("Unexpected message type")
            return

        # Parse the response
        response = ClientEventsSubscribeResponse()
        response.ParseFromString(msg.content)

        # Validate the response status
        if response.status != ClientEventsSubscribeResponse.OK:
            print("Subscription failed: {}".format(response.response_message))
            return
                
    def _start_receive_loop(self):
        def inner_task():
            resp = self._socket.recv_multipart()[-1]

            # Parse the message wrapper
            msg = Message()
            msg.ParseFromString(resp)

            # Validate the response type
            if msg.message_type != Message.CLIENT_EVENTS:
                print("Unexpected message type")
                return

            # Parse the response
            events = EventList()
            events.ParseFromString(msg.content)

            print("Received events ------")
            for event in events:
                print(event)
                # Save in mongo
            
        with concurrent.futures.ThreadPoolExecutor() as executor:
            while True:
                executor.submit(inner_task)
        