import argparse
import time

import rule_parser
from pattern_gen import ship_search
from sat_grid import Grid

# Help ()
description = """Welcome to Logic Cellular Automaton Search (LCAS)! LCAS converts your CA rule into a SAT problem 
which is fed into a SAT solver to be solved. LCAS uses PySAT, go to their github page to see what SAT solvers are 
supported. LCAS currently supports Weighted Alternating Higher Range Outer-Totalistic (HROT) Rules. Support for 
partial, isotropic non-totalistic and multi-state Rules is planned. The pattern format is the same as LLS ( 
but don't use commas or multiple whitespaces, the parsing code is still quite strict). Idea by WildMyron, 
Code is written by Lemon41625 with additional code contributions and debugging help from Mateon1.

Example Usage:
python main.py -p 4 -dx 1 -dy 1 -x 3 -y 3 (c/4d in 3x3 bounding box)
python main.py -p 3 -dx 0 -dy 0 -x 6 -y 6 -fc 0,1 (P3 Oscillator in 6x6 bounding box)"""

# Initiate the parser
parser = argparse.ArgumentParser(description=description)
parser.add_argument("-p", "--period", help="Period of the spaceship / oscillator", default=4)
parser.add_argument("-dx", "--displace_x", help="Displacement in the x-dir (0 if oscillator)", default=1)
parser.add_argument("-dy", "--displace_y", help="Displacement in the y-dir (0 if oscillator)", default=1)
parser.add_argument("-x", "--bound_x", help="Length of the bounding box of the object", default=3)
parser.add_argument("-y", "--bound_y", help="Height of the bounding box of the object", default=3)
parser.add_argument("-sym", "--symmetry", help="Symmetry of the pattern. These symmetries [C1, D2|, D2-] are "
                                               "currently supported.", default="C1")
parser.add_argument("-trans", "--transform", help="Transformation of the pattern. The transforms [Id, Flip|] are "
                                                  "currently supported", default="Id")
parser.add_argument("-n", "--num_solutions", help="Number of solution you want to find. (default: 1)", default=1)
parser.add_argument("-fc", "--force_change", help="Force the pattern to be different in the specified generations, "
                                                  "helps to prevent finding subperiods and still lives")
parser.add_argument("-pt", "--pattern", help="Pattern file, LLS format (if specified overwrites the automatically "
                                             "generated one)")
parser.add_argument("-r", "--rule", help="Rule file, CAViewer format (default: rule.ca_rule)", default="rule.ca_rule")
parser.add_argument("-s", "--solver", help="SAT solver (default: cadical)", default="cadical")

args = parser.parse_args()

# Generate pattern
rule_parser.load(args.rule)

if args.pattern is None:
    ship_search(int(args.period), int(args.bound_x), int(args.bound_y), int(args.displace_x), int(args.displace_y),
                args.symmetry, args.transform, rule_parser.neighbourhood_range * 2, "pattern.txt")

force_change = [int(x) for x in args.force_change.split(",")] if args.force_change is not None else ()

grid = Grid()

print(f"Loading {'pattern.txt' if args.pattern is None else args.pattern} and {args.rule}...")
grid.load_pattern("pattern.txt" if args.pattern is None else args.pattern)
grid.load_rule(args.rule)

print("Running setup...")
grid.set_formula(force_change_lst=force_change)

# Start solving
for i in range(int(args.num_solutions)):
    print(f"Starting search for solution {i}...\n")

    start_time = time.time()
    grid.solve(args.solver, previous_solution=grid.solution)

    if grid.UNSAT:
        print(f"\nSolver returned UNSAT, took {time.time() - start_time}s")
        print("===========================================")
        # print(grid.solution)
        break
    else:
        print(f"\nSOLUTION FOUND, took {time.time() - start_time}s")
        print("===========================================")
        print(grid.to_rle())
