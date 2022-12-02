import SimpleGrouper
# TODO: Convert application into packages for importing into unit tests

def dummyreq(id_no, meet_type, meet_size, topic):
    return {"slack_id": id_no, "meeting_type": meet_type, "meeting_size": meet_size, "topic": topic}

# TESTING
# TODO: Build proper testing classes
def test_basic():
    grp_no = [2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4]
    met_typ = ["mock_interview" if x < 11 else "group_problem_solving" for x in range(16)]
    x = [dummyreq(id, met_typ[id], grp_no[id], "arrays") for id in range(len(grp_no))]
    # Insert into group function (Use the better grouping system if we have it ready)
    y = SimpleGrouper.simple_group(x)
    # TODO: What do you want the deterministic output to be?

if __name__ == "__main__":
    pass # Tests go here
    print("All tests passed")