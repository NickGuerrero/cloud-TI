#put modals in separate files

from ctypes import create_string_buffer
import os
from slack_bolt import App
from dotenv import load_dotenv
from pathlib import Path
import random
from modals import Modals
from multiprocessing.connection import Client

# loads env variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Initializes app with bot token and signing secret
app = App(
    token=os.environ['SLACK_BOT_TOKEN'],
    signing_secret=os.environ['SLACK_SIGNING_SECRET']
)

# functionality
@app.event("app_mention")
def event_test(body, say):
    print(body)
    user_id = body["event"]["user"]
    if "random number" in body["event"]["text"].lower():
        say("Here's a random number: " + str(random.randint(1,100)))
    else:
        say("Hello <@" + user_id + ">!")


'''
{
"slack_id": String for user identification and messaging,
"meeting_type": String for type of meeting (e.g. "Mock Interview"),
"meeting_size": Int, either 2, 3, or 4, determining the size of the team,
"topic": String representing the topic meeting
"group_type": String for determining if group is static or dynamic
}
'''
@app.view("group_view")
def handle_submission(ack, body, client, view, logger):
    # Collect form data
    group_dict = dict()
    group_dict["slack_id"] = body["user"]["id"]
    group_dict["meeting_type"] = view["state"]["values"]["meet_type"]["meet_type_value"]
    group_dict["meeting_size"] = view["state"]["values"]["meet_size"]["meet_size_value"]
    group_dict["group_type"] = view["state"]["values"]["group_type"]["group_type_value"]
    group_dict["topic"] = view["state"]["values"]["topic_type"]["topic_type_value"]

    ack()
    # Send data to queue and acknowledge
    try:
        HOST = 'group-queue'              # Localhost
        PORT = 4000                     # Port location of other program
        with Client((HOST, PORT), authkey=b'password') as conn:
            conn.send(group_dict)
            response = conn.recv()
        if response > 0:
            client.chat_postMessage(channel=group_dict["slack_id"], text="You will be placed in a group shortly")
        else:
            client.chat_postMessage(channel=group_dict["slack_id"], text="Something went wrong, please report this issue to @NicolasGuerrero")
    except Exception as e:
        logger.exception(f"Failed to post a message {e}")
    # return group_dict

@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    Modals.homepage(client, event, logger)

@app.action("resource-button")
def open_resource_modal(ack, body, client):
    Modals.resource_modal(ack, body, client)

@app.action("group-button")
def open_group_modal(ack, body, client):
    Modals.group_modal(ack, body, client)


# Starts app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
