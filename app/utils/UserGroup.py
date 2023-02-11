from copy import deepcopy

class DuplicateUserException(Exception):
    pass

class UserGroup:
    users = set()

    def __init__(self, slack_id, att_dict):
        if slack_id in UserGroup.users: raise DuplicateUserException
        UserGroup.users.add(slack_id)
        self.ids = [slack_id]
        self.attr = deepcopy(att_dict)
        self.timeout = 1

    def expire(self):
        for id in self.ids:
            UserGroup.users.remove(id)
    
    def merge(self, other):
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

# Compatibility Rating
def compare_groupable(user_x, user_y, weights):
    '''
    Create a compatbility rating between two users, two groups, or a user and a group
    Larger score is a worse score, you can think of it as the distance between two points
    :param user_x: A dictionary representing the desired group attributes
                   Two types of entries: String => Numeric & String => {String => Numeric}
    :param user_y: The user to compare to, follows a similar form
    :param weights: A dictionary that weighs the attributes, direct multiplication
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
        atts = list(set(user_x.keys()) & set(user_y.keys()))
        for att in atts:
            # Use the weights to control how the error contributes to the net error
            if isinstance(user_x[att], dict):
                # Assume that the sum of a single dictionary's values is 1, i.e. floats
                fields = list(set(user_x[att].keys()) & set(user_y[att].keys()))
                dict_score = 2 - sum((user_x[att][field] + user_y[att][field] for field in fields))
                error_score += weights[att] * (dict_score)
            else:
                # Assume the internal dictionary is Key => Numeric
                error_score += weights[att] * (abs(user_x[att] - user_y[att]) if user_x[att] * user_y[att] != 0 else 0)
        return error_score
    except AttributeError:
        # logger.error("Attribute mismatch when comparing " + str(user_x) + " and " + str(user_y))
        return 2000000 # Some arbitarily high number
    except TypeError:
        # logger.error("Attribute values are not compatible when comparing " + str(user_x) + " and " + str(user_y))
        return 2000000 # Some arbitrarily high number