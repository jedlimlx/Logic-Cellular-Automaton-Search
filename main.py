import argparse
import time

import RuleParser
from pattern_gen import ship_search
from sat_grid import Grid

# Help ()
description = """Welcome to Logic Cellular Automaton Search (LCAS)! LCAS converts your CA rule into a SAT problem 
which is fed into a SAT solver to be solved. LCAS uses PySAT, go to their github page to see what SAT solvers are 
supported. LCAS currently supports Weighted Alternating Higher Range Outer-Totalistic (HROT) Rules. Support for 
partial, isotropic non-totalistic and multi-state Rules is planned. When searching for oscillator, you are likely to 
find sub-periods and even still-lifes! This will be fixed in a future update. The pattern format is the same as LLS ( 
but don't use commas or multiple whitespaces, the parsing code is still quite strict). Idea by WildMyron, 
Code is written by Lemon41625 with additional code contributions and debugging help from Mateon1.

Example Usage: 
python main.py -p 4 -dx 1 -dy 1 -x 3 -y 3 (finds glider if Life is loaded)"""

# Initiate the parser
parser = argparse.ArgumentParser(description=description)
parser.add_argument("-p", "--period", help="Period of the spaceship / oscillator", default=4)
parser.add_argument("-dx", "--displace_x", help="Displacement in the x-dir (0 if oscillator)", default=1)
parser.add_argument("-dy", "--displace_y", help="Displacement in the y-dir (0 if oscillator)", default=1)
parser.add_argument("-x", "--bound_x", help="Length of the bounding box of the object", default=3)
parser.add_argument("-y", "--bound_y", help="Height of the bounding box of the object", default=3)
parser.add_argument("-sym", "--symmetry", help="Symmetry of the pattern. These symmetries [C1] are "
                                               "currently supported.")
parser.add_argument("-pt", "--pattern", help="Pattern file, LLS format (if specified overwrites the automatically "
                                             "generated one)")
parser.add_argument("-r", "--rule", help="Rule file, CAViewer format (default: rule.ca_rule)", default="rule.ca_rule")
parser.add_argument("-s", "--solver", help="SAT solver (default: minisat)", default="minisat")

args = parser.parse_args()

# Generate pattern
RuleParser.load(args.rule)

if args.pattern is None:
    ship_search(int(args.period), int(args.bound_x), int(args.bound_y), int(args.displace_x), int(args.displace_y),
                args.symmetry, RuleParser.neighbourhood_range * 2, "pattern.txt")

grid = Grid()

print(f"Loading {'pattern.txt' if args.pattern is None else args.pattern} and {args.rule}...")
grid.load_pattern("pattern.txt" if args.pattern is None else args.pattern)
grid.load_rule(args.rule)

print("Running setup...")
grid.set_formula()

# Start solving
print("Starting search...\n")
start_time = time.time()
grid.solve(args.solver)

if grid.UNSAT:
    print(f"\nSolver returned UNSAT, took {time.time() - start_time}s")
    print("===========================================")
    print(grid.solution)
else:
    print(f"\nSOLUTION FOUND, took {time.time() - start_time}s")
    print("===========================================")
    print(grid.to_rle())
