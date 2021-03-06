import re
from typing import List
import b0_lyser

colour_palette_count: int = 0
colour_palette = []
parsing_colour_palette: bool = False

neighbourhood = []
neighbourhood_weights = []
current_neighbourhood_weights = []
neighbourhood_count: int = 0
neighbourhood_range: int = 0
parsing_neighbourhood: bool = False

n_states: int = 0
rule_name: str = ""
tiling: str = "Square"
bs_conditions: str = "Outer Totalistic"
rulespace: str = "Single State"
rule_string: List[str] = []
state_weights: List[List[int]] = []


def load(filename):
    global colour_palette, colour_palette_count, parsing_colour_palette, \
        rule_name, n_states, state_weights, tiling, parsing_neighbourhood, neighbourhood, neighbourhood_weights, \
        current_neighbourhood_weights, neighbourhood_count, neighbourhood_range, rule_string, rulespace, bs_conditions
    neighbourhood = []
    neighbourhood_weights = []
    current_neighbourhood_weights = []

    file = open(filename, "r")
    rule: str = file.read()
    colour_palette = []

    for section in rule.split("\n"):
        if "Colour Palette:" in section:
            parsing_colour_palette = True
            continue
        elif parsing_colour_palette:
            if "None" in section:
                colour_palette = None
                parsing_colour_palette = False
                continue
            colour_palette.append([int(re.sub("[() ]", "", x)) for x in section.split(",")])
            colour_palette_count += 1
            if colour_palette_count == n_states:
                parsing_colour_palette = False
            continue

        if "Neighbourhood:" in section or "#" in section:
            neighbourhood_count = 0
            parsing_neighbourhood = True
            current_neighbourhood_weights = []
            continue
        elif parsing_neighbourhood:
            current_neighbourhood_weights += [int(x) for x in section.split(",")]
            neighbourhood_count += 1
            if neighbourhood_count == neighbourhood_range * 2 + 1:
                parsing_neighbourhood = False
                neighbourhood_weights.append(current_neighbourhood_weights)
            continue

        if "Name:" in section:
            rule_name = section.replace("Name: ", "")
        elif "State Weights:" in section:
            state_weights = [[int(x) for x in y.split(",")]
                             for y in section.replace("State Weights: ", "").split("|")]
            n_states = len(state_weights[0])
        elif "Tiling:" in section:
            tiling = section.replace("Tiling: ", "")
        elif "Neighbourhood Range:" in section:
            neighbourhood_range = int(section.replace("Neighbourhood Range: ", ""))
        elif "Rulestring:" in section:
            rule_string = [[x.lower() for x in rulestring.split("|")] for rulestring in
                           section.replace("Rulestring: ", "").split(" - ")]
        elif "Rulespace:" in section:
            rulespace = section.replace("Rulespace: ", "")
        elif "B/S Conditions:" in section:
            bs_conditions = section.replace("B/S Conditions: ", "")

    for j in range(len(neighbourhood_weights)):
        neighbourhood.append([])
        for i in range((2 * neighbourhood_range + 1) ** 2):
            for k in range(neighbourhood_weights[j][i]):
                neighbourhood[j].append((i // (2 * neighbourhood_range + 1) - neighbourhood_range,
                                         i % (2 * neighbourhood_range + 1) - neighbourhood_range))

    # Apply B0
    rule_string = [b0_lyser.b0_lyser(x, rulespace, bs_conditions,
                                     [len(y) for y in neighbourhood]) for x in rule_string]

    # Increase size of neighbourhood to match
    if len(rule_string[0]) > len(neighbourhood):
        temp = []
        for i in neighbourhood:
            temp += [i] * 2
        neighbourhood = temp
