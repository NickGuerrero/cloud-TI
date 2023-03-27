from utils import QueueGrouper, UserGroup, ResourceFinder
from modals import GroupFormResponse

from multiprocessing import Process, Queue
from multiprocessing.connection import Listener, Client
from queue import Empty as EmptyQueue
from collections import deque
import threading

import json
import logging
import os
import time
import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# WebClient instantiates a client that can call API methods
# When using Bolt, you can use either `app.client` or the `client` passed to listeners.
client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))

# Logging
# TODO: Determine why the logs are no longer being written to a file
dt = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
logging.basicConfig(filename="listener-queue-" + dt + ".log", level=logging.INFO)
logger = logging.getLogger(__name__)

# Assume the event listener and queue are on the same Docker instance
HOST = "group-queue"
PORT = 4000
# Path to SQL scripts for constructing a temporary database
DATABASE_PATH = "/sql/resource_database.sql"
# CHANGED FOR DEBUGGING
TIMER = 15                      # Seconds to wait between cycles
TIMEOUT_THRESHOLD = 12          # Number of cycles to wait before sending feedback to user
SECRET = "PASSWORD"
PACKET_CONTENT = ("slack_id", "difficulty", "meeting_size", "topics")

# Determine how to prioritize attributes of the form. For example, a weight of
# {"a": 1, "b": 2} means that b will factor twice as much as a
WEIGHTS = {"meeting_size": 2, "difficulty": 3, "topics": 1}

# Thread A: Listen for server requests and handle immediate requests
def listener_thread(receiver, user_req_queue: Queue):
    logger.info("Listener Thread started")
    while True:
        with receiver.accept() as conn:
            packet = conn.recv()
            if packet["header"] == "user_queue_request" and packet["secret"] == SECRET:
                # Filter out the packet content and put in user queue
                user_req_queue.put({x: packet[x] for x in PACKET_CONTENT}, block=False)
                conn.send(1)
            elif packet["header"] == "check_queue_count" and packet["secret"] == SECRET:
                # Check status of users waiting in the queue TODO: Not implemented yet until needed
                conn.send(-1)
            elif packet["secret"] != SECRET:
                logger.warning("Request secret does not match with packet contents: " + str(packet))
                conn.send(-1)
            else:
                logger.warning("Request does not exist with packet contents: " + str(packet))
                conn.send(-1)

# Thread B: Cron jobs, prevent listener from getting backed up
# TODO: Illegitmate packets will crash this thread, you should add safeguards
def worker_thread(user_req_queue: Queue, db_conn, timer=TIMER):
    logger.info("Cron job thread started")
    UserGroup.UserGroup.reset() # Ensure that the UserGroup user list is clean for a new run
    groups_waiting = deque(maxlen=300)
    while True:
        start_time = time.time()
        # Check for new users TODO: Make this cleaner, only one try block should be necessary
        logger.info("Pulling new user requests into the system")
        users_waiting = deque(maxlen=100)
        try:
            while True:
                try:
                    current_user = user_req_queue.get(block=False)
                    users_waiting.append(UserGroup.convert_to_usergroup(current_user))
                except UserGroup.DuplicateUserException:
                    logger.error("User " + current_user["slack_id"] + " is already in the queue")
        except EmptyQueue: pass
        # Match users and increase group timeout
        logger.info("Matching groups together")
        QueueGrouper.group_matcher(users_waiting, groups_waiting, WEIGHTS, compromise_factor=2, match_threshold=4)
        # Increase timeout, remove groups if they passed their expiration date
        exit_queue = deque(maxlen=300)
        groups_waiting.append(None)
        while groups_waiting[0] is not None:
            if groups_waiting[0].timeout < TIMEOUT_THRESHOLD:
                groups_waiting[0].step()
                groups_waiting.rotate(-1)
            else:
                groups_waiting[0].expire() # Remove users from the no-repeat set
                exit_queue.append(groups_waiting.popleft())
        groups_waiting.popleft()
        # Message groups on the exit queue (Single id means timeout, multiple people mean group matched)
        logger.info("Sending messages to expired groups")
        for group in exit_queue:
            # Suggest resources for each group from the db_conn
            res_list = ResourceFinder.suggest_resource(db_conn, {"difficulty": group.attr["difficulty"], "topics": group.attr["topics"]})
            mail = json.dumps(GroupFormResponse.generate_response(group.to_group_form(), resources=res_list)["blocks"]) #TODO Add resources here
            try:
                result = client.conversations_open(token=os.environ.get("SLACK_BOT_TOKEN"), users=",".join(group.ids))
                if result["ok"]:
                    result = client.chat_postMessage(
                        channel=result["channel"]["id"],
                        blocks=mail
                    )
            except SlackApiError as e:
                logger.error(f"Error: {e}")
        exit_queue.clear()
        # Generate iterative log
        logger.info("All jobs finished in cycle, waiting for next iteration...")

        # Determine wait time for next iteration
        end_time = time.time() - start_time
        if(end_time > timer): logger.warning("Cron job runtime exceeds the time allotted: " + str(end_time))
        time.sleep(timer - min(timer, end_time))

def main():
    # Create a server to handle user requests
    listener = Listener((HOST, PORT), authkey=b'password')
    incoming_users = Queue(maxsize=100) # Process incoming requests, 100 is a safe cap
    # Instantiate a temporary database for managing resources
    db_conn = ResourceFinder.create_temporary_database(DATABASE_PATH)
    # Start threads
    request_accepter = threading.Thread(target=listener_thread, args=(listener, incoming_users))
    cron_jobs = threading.Thread(target=worker_thread, args=(incoming_users, db_conn, TIMER))
    request_accepter.start()
    cron_jobs.start()
    request_accepter.join()

if __name__ == "__main__":
    main()