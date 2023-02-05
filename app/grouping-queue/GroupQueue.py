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

# TODO: Carry this over to the Slack Listener, we only handle clean data here
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
TIMER = 60
MAX_TIME_LIMIT = 100

# Determine how to prioritize attributes of the form. For example, a weight of
# {"a": 1, "b": 2} means that b will factor twice as much as a
WEIGHTS = {"size": 1, "difficulty": 3, "topics": 2}

# Classes for streamlining group matching
# Abstract Class Groupable
# Fields: attributes (dict), lifespan (int)
# Methods: Compare,  

def compare_groupable(user_x, user_y, weights):
    '''
    Create a compatbility rating between two users, two groups, or a user and a group
    Larger score is a worse score, you can think of it as the distance between two points
    :param user_x: A dictionary representing the desired group attributes
                   Two types of entries: String => Numeric & String => {String => Numeric}
    :param user_y: The user to compare to, follows a similar form
    :param weights: A dictionary that weighs the attributes, direct multiplication
                    There is no default because the user should have a good understanding
                    of what attributes and how they affect the desired result
    :return: A numeric score comparing each of the attributes they BOTH have
    
    Notes:
    - A numeric value of 0 is treated like a wildcard, (it zeroes out the error score)
      This is done to accomodate 'Surprise Me', with the goal of creating a match the fastest
      However, this doesn't apply to attribute dictionaries, to improve matching
    - The original comparison (diff, size, topics) just happened to have errors within 0-2 range
      Weights are still useful for shifting around the priority of attributes
    - Currently uses linear error, squaring the error may be better
    '''
    try:
        error_score = 0
        atts = list(set(user_x.keys()) & set(user_y.keys()))
        for att in atts:
            # Use the weights to control how the error contributes to the net error
            if isinstance(user_x[att], dict):
                # Assume that the sum of a single dictionary's values is 1, i.e. floats
                fields = list(set(user_x[att].keys()) & set(user_y[att].keys()))
                dict_score = 2 - sum((user_x[att][field] + user_y[att][field] for field in fields))
                error_score += weights[att] * (dict_score)
            else:
                # Assume the internal dictionary is Key => Numeric
                error_score += weights[att] * (abs(user_x[att] - user_y[att]) if user_x[att] * user_y[att] != 0 else 0)
        return error_score
    except AttributeError:
        logger.error("Attribute mismatch when comparing " + str(user_x) + " and " + str(user_y))
        return 2000000 # Some arbitarily high number
    except TypeError:
        logger.error("Attribute values are not compatible when comparing " + str(user_x) + " and " + str(user_y))
        return 2000000 # Some arbitrarily high number

# Create a server to handle user requests
listener = Listener((HOST, PORT), authkey=b'password')
queue = Queue() # Read & Write

# Thread A: Listen for server requests and handle immediate requests
def listener_thread(receiver, q: Queue):
    while True:
        with receiver.accept() as conn:
            packet = conn.recv()
            # If group form, add to queue & let Thread B handle it
            # If status check, check group status

# Thread B: Cron jobs, prevent listener from getting backed up
def worker_thread(q: Queue):
    while True:
        # Check for new users
        # Shift groups if possible
        # Check which groups are ready and if users need to repoll
        # Send messages
        # Remove groups/users
        # Generate iterative log
        time.sleep(TIMER)
        pass

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
