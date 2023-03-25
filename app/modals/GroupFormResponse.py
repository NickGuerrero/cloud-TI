"""
Template for notifying users of the group that they're part of
TODO: Modify this so that it accepts a UserGroup object instead
"""

def generate_response(group_form, resources=[]):
    """Convert the group dictionaries generated from the matching process into Slack message blocks
    :param group_form: A dictionary in the following format:
                    {
                        "meeting_type": String for the type of meeting,
                        "topics": List of strings for all topic tags
                        "members": List of slack ids for the members of a group
                    }
    :param resources: A list of dictionaries with resource attributes w/ at least the following
                    {
                        "title": String with the name of the resource,
                        "link": String with link that redirects to external resource
                    }
    :return: A dictionary formatted into a Slack message block
    """
    if len(group_form["members"]) <= 1:
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Sorry, no team members were found"
                }
		    }
        ]
    else:
        m = "Members: "
        for id in group_form["members"]:
            m += "<@" + id + ">"
        m += "\nTopics: "
        m += ", ".join(set(group_form["topics"]))
        m += "\nHere are some recommended activities:"
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Group Matched for " + group_form["meeting_type"]
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": m
                }
            }
        ]
        # Append resource links here
        for res in resources:
            blocks.append(link_block(res["title"], res["link"]))
    return {"blocks": blocks}

def link_block(title, link):
    """I'm separating this as a function in case we want to change how links are presented"""
    s = "{}: {}".format(title, link)
    block = {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": s
			}
		}
    return block