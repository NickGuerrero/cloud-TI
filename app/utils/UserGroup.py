from copy import deepcopy

class DuplicateUserException(Exception):
    pass

class UserGroup:
    '''
    UserGroup: Represents users and group when forming groups together
    
    Class Attributes
    :user set(String): A set of strings, representing unique ids of all users waiting

    Instance Atrributes:
    :ids list(String): A list of slack ids that represent the group members
    :attr dict(String=>Numeric -OR- String=>dict(String=>Numeric)): A dictionary of attributes
        - String=>Numeric are values compared directly
        - String=>dict(String=>Numeric) are dictionary where all values add up to 1. Normalize when merging.
    :timeout int: The number of cycles that a UserGroup object has iterated through
    '''
    users = set()

    def __init__(self, slack_id, att_dict):
        '''
        Defines a UserGroup object from the provided id and comparison attributes
        :param slack_id: The unique id associated with each member (App uses the slack id)
        :param att_dict: The attribute dictionary for the instance
        '''
        if slack_id in UserGroup.users: raise DuplicateUserException
        UserGroup.users.add(slack_id)
        self.ids = [slack_id]
        self.attr = deepcopy(att_dict)
        self.timeout = 1

    def expire(self):
        '''Remove all group ids from the set of users'''
        for id in self.ids:
            UserGroup.users.remove(id)
    
    def merge(self, other):
        '''
        Merge this UserGroup with another UserGroup
        :param other: UserGroup object, combines the ids, attributes, and timeout
        '''
        self.ids.extend(other.ids)
        self.timeout = (self.timeout + other.timeout) // 2
        for att in self.attr.keys():
            if type(self.attr[att]) == dict:
                # Key => {Key => Numeric} takes the average for each internal key 
                for key in self.attr[att]:
                    self.attr[att][key] = self.attr[att][key] / 2
                # Note that the other UserGroup can add dictionary keys
                for key in other.attr[att]:
                    if key in self.attr[att].keys():
                        self.attr[att][key] += other.attr[att][key] / 2
                    else:
                        self.attr[att][key] = other.attr[att][key] / 2
            else:
                # Key => Numeric is just the average
                self.attr[att] = (self.attr[att] + other.attr[att]) / 2
    
    def step(self, n=1):
        '''Increment (or decrement) the timeout counter for checking group cohesion'''
        self.timeout += n

    # TODO: Consider streamlining this process so we don't have to adapt to old code
    def to_group_form(self):
        '''Create dictionary version of UserGroup, used in GroupFormResponse'''
        return {"members": self.ids, "topics": self.attr["topics"], "type": "Mock Interview"}

    @staticmethod
    def reset():
        '''Reset the unique id set to an empty if needed'''
        UserGroup.users = set()

# Compatibility Rating Function
def compare_groupable(user_x, user_y, weights):
    '''
    Create a compatbility rating between two users, two groups, or a user and a group
    Larger score is a worse score, you can think of it as the distance between two points
    :param user_x: A UserGroup object to compare to
    :param user_y: Another UserGroup Object
    :param weights: A dictionary that weighs the attributes, direct multiplication
                    The dictionary should match what's in the attribute dictionary already
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
        atts = list(set(user_x.attr.keys()) & set(user_y.attr.keys()))
        for att in atts:
            # Use the weights to control how the error contributes to the net error
            if isinstance(user_x.attr[att], dict):
                # Assume that the sum of a single dictionary's values is 1, i.e. floats
                fields = list(set(user_x.attr[att].keys()) & set(user_y.attr[att].keys()))
                dict_score = 2 - sum((user_x.attr[att][field] + user_y.attr[att][field] for field in fields))
                error_score += weights[att] * (dict_score)
            else:
                # Assume the internal dictionary is Key => Numeric
                error_score += weights[att] * (abs(user_x.attr[att] - user_y.attr[att]) if user_x.attr[att] * user_y.attr[att] != 0 else 0)
        return error_score
    except AttributeError:
        # logger.error("Attribute mismatch when comparing " + str(user_x) + " and " + str(user_y))
        return 2000000 # Some arbitarily high number
    except TypeError:
        # logger.error("Attribute values are not compatible when comparing " + str(user_x) + " and " + str(user_y))
        return 2000000 # Some arbitrarily high number

# Convert packets into UserGroup objects (Moved here to make testing easier)
# TODO: Check whether the difficulty dictionary is necessary for converting the packet values
# You need to check the slack modal
def convert_to_usergroup(packet):
    '''
    Converts a packet recieved from Slack into a UserGroup object for easy matching
    :param packet: A dictionary with string keys and variable content

    Expected Packet Contents {
        slack_id (String): The slack id retrieve from the Slack API
        difficulty (String): A numeric score that associates with a difficulty
        meeting_size (String): A number that aligns with the desired group size
        topics (List(String)): A list of topics strings, we give these numeric weights
    }
    '''
    # Slack Conversion Key
    difficulties = {"dif-hard": 3, "dif-medium": 2, "dif-easy": 1, "dif-any": 0}
    meeting_sizes = {"siz-small": 2, "siz-medium": 3, "siz-large": 4, "siz-any": 0}
    topic_list = {"top-array": "array", "top-string": "string", "top-sorting": "sorting",
                  "top-tree": "tree", "top-greedy": "greedy", "top-stack": "stack",
                  "top-recursion": "recursion", "top-math": "math", "top-geometry": "geometry",
                  "top-divide_and_conquer": "divide-and-conquer", "top-any": "any"}
    # Get basic packet content
    id = packet["slack_id"]
    diff = int(difficulties[packet["difficulty"]])
    sz = int(meeting_sizes[packet["meeting_size"]])
    # Create the topic dictionary, topics have weight 1 / size of the topic list
    ls = dict()
    ls_size = len(packet["topics"])
    for topic in packet["topics"]:
        ls[topic_list[topic]] = 1 / ls_size
    return UserGroup(id, {"difficulty":diff, "meeting_size":sz, "topics":ls})