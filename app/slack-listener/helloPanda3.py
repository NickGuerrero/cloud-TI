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

@app.view("group_view")
def handle_submission(ack, body, client, view, logger):
    ack()
    # Create packet from the form data
    group_dict = dict()
    group_dict["header"] = "user_queue_request"
    group_dict["secret"] = "PASSWORD"
    group_dict["slack_id"] = body["user"]["id"]
    group_dict["meeting_size"] = view["state"]["values"]["meet_size"]["meet_size_value"]['selected_option']['value']
    group_dict["difficulty"] = view["state"]["values"]["problem_difficulty"]["problem_difficulty_value"]['selected_option']['value']
    group_dict["topics"] = [x['value'] for x in view["state"]["values"]["topic_selection"]["topic_list_value"]['selected_options']]

    # Send data to queue and acknowledge
    try:
        HOST = 'group-queue'            # Localhost
        PORT = 4000                     # Port location of other program
        with Client((HOST, PORT), authkey=b'password') as conn:
            conn.send(group_dict)
            response = conn.recv()
        if response > 0:
            m = "You will be placed in a group shortly. If this is your first time, please read our quick guide for getting started: "
            m += os.environ["MOCK_INTERVIEW_QUICK_GUIDE"]
            client.chat_postMessage(channel=group_dict["slack_id"], text=m)
        else:
            client.chat_postMessage(channel=group_dict["slack_id"], text="Something went wrong, please report this issue to @NicolasGuerrero")
    except Exception as e:
        logger.exception(f"Failed to post a message {e}")

@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    urls = {
        "STUDENT_HANDBOOK_LINK": os.environ['STUDENT_HANDBOOK_LINK'],
        "CANVAS_LINK": os.environ['CANVAS_LINK'],
        "DEEP_WORK_SESSION_LINK": os.environ['DEEP_WORK_SESSION_LINK']
    }
    Modals.homepage(client, event, logger, links=urls)

# Temporarily removed from the homepage
@app.action("resource-button")
def open_resource_modal(ack, body, client):
    Modals.resource_modal(ack, body, client)

@app.action("group-button")
def open_group_modal(ack, body, client):
    Modals.group_modal(ack, body, client)


# Starts app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
