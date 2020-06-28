import re

from pysat.formula import CNF
from pysat.solvers import Glucose4, Glucose3, Lingeling, Minisat22, Cadical
from pysat.solvers import Minicard, MinisatGH, Maplesat, MapleChrono, MapleCM

import RuleParser as RuleParser


def bitonic_generator(size, check=False):
    """Translation of https://www.inf.hs-flensburg.de/lang/algorithmen/sortieren/bitonic/oddn.htm
    Generator approach inspired by https://en.wikipedia.org/wiki/Batcher_odd%E2%80%93even_mergesort
    Code by Mateon1"""

    def my_log2(n):  # floor(log2(n))
        assert n >= 1
        if n <= 2: return n - 1
        return my_log2(n >> 1) + 1

    def merge(low, n, d):
        if n > 1:
            m = 1 << my_log2(n - 1)
            for i in range(low, low + n - m):
                yield (True, i, i + m, d) if check else (i, i + m, d)
            for c in merge(low, m, d): yield c
            for c in merge(low + m, n - m, d): yield c

    def sort(low, n, d):
        if n > 1:
            m = n >> 1
            for c in sort(low, m, not d): yield c
            for c in sort(low + m, n - m, d): yield c
            for c in merge(low, n, d): yield c
            if check:
                for i in range(low, low + n - 1):
                    yield False, i + (not d), i + d, None

    return sort(0, size, False)


