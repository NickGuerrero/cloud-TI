"""
Template for notifying users of the group that they're part of
# TODO: Modify allowable group forms so that the site url base can be changed
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
                        "difficulty": Numeric difficulty rating (1 for easy, 2 for medium, 3 for hard)
                        "tags": Set of strings, each representing a unique tag associated with the problem
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

def link_block(title, link, diff=0, tags=[], res_base="https://leetcode.com"):
    """Create a slack block for presenting resource links
    :param title: String that explains where the URL is going to
    :param link: String with the URL sub-directory/extension
    :paran res_base: String with the URL up to the top-level scheme

    Note that link and res_base were initially split to save space in the database
    since all links would re-direct to 1 website, with different extensions
    """
    # Create difficulty & tag strings TODO: Consider returning difficulty as string to streamline
    d = ""
    if diff in (1,2,3):
        d += " " + {1:"Easy", 2:"Medium", 3:"Hard"}[diff]
    if len(tags) > 0:
        d += " (" + ", ".join(tags) + ")"
    if len(d) > 0:
        d += "\n"
    # Write message
    s = "{}:{} {}".format(title, d, res_base + link)
    block = {
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": s
			}
		}
    return block