import re


def get_outer_totalistic_trans(rulestring):
    """Gets transitions for outer totalistic rule"""
    transitions = []
    for i in rulestring.split(","):
        if "-" in i:
            for j in range(int(i.split("-")[0]), int(i.split("-")[1]) + 1):
                transitions.append(j)
        else:
            transitions.append(int(i))

    return transitions


def outer_totalistic_gen(rulestrings):
    birth, survival = [], []
    for rulestring in rulestrings:
        if "/" in rulestring:  # Check if S/B Notation or B/S Notation
            birth.append(get_outer_totalistic_trans(rulestring.split("/")[1]))
        else:
            birth.append(get_outer_totalistic_trans(re.split("[bs]", rulestring)[0]))

    for rulestring in rulestrings:
        if "/" in rulestring:  # Check if S/B Notation or B/S Notation
            survival.append(get_outer_totalistic_trans(rulestring.split("/")[0]))
        else:
            survival.append(get_outer_totalistic_trans(re.split("[bs]", rulestring)[1]))

    return birth, survival