class Grid:
    def __init__(self):
        self.solver = None
        self.pattern = []  # Pattern from the text file provided
        self.formula = CNF()  # CNF for SAT Solving
        self.cnf_variables = {}  # Variables for the CNF
        self.num_vars = 0  # Number of variables created for the CNF
        self.variables = {}
        self.birth_trans = []
        self.survival_trans = []
        self.neighbourhood = []

        self.UNSAT = False
        self.solution = []

    def get_cell_var(self, t, x, y):
        """Gets the variable number for a cell at generation t, position (x, y)"""
        if type(self.cnf_variables[(t, x, y)]) == int:
            cell = self.cnf_variables[(t, x, y)]
        elif type(self.cnf_variables[(t, x, y)]) == bool:
            cell = self.cnf_variables[(t, x, y)]
        else:
            cell = self.cnf_variables[self.cnf_variables[(t, x, y)]]

        return cell

    def allocate_var(self):
        """Allocates a new variable"""
        self.num_vars += 1
        return self.num_vars

    def load_pattern(self, pattern_file):
        """Loads pattern from the pattern file"""
        file = open(pattern_file, "r")
        pattern = file.readlines()
        file.close()

        self.pattern.append([])
        for i in pattern:
            if i == "\n":
                self.pattern.append([])
            else:
                self.pattern[-1].append([x.replace("\n", "") for x in i.split(" ") if x.replace("\n", "") != ""])

        while [] in self.pattern:  # Remove trailing empty list
            self.pattern.remove([])

    def load_rule(self, rule_file):
        """Loads neighbourhood, birth transition and survival transitions from pattern file"""
        RuleParser.load(rule_file)

        # Neighbour coordinates
        self.neighbourhood = RuleParser.neighbourhood

        for k in RuleParser.rule_string:
            self.survival_trans.append([])
            if "/" in k:  # Check if S/B Notation or B/S Notation
                for i in k.split("/")[0].split(","):
                    if "-" in i:
                        for j in range(int(i.split("-")[0]), int(i.split("-")[1]) + 1):
                            self.survival_trans[-1].append(j)
                    else:
                        self.survival_trans[-1].append(int(i))
            else:
                for i in re.split("[bs]", k)[1].split(","):
                    if "-" in i:
                        for j in range(int(i.split("-")[0]), int(i.split("-")[1]) + 1):
                            self.survival_trans[-1].append(j)
                    else:
                        self.survival_trans[-1].append(int(i))

        for k in RuleParser.rule_string:
            self.birth_trans.append([])
            if "/" in k:  # Check if S/B Notation or B/S Notation
                for i in k.split("/")[1].split(","):
                    if "-" in i:
                        for j in range(int(i.split("-")[0]), int(i.split("-")[1]) + 1):
                            self.birth_trans[-1].append(j)
                    else:
                        self.birth_trans[-1].append(int(i))
            else:
                for i in re.split("[bs]", k)[0].split(","):
                    if "-" in i:
                        for j in range(int(i.split("-")[0]), int(i.split("-")[1]) + 1):
                            self.birth_trans[-1].append(j)
                    else:
                        self.birth_trans[-1].append(int(i))

        # Turn into boolean arrays -> [True, False, True, ...]
        temp_birth_trans = [[True if x in self.birth_trans[y] else False for x in range(len(self.neighbourhood[y]) + 1)]
                            for y in range(len(self.neighbourhood))]
        temp_survival_trans = [
            [True if x in self.survival_trans[y] else False for x in range(len(self.neighbourhood[y]) + 1)]
            for y in range(len(self.neighbourhood))]

        self.birth_trans = temp_birth_trans
        self.survival_trans = temp_survival_trans

    def make_counter(self, lits):
        """Based on code by Mateon1"""
        sorts = [[]]
        for (r, i, j, rev) in bitonic_generator(len(lits), check=True):
            if r is False:
                sorts[-1].append((lits[j], lits[i]))
                self.formula.append([-lits[i], lits[j]])
                continue
            else:
                if sorts[-1]: sorts.append([])

            x, y = lits[i], lits[j]
            if x == y: continue

            a = self.allocate_var()
            b = self.allocate_var()

            self.formula.append([-x, a])
            self.formula.append([-y, a])
            self.formula.append([-b, x])
            self.formula.append([-b, y])
            self.formula.append([-a, x, y])
            self.formula.append([b, -x, -y])
            self.formula.append([-b, a])
            lits[i], lits[j] = (b, a) if rev else (a, b)

        for i in range(len(lits) - 1):
            self.formula.append([lits[i], -lits[i + 1]])

        return lits

    def get_rule_boolean(self, t, x, y):
        """Returns a list of CNF clauses that represent the transition function of that cell"""
        clauses = []

        # Getting the variables for this cell and the next one
        cell = self.get_cell_var(t, x, y)
        next_cell = self.get_cell_var(t + 1, x, y)

        # For alternating rules
        phase = t % len(self.neighbourhood)

        # Getting variables for the cells neighbours
        neighbours = []
        for dx, dy in self.neighbourhood[phase]:
            neighbours.append(self.get_cell_var(t, x + dx, y + dy))

        # Run some function that sorts neighbours
        neighbours = self.make_counter(neighbours)

        # Based on code by Mateon1
        cn = [True] + neighbours
        for i in range(len(neighbours)):
            if i == 0:
                guard = [cn[1]]
            elif i < len(cn) - 1:
                guard = [-cn[i], cn[i + 1]]
            else:
                guard = [-cn[i]]

            vb = self.birth_trans[phase][i]
            vs = self.survival_trans[phase][i]

            clauses.append([vb] + guard + [-next_cell, cell])  # no births => dead cell stays dead
            clauses.append([not vb] + guard + [next_cell, cell])  # birth => dead cell comes alive
            clauses.append([vs] + guard + [-next_cell, -cell])  # no surviving => live cell dies
            clauses.append([not vs] + guard + [next_cell, -cell])  # survive => live cell lives

            # shortcut: (is this even necessary?)
            clauses.append([vb, vs] + guard + [-next_cell])  # neither rule active => cell dead
            clauses.append([not vb, not vs] + guard + [next_cell])  # both rules active => cell lives

        # Filter out all clauses that have a True in them since they are automatically True
        # Filter out all Falses in the clauses since they do not affect it as the clause is a giant OR statement
        new_clauses = []
        for clause in clauses:
            if True in clause: continue
            new_clauses.append([x for x in clause if x != False])

        return new_clauses

    def force_change(self, g1, g2):
        """Adds clauses forcing at least one cell to change between specified generations, method suggested by Macbi
        and Mateon1 """

        clauses = []
        shadow_vars = {}

        # Form a shadow grid that says cell in grid 1 is the same as cell in grid 2
        for i in range(len(self.pattern[0])):
            for j in range(len(self.pattern[0][i])):
                shadow_vars[(i, j)] = self.allocate_var()

                # Represents (A XOR B) XNOR C
                clauses.append([-self.get_cell_var(g1, i, j), -self.get_cell_var(g2, i, j), -shadow_vars[(i, j)]])
                clauses.append([-self.get_cell_var(g1, i, j), self.get_cell_var(g2, i, j), shadow_vars[(i, j)]])
                clauses.append([self.get_cell_var(g1, i, j), -self.get_cell_var(g2, i, j), shadow_vars[(i, j)]])
                clauses.append([self.get_cell_var(g1, i, j), self.get_cell_var(g2, i, j), -shadow_vars[(i, j)]])

        # Force one of the shadow vars to be True
        clause = []
        for var in shadow_vars:
            clause.append(shadow_vars[var])

        clauses.append(clause)
        return clauses

    def set_formula(self, force_change_lst=()):
        """Sets the CNF formula according to the pattern"""
        # First, add variables and constrains based on the pattern provided
        for i in range(len(self.pattern)):
            for j in range(len(self.pattern[i])):
                for k in range(len(self.pattern[i][j])):
                    cell = self.pattern[i][j][k]
                    if cell == "0":
                        var = self.allocate_var()
                        self.formula.append([-var])
                        self.cnf_variables[(i, j, k)] = var
                    elif cell == "1":
                        var = self.allocate_var()
                        self.formula.append([var])
                        self.cnf_variables[(i, j, k)] = var
                    elif cell == "*":
                        self.cnf_variables[(i, j, k)] = self.allocate_var()
                    else:
                        if cell not in self.variables:
                            self.variables[cell] = (i, j, k)
                            self.cnf_variables[(i, j, k)] = self.allocate_var()
                        else:
                            self.cnf_variables[(i, j, k)] = self.cnf_variables[self.variables[cell]]

        nrange = RuleParser.neighbourhood_range
        for i in range(len(self.pattern) - 1):  # Next, apply rule transitions
            for j in range(nrange, len(self.pattern[i]) - nrange):
                for k in range(nrange, len(self.pattern[i][j]) - nrange):
                    for clause in self.get_rule_boolean(i, j, k):
                        self.formula.append(clause)

        # Force at least one cell to be on in the first generation
        clause = []
        for key in self.cnf_variables:
            var = self.get_cell_var(key[0], key[1], key[2])
            if type(var) == int: clause.append(var)  # Check for CNF Literal (int)

        self.formula.append(clause)

        # Force generations to be different
        for i in range(len(force_change_lst)):
            for j in range(i + 1, len(force_change_lst)):
                for clause in self.force_change(force_change_lst[i], force_change_lst[j]):
                    self.formula.append(clause)

    def solve(self, solver_type, previous_solution=None):
        """Runs SAT Solver on the CNF Formula"""

        # Add clause to say that it must differ from the previous solution by at least one cell
        if previous_solution is not None and len(previous_solution) != 0:
            clause = []
            for i in previous_solution:
                clause.append(-i)

            self.solver.add_clause(clause)

            # Start solving
            if not self.solver.solve():
                self.UNSAT = True
            else:
                self.UNSAT = False  # Get solution
                self.solution = self.solver.get_model()
        else:
            # Make it case insensitive
            solver_type = solver_type.lower()

            # Check which solver to use
            if solver_type == "glucose4" or solver_type == "glucose" or solver_type == "g4" or solver_type == "g":
                self.solver = Glucose4(bootstrap_with=self.formula.clauses, with_proof=True)
            elif solver_type == "glucose3" or solver_type == "g3":
                self.solver = Glucose3(bootstrap_with=self.formula.clauses, with_proof=True)
            elif solver_type == "lingeling":
                self.solver = Lingeling(bootstrap_with=self.formula.clauses, with_proof=True)
            elif solver_type == "minisat22" or solver_type == "minisat":
                self.solver = Minisat22(bootstrap_with=self.formula.clauses)
            elif solver_type == "cadical":
                self.solver = Cadical(bootstrap_with=self.formula.clauses)
            elif solver_type == "minisatgithub" or solver_type == "minisatgh":
                self.solver = MinisatGH(bootstrap_with=self.formula.clauses)
            elif solver_type == "minicard":
                self.solver = Minicard(bootstrap_with=self.formula.clauses)
            elif solver_type == "maplesat":
                self.solver = Maplesat(bootstrap_with=self.formula.clauses)
            elif solver_type == "maplechrono":
                self.solver = MapleChrono(bootstrap_with=self.formula.clauses)
            elif solver_type == "maplecm":
                self.solver = MapleCM(bootstrap_with=self.formula.clauses)
            else:  # Default to Glucose4
                print(f"WARNING: {solver_type} not a valid / supported SAT solver, defaulting to Glucose4.")
                self.solver = Glucose4(bootstrap_with=self.formula.clauses, with_proof=True)

            # Start solving
            if not self.solver.solve():
                self.UNSAT = True
            else:
                self.UNSAT = False  # Get solution
                self.solution = self.solver.get_model()

    def to_rle(self):
        """Converts solution to RLE"""
        rle_header = f"x = {len(self.pattern[0][0])}, y = {len(self.pattern[0])}, rule = {RuleParser.rule_name}\n"
        rle = ""
        for g in range(1):
            for i in range(len(self.pattern[0])):
                for j in range(len(self.pattern[0][0])):
                    # Get the variable number of that cell
                    if type(self.cnf_variables[(g, i, j)]) == int:
                        index = self.cnf_variables[(g, i, j)]
                    else:
                        index = self.cnf_variables[self.cnf_variables[(g, i, j)]]

                    # Get value of that cell
                    rle += "o" if index in self.solution else "."
                rle += "$\n"
            rle += "!\n"

        return rle_header + rle
