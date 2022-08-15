
"""
Simple team formation algorithm, designed for team sizes 2 - 4
Contributor: Nicolas Guerrero

TODO: Change the group lists into group objects to improve abstraction

Note: Simple Group is extremely rudimentary, it will not always create ideal groups, even when
ideal conditions can be met. This function should only be used in the prototype and maybe early
servers. The grouping will need to be improved in the future. Also, make sure to acknowledge that
a perfect match couldn't be found whenever returning un-ideal results.
"""

def simple_group(forms):
    """Create study groups from Slack submissions
    :param forms: A list of dictionaries representing the forms that users submit
                  through the Slack API. Form data should be organized as follows:
                  {
                    "slack_id": String for user identification and messaging,
                    "meeting_type": String for type of meeting (e.g. "Mock Interview"),
                    "meeting_size": Int, either 2, 3, or 4, determining the size of the team,
                    "topic": String reprenting the topic meeting
                  }
    :returns: A list of dictionaries, with the following group details
              {
                "meeting_type": String for the type of meeting,
                "topics": List of strings for all topic tags
                "members": List of slack ids for the members of a group
              }
              A group size of 1 means no group could be found
    """
    # Seperate users strictly by meeting type
    categories = {}
    for form in forms:
        if form["meeting_type"] in categories.keys():
            categories[form["meeting_type"]].append(form)
        else:
            categories[form["meeting_type"]] = [form]
    # Simple Grouping
    groups = []
    # WARNING: These values are hard-coded, change when possible
    minimum = lambda x: x >= 2 and x <= 4                               # x: current size
    ideal = lambda x, y: minimum(x) and (x <= y + 1) and (x >= y - 1)   # x: current size, y: specified size
    for category in categories.values():
        category.sort(key=lambda x: (x["meeting_size"], x["topic"]))
        # Try to create ideal groups, if not possible pull from previous (first should never pull)
        # You may pull a group down to minimum (2), hence imperfect group
        stragglers = []
        index_queue = [0]
        category_queue = []
        current_queue = []
        current_size = category[0]["meeting_size"]
        for member in category:
            # Check for stragglers
            if member["meeting_size"] != current_size:
                if ideal(len(current_queue), current_size):
                    category_queue.append(current_queue)
                else:
                    stragglers.extend(current_queue)
                current_queue = []
                current_size = member["meeting_size"]
                index_queue.append(len(category_queue))
            # Group forming
            current_queue.append(member)
            if len(current_queue) == current_size:
                category_queue.append(current_queue)
                current_queue = []
        # Empty the current queue, O(k) w/ k <= max group size
        if ideal(len(current_queue), current_size):
            category_queue.append(current_queue)
        else:
            stragglers.extend(current_queue)
        # Empty the straggler queue O(k*n) w/ 1/2k^2 -2k for k = max group size, roughly
        while len(stragglers) > 0:
            if minimum(len(stragglers)):
                category_queue.append(stragglers)
                stragglers = []
            else:
                head = stragglers.pop()
                ind = len(category_queue) - 1 if head["meeting_size"] > 3 else index_queue[-1] # HARD-CODED VALUE, REMOVE BEFORE PRODUCTION
                while head and (ind >= 0):
                    size = category_queue[ind][0]["meeting_size"]
                    if ideal(size + 1, size):
                        category_queue[ind].append(head)
                        head = False
                    ind -= 1
                if head: category_queue.append([head])
        groups.extend(category_queue)
    # Convert group list to group objects
    return group_formatting(groups)

def group_formatting(groups):
    """ Convert member data list to group dictionaries
    :param groups: A list of lists of dictionaries, each list contains the information for making a group. Ex:
        [
            [
                {"slack_id": str Slack ID, "meeting_type": str, "meeting_size": int, "topic": str},
                {"slack_id": str Slack ID, "meeting_type": str, "meeting_size": int, "topic": str},
                etc.
            ],
            [
                {"slack_id": str Slack ID, "meeting_type": str, "meeting_size": int, "topic": str},
                {"slack_id": str Slack ID, "meeting_type": str, "meeting_size": int, "topic": str},
                etc.
            ],
            etc.
        ]
    :return: A list of dictionaries that contain group data
        [
            {"meeting_type": str, "topics": List of strings for all topic tags, "members": List of slack ids},
            {"meeting_type": str, "topics": List of strings for all topic tags, "members": List of slack ids},
            etc.
        ]
    """
    formatted_groups = []
    for group in groups:
        cluster = {}
        cluster["meeting_type"] = group[0]["meeting_type"]
        cluster["topics"] = [x["topic"] for x in group]
        cluster["members"] = [x["slack_id"] for x in group]
        formatted_groups.append(cluster)
    return formatted_groups
    
# TESTING
# TODO: Build proper testing classes
x = [
    {"slack_id": 1, "meeting_type": "mock_interview", "meeting_size": 2, "topic": "arrays"},
    {"slack_id": 2, "meeting_type": "mock_interview", "meeting_size": 2, "topic": "arrays"},
    {"slack_id": 3, "meeting_type": "mock_interview", "meeting_size": 2, "topic": "arrays"},
    {"slack_id": 4, "meeting_type": "mock_interview", "meeting_size": 2, "topic": "arrays"},
    {"slack_id": 5, "meeting_type": "mock_interview", "meeting_size": 2, "topic": "arrays"},
    {"slack_id": 6, "meeting_type": "mock_interview", "meeting_size": 3, "topic": "arrays"},
    {"slack_id": 7, "meeting_type": "mock_interview", "meeting_size": 3, "topic": "arrays"},
    {"slack_id": 8, "meeting_type": "mock_interview", "meeting_size": 3, "topic": "arrays"},
    {"slack_id": 9, "meeting_type": "mock_interview", "meeting_size": 3, "topic": "arrays"},
    {"slack_id": 10, "meeting_type": "mock_interview", "meeting_size": 4, "topic": "arrays"},
    {"slack_id": 11, "meeting_type": "group_problem_solving", "meeting_size": 4, "topic": "arrays"},
    {"slack_id": 13, "meeting_type": "group_problem_solving", "meeting_size": 4, "topic": "arrays"},
    {"slack_id": 14, "meeting_type": "group_problem_solving", "meeting_size": 4, "topic": "arrays"},
    {"slack_id": 15, "meeting_type": "group_problem_solving", "meeting_size": 4, "topic": "arrays"},
    {"slack_id": 16, "meeting_type": "group_problem_solving", "meeting_size": 4, "topic": "arrays"},
    {"slack_id": 17, "meeting_type": "group_problem_solving", "meeting_size": 4, "topic": "arrays"},
    {"slack_id": 18, "meeting_type": "group_problem_solving", "meeting_size": 2, "topic": "arrays"},
]
y = simple_group(x)
log = open("log.txt", "w")
for z in y:
    log.write(str(z))
    log.write("\n")
log.close()