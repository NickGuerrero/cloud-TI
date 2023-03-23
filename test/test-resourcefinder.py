# Install files from the main application, using the .env file
import sys
import os
from dotenv import load_dotenv
load_dotenv()
locs = os.getenv("testfiles").split(",")
for loc in locs:
    sys.path.append(loc)

# Install necessary libraries
from utils import ResourceFinder
import unittest
sql_script = os.getenv("databasescriptpath")

# Note that the function has randomness (non-deterministic)
# Expect possible variations in tests, be careful with how tests are written

class TestResourceFinderBasic(unittest.TestCase):
    def test_basic(self):
        db_conn = ResourceFinder.create_temporary_database(sql_script)
        try:
            # Check that connection can properly execute queries
            attributes = {"difficulty": 1, "topics": {"string": 0.5, "array": 0.5}}
            problems = ResourceFinder.suggest_resource(db_conn, attributes)
            self.assertTrue(len(problems) == 3)
            
            # Check that the problems retireved provide valid data
            EXPECTED_ATTR = {"link", "title", "difficulty", "tags"}
            for prob in problems:
                self.assertTrue(len(set(prob.keys()).intersection(EXPECTED_ATTR)) == len(EXPECTED_ATTR))
                self.assertTrue(len(prob["link"]) >= 0)
                self.assertTrue(len(prob["title"]) >= 0)
                self.assertTrue(prob["difficulty"] in {1,2,3})
        finally:
            db_conn.close()

if __name__ == "__main__":
    unittest.main()
    print("All tests passed")