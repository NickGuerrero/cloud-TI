from ctypes import create_string_buffer
import os
from slack_bolt import App
from dotenv import load_dotenv
from pathlib import Path
import random

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







#Creates home app
#must subscribe to the app_home_opened event
@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    try:
        client.views_publish(
            # Use the user ID associated with the event
            user_id=event["user"],
            view={
                "type": "home",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "Welcome Home",
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "plain_text",
                            "text": "Homepage for resources and workshopping",
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "This is a header block",
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Homework/general coding assistance"
                        },
                        "accessory": {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Find Resources",
                            },
                            "value": "click_me_123",
                            "action_id": "resource-button"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Mock Interview/Resume Workshopping"
                        },
                        "accessory": {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Find A Group",
                            },
                            "value": "click_me_123",
                            "action_id": "group-button"
                        }
                    }
                ]
            }
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")



@app.action("resource-button")
def open_resource_modal(ack, body, client):
    ack()
    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "submit": {
                "type": "plain_text",
                "text": "Submit",
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel",
            },
            "title": {
                "type": "plain_text",
                "text": "Find Resources",
            },
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": "Get resources to help you on your coding journey!",
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "input",
                    "label": {
                        "type": "plain_text",
                        "text": "What course are you in now?",
                    },
                    "element": {
                        "type": "multi_static_select",
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "101",
                                },
                                "value": "value-0"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "201",
                                },
                                "value": "value-1"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "202",
                                },
                                "value": "value-2"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "301",
                                },
                                "value": "value-3"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "302",
                                },
                                "value": "value-4"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Beyond 302",
                                },
                                "value": "value-5"
                            }
                        ]
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Select the types of resources you would like to see:*"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "checkboxes",
                            "options": [
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Videos",
                                    },
                                    "value": "value-0"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Coding Problems",
                                    },
                                    "value": "value-1"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Reading Material",
                                    },
                                    "value": "value-2"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Tutorials",
                                    },
                                    "value": "value-2"
                                }
                            ],
                            "action_id": "actionId-0"
                        }
                    ]
                }
            ]
        }
    )




@app.action("group-button")
def open_group_modal(ack, body, client):
    ack()
    print("GROUP BUTTON PRESSED")
    client.views_open(
        trigger_id=body["trigger_id"],
        view={
	"type": "modal",
	"title": {
		"type": "plain_text",
		"text": "My App",
	},
	"submit": {
		"type": "plain_text",
		"text": "Submit",
	},
	"close": {
		"type": "plain_text",
		"text": "Cancel",
	},
	"blocks": [
		{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "This is a header block",
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "Group Size"
			},
			"accessory": {
				"type": "static_select",
				"placeholder": {
					"type": "plain_text",
					"text": "Select an item",
				},
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": "2",
						},
						"value": "value-0"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "3",
						},
						"value": "value-1"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "4",
						},
						"value": "value-2"
					}
				],
				"action_id": "static_select-action"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "Meeting Type"
			},
			"accessory": {
				"type": "static_select",
				"placeholder": {
					"type": "plain_text",
					"text": "Select an item",
				},
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": "Mock Interview",
						},
						"value": "value-0"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Group Problem Solving",
						},
						"value": "value-1"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Resume Review",
						},
						"value": "value-2"
					}
				],
				"action_id": "static_select-action"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "Topic"
			},
			"accessory": {
				"type": "static_select",
				"placeholder": {
					"type": "plain_text",
					"text": "Select an item",
				},
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": "Data Types",
						},
						"value": "value-0"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Loops",
						},
						"value": "value-1"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Arrays",
						},
						"value": "value-2"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Algorithms",
						},
						"value": "value-2"
					}
				],
				"action_id": "static_select-action"
			}
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "Group Type"
			},
			"accessory": {
				"type": "static_select",
				"placeholder": {
					"type": "plain_text",
					"text": "Select an item",
				},
				"options": [
					{
						"text": {
							"type": "plain_text",
							"text": "Dynamic",
						},
						"value": "value-0"
					},
					{
						"text": {
							"type": "plain_text",
							"text": "Fixed",
						},
						"value": "value-1"
					}
				],
				"action_id": "static_select-action"
			}
		}
	]
}
    )


# Starts app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
