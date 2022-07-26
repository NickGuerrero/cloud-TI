import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter
import random
​
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
​
app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'],'/slack/events', app)
​
client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']
#client.chat_postMessage(channel='#general', text='pineapple pizza supremacy')
​
@slack_event_adapter.on('app_mention')
def message(payload):
    event = payload.get('event', {})
    user_id = event.get('user')
    text = event.get('text')
    if BOT_ID != user_id:
        if "random number" in text.lower():
            client.chat_postMessage(channel='#general', text=random.randint(1,100))
        else:
            client.chat_postMessage(channel='#general', text='Hello <@' + user_id + ">!")
 
​
#run flask app on default port, can set port
#if we modify script, web server is automatically updated
if __name__ == "__main__":
    app.run(debug=True)