# Install files from the main application, using the .env file
import sys
import os
from dotenv import load_dotenv
load_dotenv()
locs = os.getenv("testfiles").split(",")
for loc in locs:
    sys.path.append(loc)

# Install necessary libraries
from utils import UserGroup, QueueGrouper
from collections import deque
import unittest

def dummyreq(id_no, diff, meet_size, topic):
    return {"slack_id": id_no, "difficulty": diff, "meeting_size": meet_size, "topics": topic}

# Constants
WEIGHTS = {"meeting_size": 2, "difficulty": 3, "topics": 1}

class TestGroupingBasic(unittest.TestCase):
    def tests_runnable(self):
        self.assertTrue(True)

    def test_basic(self):
        '''Test that the grouping function can merge two users together'''
        x = UserGroup.convert_to_usergroup(dummyreq("a", "1", "2", ["m", "n"]))
        y = UserGroup.convert_to_usergroup(dummyreq("b", "1", "2", ["m", "n"]))
        user_queue = deque([x,y])
        group_queue = deque()
        # Test that users were added to the group queue properly
        QueueGrouper.group_matcher(user_queue, group_queue, WEIGHTS, compromise_factor=2, match_threshold=4)
        self.assertTrue(len(group_queue) == 2)
        self.assertTrue(len(user_queue) == 0)
        # Test that users are matched on the second iteration
        QueueGrouper.group_matcher(user_queue, group_queue, WEIGHTS, compromise_factor=2, match_threshold=4)
        assert len(group_queue) == 1
        assert len(group_queue[0].ids) == 2
        # Check that the users merged correctly
        for i in ("a", "b"):
            assert i in group_queue[0].ids
        self.assertTrue(group_queue[0].attr["difficulty"] == 1)
        self.assertTrue(group_queue[0].attr["meeting_size"] == 2)
        self.assertTrue(group_queue[0].attr["topics"]["m"] == 0.5)
        self.assertTrue(group_queue[0].attr["topics"]["n"] == 0.5)

if __name__ == "__main__":
    unittest.main()
    print("All tests passed")