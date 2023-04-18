import re
import math
import heapq
import sqlite3

def create_temporary_database(sql_script_path, db_path=":memory:"):
    '''
    Create a fresh resource database, default to a private in-memory
    Since there's no interface to update the database right now, it'll be
    recereated whenever changes are needed. The database should be able to persist
    between instance launches, and deleted when new data is needed.

    :param db_path: A filepath string to the database file (should be resource.db)
    :param sql_script_path: A filepath string to the sql script for making the database
    :return: sqlite3 connection object to the completed database
    '''
    db_connection = sqlite3.connect(db_path)
    sql_script = open(sql_script_path, 'r')
    sql_reader = sql_script.read()
    db_connection.executescript(sql_reader)
    sql_script.close()
    return db_connection

def create_problem_set(res):
    '''
    Fetch rows from a query result and return them as dictionaries w/ the following
    {
        "link": External link to the problem/resource
        "title": Title of the resource/problem
        "difficulty": Numeric difficulty rating (1 for easy, 2 for medium, 3 for hard)
        "tags": Set of strings, each representing a unique tag associated with the problem
    }
    Expected row placements from query result: (pid, link, title, difficulty, tid, tag_name)

    :return: A list of dictionaries with the above format
    '''
    sql_listing = res.fetchall()
    output = {}
    # Condense the entry tags (from the natural join with the tag table)
    for entry in sql_listing:
        if entry in output:
            output[entry[1]]["tags"].add(str(entry[5]))
        else:
            output[entry[1]] = {"link": str(entry[1]), "title": str(entry[2]), "difficulty": entry[3], "tags": set([str(entry[5])])}
    return list(output.values())

# Relevant Attribute Keys = ["topics", "difficulty"]
def suggest_resource(db_connection, group_attr, PROBLEMS=3):
    '''
    Provide problem suggestions with the given sqlite3 database and group preferences
    Algorithm runs two queries, difficulty-based and tag-based, choose best of PROBLEMS

    :param db_connection: A valid sqlite3 database connection
    :param group_attr: A dictionary with the group attributes for recommendation
        {
            "difficulty": Numeric score corresponding to difficulty
            "topics": A dicionary of String=>Numeric values that correlate to topic weight
        }
    :param PROBLEMS: The number of problems to fetch, max 10
    :return: A list of diciontaries containing problem attributes
        {
            "link": External link to the problem/resource
            "title": Title of the resource/problem
            "difficulty": Numeric difficulty rating (1 for easy, 2 for medium, 3 for hard)
            "tags": Set of strings, each representing a unique tag associated with the problem
        }
    '''
    # DB Connection
    cur = db_connection.cursor()

    # Convert group into values for queries + create the topic set
    query_difficulty = math.ceil(group_attr["difficulty"] - 0.5) # Round half-down to integer
    query_difficulty = max(1, min(3, query_difficulty)) # Ensure integer is between difficulty interval
    query_topic = max(group_attr["topics"]) if len(group_attr["topics"]) > 0 else None
    group_topics = set(group_attr["topics"].keys())
    group_topics.add("any") # Make sure that we won't have 0 denominator

    # Difficulty Query: Get list of 5 possible problems
    diff_query = """
    SELECT * FROM
        (SELECT * FROM
            (SELECT * FROM problems WHERE difficulty = ?)
        ORDER BY random() LIMIT 5)
    NATURAL JOIN taggings NATURAL JOIN tags;
    """
    diff_query = re.sub(r'\s+', ' ', diff_query).strip()
    diff_list = create_problem_set(cur.execute(diff_query, (query_difficulty,)))

    # Tag Query: Get a list of 5 possible problems
    tag_query = """
    SELECT * FROM
        (SELECT * FROM problems
        WHERE pid IN
            (SELECT pid FROM
                (SELECT * FROM tags NATURAL JOIN taggings)
            WHERE tag_name = ? ORDER BY random() LIMIT 5))
    NATURAL JOIN taggings NATURAL JOIN tags
    """
    tag_query = re.sub(r'\s+', ' ', tag_query).strip()
    if query_topic is not None:
        tag_list = create_problem_set(cur.execute(tag_query, (query_topic,)))
        diff_list.extend(tag_list)

    # Rank the problems, comparing to the group attributes
    problem_list = []       # Min-heap for ranking the problem choices
    name_set = set()        # Ensure that there aren't problem duplicates across 2 queries
    value_set = set()       # Ensure that there aren't value duplicates for proper heapq implementation
    DELTA = 0.0005          # Used to solve value duplicate issues
    for prob in diff_list:
        if prob["link"] not in name_set:
            # Error uses difficulty as a base, and the topic difference as a coefficient to scale down
            cur_error = abs(group_attr["difficulty"] - prob["difficulty"]) + 1
            cur_error *= 1 - (len(group_topics.intersection(prob["tags"])) / len(group_topics))
            # Prevent duplicate errors with heapq
            while cur_error in value_set:
                cur_error += DELTA
            value_set.add(cur_error)
            name_set.add(prob["link"])
            heapq.heappush(problem_list, (cur_error, prob))
    # Remove the ranking number, the output is just the problem data
    return [x[1] for x in heapq.nsmallest(PROBLEMS, problem_list)]