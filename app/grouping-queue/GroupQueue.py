from utils import SimpleGrouper
from modals import GroupFormResponse
from multiprocessing import Process, Queue
from multiprocessing.connection import Listener, Client
import threading

import json
import logging
import os
import time
import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

SECRET = "password" # Please replace this with a value in the environment
def is_user_request(req): return all(k in req for k in ("slack_id","meeting_type", "meeting_size", "topic"))
def is_command(req): "cmd_secret" in req and req["cmd_secret"] == SECRET

def correct_form(x):
    """ Fix the form received from the listener to work with the simple grouper """
    output = {}
    output["slack_id"] = x['slack_id']
    output["meeting_type"] = x['meeting_type']['selected_option']['text']['text']
    output["meeting_size"] = int(x['meeting_size']['selected_option']['text']['text'])
    output["topic"] = x['topic']['selected_option']['text']['text']
    return output

# WebClient instantiates a client that can call API methods
# When using Bolt, you can use either `app.client` or the `client` passed to listeners.
client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))

# Logging
dt = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
logging.basicConfig(filename="listener-queue-" + dt + ".log", level=logging.INFO)
logger = logging.getLogger(__name__)

# Assume the event listener and queue are on the same Docker instance
HOST = "group-queue"
PORT = 4000
# CHANGED FOR DEBUGGING
TIMER = 60 # 1 minute
MAX_TIME_LIMIT = 100 # 1 minute, 40 seconds

# Create a server to handle user requests
listener = Listener((HOST, PORT), authkey=b'password')

while True:
    logger.info("Starting polling cycle")
    try:
        # Open queue and polling session on first request
        queue = Queue()
        conn = listener.accept()
        msg = conn.recv()
        if not is_user_request(msg) or is_command(msg): raise Exception("Invalid message recieved")
        if is_user_request(msg):
            queue.put(msg)
            conn.send(1)
        
        # Thread A: Listener, only ends on command
        def proc_a(receiver, q: Queue):
            active = True
            while active:
                with receiver.accept() as conn:
                    msg = conn.recv()
                    if is_user_request(msg):
                        q.put(msg)
                        conn.send(1)
                    elif is_command(msg):
                        if msg["cmd"] == "stop":
                            active = False
                    else:
                        conn.send(0)

        # Thread B: Timer
        def proc_b(t=TIMER):
            time.sleep(t)
            done = False
            while not done:
                with Client((HOST, PORT), authkey=b'password') as conn:
                    conn.send({"cmd_secret": "password","cmd": "stop"})
                    done = conn.recv()

        # Threading implementation of above
        logger.info("Starting Threading")
        polling = threading.Thread(target=proc_a, args=(listener, queue))
        timer = threading.Thread(target=proc_b, args=(TIMER,))
        polling.start()
        timer.start()
        polling.join(MAX_TIME_LIMIT)
        logger.info("Polling status after join:" + str(polling.is_alive()))
        logger.info("Timer status after join:" + str(timer.is_alive()))
        
        # TODO: Check if we can message multiple students at once instead of one at a time
        # TODO: Also check if that's viable or if it's too overwhelming
        # After all requests received, return the results
        tmp = [correct_form(queue.get()) for i in range(queue.qsize())]
        logger.info("Queue after polling: " + str(tmp))
        groups = SimpleGrouper.simple_group(tmp)
        logger.info("Groupings: " + str(groups))
        for group in groups:
            mail = json.dumps(GroupFormResponse.generate_response(group)["blocks"])
            for member in group["members"]:
                try:
                    result = client.conversations_open(token=os.environ.get("SLACK_BOT_TOKEN"), users=member)
                    if result["ok"]:
                        result = client.chat_postMessage(
                            channel=result["channel"]["id"],
                            blocks=mail
                        )
                except SlackApiError as e:
                    logger.error(f"Error: {e}")

    except Exception as e:
        logger.error(e)
