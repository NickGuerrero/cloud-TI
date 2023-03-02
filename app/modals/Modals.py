from slack_bolt import App

# Creates home app
# must subscribe to app_home_opened event
def homepage(client, event, logger):
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
                            "text": "CTI Accelerate Homepage"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "plain_text",
                            "text": "Welcome to the CTI homepage! Here, you can find links to resources and find a group to work with."
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Access the student handbook"
                        },
                        "accessory": {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Handbook",
                                "emoji": True
                            },
                            "value": "click_me_1",
                            "url": "https://bit.ly/Accelerate-Student-Handbook",
                            "action_id": "button-action"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Access the CTI Canvas Site"
                        },
                        "accessory": {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Canvas",
                                "emoji": True
                            },
                            "value": "click_me_2",
                            "url": "https://cti-courses.instructure.com/",
                            "action_id": "button-action"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Access Deep Work schedule and Links"
                        },
                        "accessory": {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Deep Work",
                                "emoji": True
                            },
                            "value": "click_me_3",
                            "url": "https://docs.google.com/spreadsheets/d/1C8FLUGrIDRXRkBgvDsNOmqwcW4go4QwfNOxoytjDvEk/edit#gid=0",
                            "action_id": "button-action"
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "Personalized Functionalities"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Homework/General Coding Assistance"
                        },
                        "accessory": {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Find Resources"
                            },
                            "value": "click_me_1234",
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
                                "text": "Find A Group"
                            },
                            "value": "click_me_123",
                            "action_id": "group-button"
                        }
                    },
                    {
                        "type": "divider"
                    }
                ]
            }
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")


def resource_modal(ack, body, client):
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


def group_modal(ack, body, client):
    ack()
    client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "group_view",
            "title": {
                "type": "plain_text",
                "text": "Mock Interview Finder"
            },
            "submit": {
                "type": "plain_text",
                "text": "Submit"
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
                        "text": "Find a Group"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": "Find a group to work together during today's session"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "input",
                    "block_id": "meet_size",
                    "element": {
                        "type": "static_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select an item"
                        },
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Pair (2 people)"
                                },
                                "value": "siz-small"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Trio (3 people)"
                                },
                                "value": "siz-medium"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Squad (4 people)"
                                },
                                "value": "siz-large"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Either is fine"
                                },
                                "value": "siz-any"
                            }
                        ],
                        "action_id": "meet_size_value"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Ideal Group Size"
                    }
                },
                {
                    "type": "input",
                    "block_id": "problem_difficulty",
                    "element": {
                        "type": "static_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select an item"
                        },
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Easy"
                                },
                                "value": "dif-easy"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Medium"
                                },
                                "value": "dif-medium"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Hard"
                                },
                                "value": "dif-hard"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Any will do"
                                },
                                "value": "dif-any"
                            }
                        ],
                        "action_id": "problem_difficulty_value"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Ideal Problem Difficulty"
                    }
                },
                {
                    "type": "input",
                    "block_id": "topic_selection",
                    "element": {
                        "type": "multi_static_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select topics",
                        },
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Array",
                                },
                                "value": "top-array"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "String",
                                },
                                "value": "top-string"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Sorting",
                                },
                                "value": "top-sorting"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Tree",
                                },
                                "value": "top-tree"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Greedy",
                                },
                                "value": "top-greedy"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Stack",
                                },
                                "value": "top-stack"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Recursion",
                                },
                                "value": "top-recursion"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Math",
                                },
                                "value": "top-math"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Geometry",
                                },
                                "value": "top-geometry"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Divide and Conquer",
                                },
                                "value": "top-divide_and_conquer"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Surprise Me",
                                },
                                "value": "top-any"
                            }
                        ],
                        "action_id": "topic_list_value"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Topic Suggestions",
                    }
                }
            ]
        }
    )

