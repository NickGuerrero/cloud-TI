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

# Creating dummy requests
def dummyreq(id_no, diff, meet_size, topic):
    return {"slack_id": id_no, "difficulty": diff, "meeting_size": meet_size, "topics": topic}
# Tag listings useful for using UserGroup Conversion
topic_options = ["top-array", "top-string", "top-sorting", "top-tree", "top-greedy", "top-stack",
                  "top-recursion", "top-math", "top-geometry", "top-divide_and_conquer", "top-any"]
diff_options = ["dif-easy", "dif-medium", "dif-hard"]
size_options = ["siz-small", "siz-medium", "siz-large"]
# Simulate the grouping queue timeout
def update_queue_timeout(group_queue, exit_queue):
    # Simulate the grouper driver that handles timeout
    group_queue.append(None)
    while group_queue[0] is not None:
        if group_queue[0].timeout < 12:
            group_queue[0].step()
            group_queue.rotate(-1)
        else:
            group_queue[0].expire()
            exit_queue.append(group_queue.popleft())
    group_queue.popleft()

# Constants
# TODO: In main application, consider using meeting_size = 3 or 4 to prevent quad only in dense queues (2, 3, 1)
WEIGHTS = {"meeting_size": 6, "difficulty": 4, "topics": 1}

class TestGroupingBasic(unittest.TestCase):
    def test_basic(self):
        '''Test that the grouping function can merge two users together'''
        UserGroup.UserGroup.reset()
        x = UserGroup.convert_to_usergroup(dummyreq("a", "dif-easy", "siz-small", ["top-string", "top-array"]))
        y = UserGroup.convert_to_usergroup(dummyreq("b", "dif-easy", "siz-small", ["top-string", "top-array"]))
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
        self.assertAlmostEqual(group_queue[0].attr["topics"]["string"], 0.5, delta=0.0001)
        self.assertAlmostEqual(group_queue[0].attr["topics"]["array"], 0.5, delta=0.0001)

    def test_basic_mismatch(self):
        '''Test that the grouping function can refuse to merge two users together'''
        UserGroup.UserGroup.reset()
        x = UserGroup.convert_to_usergroup(dummyreq("a", "dif-easy", "siz-small", ["top-string", "top-array"]))
        y = UserGroup.convert_to_usergroup(dummyreq("b", "dif-hard", "siz-large", ["top-tree", "top-recursion"]))
        user_queue = deque([x,y])
        group_queue = deque()
        # Test that users were added to the group queue properly
        QueueGrouper.group_matcher(user_queue, group_queue, WEIGHTS, compromise_factor=2, match_threshold=4)
        self.assertTrue(len(group_queue) == 2)
        self.assertTrue(len(user_queue) == 0)
        # Test that users are not matched on the second iteration
        QueueGrouper.group_matcher(user_queue, group_queue, WEIGHTS, compromise_factor=2, match_threshold=4)
        assert len(group_queue) == 2
    
    def test_match_forgiveness(self):
        '''Test that the grouping function can refuse to merge two users together'''
        UserGroup.UserGroup.reset()
        x = UserGroup.convert_to_usergroup(dummyreq("a", "dif-easy", "siz-small", ["top-string", "top-array"]))
        y = UserGroup.convert_to_usergroup(dummyreq("b", "dif-hard", "siz-large", ["top-recursion", "top-tree"]))
        z = UserGroup.convert_to_usergroup(dummyreq("c", "dif-medium", "siz-medium", ["top-stack", "top-math"]))
        user_queue = deque([x,y,z])
        group_queue = deque()
        # Test that users were added to the group queue properly
        QueueGrouper.group_matcher(user_queue, group_queue, WEIGHTS, compromise_factor=2, match_threshold=4)
        self.assertTrue(len(group_queue) == 3)
        self.assertTrue(len(user_queue) == 0)
        # Test that users are not matched on the second iteration
        QueueGrouper.group_matcher(user_queue, group_queue, WEIGHTS, compromise_factor=2, match_threshold=4)
        self.assertTrue(len(group_queue) == 3)
        # Change the timeouts to test forgiveness
        group_queue[1].timeout = 12
        group_queue[2].timeout = 12
        # Test for forgiveness, a should forgive c but not b
        QueueGrouper.group_matcher(user_queue, group_queue, WEIGHTS, compromise_factor=2, match_threshold=4)
        self.assertTrue(len(group_queue) == 2)
    
    # TODO: Consider changing weights to improve group performance, as well as compromise factor & match forgiveness
    # This test is biased towards forgiveness (one-at-a-time), so it owuld be helpful to write tests to find balance
    def test_many_users_1by1(self):
        '''Test that the algorithm can handle at least 100 users'''
        UserGroup.UserGroup.reset()
        # Generate 100 users on command
        users = (UserGroup.convert_to_usergroup(dummyreq(
            str(x), diff_options[x % 3], size_options[((x // 3) % 3)], [topic_options[x % 10]])
            ) for x in range(100))
        user_queue = deque()
        group_queue = deque()
        exit_queue = deque()
        for user in users:
            user_queue.append(user)
            QueueGrouper.group_matcher(user_queue, group_queue, WEIGHTS, compromise_factor=2, match_threshold=3) # MT = 4
            # Simulate the grouper driver that handles timeout
            update_queue_timeout(group_queue, exit_queue)
        for i in range(12):
            QueueGrouper.group_matcher(user_queue, group_queue, WEIGHTS, compromise_factor=2, match_threshold=3) # MT = 4
            # Simulate the grouper driver that handles timeout
            update_queue_timeout(group_queue, exit_queue)
        # Check the number of successful group matches
        fail = 0
        for grp in exit_queue:
            fail += (len(grp.ids) <= 1)
        self.assertTrue(fail < 10)
        # Checking group formations
        for grp in exit_queue:
            print(grp.ids)
        print(len(exit_queue))
    
    def test_many_users_singlelargequeue(self):
        UserGroup.UserGroup.reset()
        # Generate 100 users on command
        users = (UserGroup.convert_to_usergroup(dummyreq(
            str(x), diff_options[x % 3], size_options[((x // 3) % 3)], [topic_options[x % 10]])
            ) for x in range(100))
        user_queue = deque(users)
        group_queue = deque()
        exit_queue = deque()
        for i in range(24):
            QueueGrouper.group_matcher(user_queue, group_queue, WEIGHTS, compromise_factor=2, match_threshold=3) # MT = 4
            # Simulate the grouper driver that handles timeout
            update_queue_timeout(group_queue, exit_queue)
        # Check the number of successful group matches
        fail = 0
        for grp in exit_queue:
            fail += (len(grp.ids) <= 1)
        self.assertTrue(fail < 10)
        # Checking group formations
        for grp in exit_queue:
            print(grp.ids)
        print(len(exit_queue))

if __name__ == "__main__":
    unittest.main()
    print("All tests passed")