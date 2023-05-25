from multiprocessing import Queue
from collections import deque
from utils import UserGroup
import math

class ImproperQueueException(Exception):
    pass

# Penalty functions: Must accept UserGroup objects & weights, and return a numeric penalty
def meeting_size_penalty(user_x: UserGroup.UserGroup, user_y: UserGroup.UserGroup, weights: dict, maxsize=4):
    full_size = len(user_x.ids) + len(user_y.ids)
    if full_size < min(user_x.attr["meeting_size"], user_y.attr["meeting_size"]):
        return (1 - (weights["meeting_size"] / sum(weights.values())))
    elif full_size > maxsize:
        return 2000000
    else:
        return 1

PENALTIES = [meeting_size_penalty]
def group_matcher(
    users_waiting: deque, groups_waiting: deque, weights:dict,
    compromise_factor: int, match_threshold: float,
    penalities=PENALTIES):
    # Go down the group wait queue

    retry_queue = deque()
    # Rotation 1: Add new users to existing groups
    groups_waiting.append(None)
    while groups_waiting[0] is not None:
        users_waiting.append(None)
        while users_waiting[0] is not None:
            # Score: Direct Comparison + Penalties
            compat_score = UserGroup.compare_groupable(groups_waiting[0], users_waiting[0], weights)
            compat_score *= sum((p(groups_waiting[0], users_waiting[0], weights)) for p in penalities)
            compat_score = max(0, compat_score)
            # Decide whether to merge or not
            if compat_score <= match_threshold:
                parent = groups_waiting.popleft()
                parent.merge(users_waiting.popleft())
                groups_waiting.appendleft(parent)
            users_waiting.rotate(-1)
        users_waiting.popleft() # Removes the sentinel None we placed earlier
        # Decide whether the current group goes to the retry queue
        if len(groups_waiting[0].ids) <= 1:
            retry_queue.append(groups_waiting.popleft())
        else:
            groups_waiting.rotate(-1)
    groups_waiting.popleft() # Removes the other sentinel None we placed even earlier
    groups_waiting.extendleft(users_waiting) # Place the unmatched users at front of group queue
    users_waiting.clear() # Remember to dump the user queue now that we're done with it

    # Rotation 2: Try to merge users that couldn't find a group originally
    retry_queue.append(None)
    while retry_queue[0] is not None:
        not_matched = True
        groups_waiting.append(None)
        while (groups_waiting[0] is not None) and not_matched:
            # Use the original comparison + penalty as a basis
            compat_score = UserGroup.compare_groupable(groups_waiting[0], retry_queue[0], weights)
            compat_score *= sum((p(groups_waiting[0], retry_queue[0], weights)) for p in penalities)
            compat_score = max(0, compat_score)
            # We use a combination of timeout and compromise factor (CF) to artificially lower thresholds
            # The +2/-1 combo works with compromise factor 2 to resemble a natural log curve 
            compromise_coeff = 1 / math.log2((retry_queue[0].timeout / compromise_factor) + 1)
            compat_score *= min(1, compromise_coeff)
            # Decide whether to merge or not
            if compat_score <= match_threshold:
                parent = groups_waiting.popleft()
                parent.merge(retry_queue.popleft())
                groups_waiting.appendleft(parent)
                not_matched = False
            else:
                groups_waiting.rotate(-1)
        # Reset groups_waiting loop by removing the None
        while groups_waiting[0] is not None:
            groups_waiting.rotate(-1)
        groups_waiting.popleft()
        # Re-integrate if a group wasn't found, guarantees an increment on retry_queue
        if not_matched: groups_waiting.appendleft(retry_queue.popleft())
    retry_queue.popleft() # Remove the None we placed at the end of the retry queue
    # retry_queue should be empty, no matter what

    # users_waiting should be empty (& can be discarded), groups_waiting modified
    # Timeout is not incremented here, read-only
    return