"""
File: evo_p.py
Description: An evolutionary computing framework for solving
multi-objective optimization problems.

Finds pareto-optimal solutions revealing tradeoffs between different
objectives

"""

import random as rnd
import copy
import numpy as np
import pandas as pd
from functools import reduce
import pickle
import time
import os

def get_output_path(filename):
    """Return full path to backend/output/filename and create folder if needed."""
    base_dir = os.path.dirname(__file__)
    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, filename)

class Evo:

    def __init__(self):
        """ Constructor """
        self.pop = {}  # scores (tuple) --> solution
        self.objectives = {}  # name --> obj function (goals)
        self.agents = {}  # agents: name -> (operator, num_solutions_input)

    def add_objective(self, name, f):
        """ Register an objective (fitness function) to the framework """
        self.objectives[name] = f

    def add_agent(self, name, op, k=1):
        """ Register a named agent with to the framework
        the operatr (op) defines what the agent does - how it changes the solution
        the k value is the number of INPUT solutions from the current population """
        self.agents[name] = (op, k)

    def get_random_solutions(self, k=1):
        if len(self.pop) == 0:
            return []
        else:
            all_solutions = list(self.pop.values())
            return [copy.deepcopy(rnd.choice(all_solutions)) for _ in range(k)]

    def add_solution(self, sol):
        """ Key: ((obj1, score1), (obj2, score2), ... (objn, scoren)) """
        scores = tuple([(name, f(sol)) for name, f in self.objectives.items()])
        self.pop[scores] = sol

    def run_agent(self, name):
        """ Execute a named agent """
        op, k = self.agents[name]
        picks = self.get_random_solutions(k)
        new_solution = op(picks)
        scores = []
        for obj_name, f in self.objectives.items():
            try:
                score = f(new_solution)
                scores.append((obj_name, score))
            except Exception as e:
                return

        scores_tuple = tuple(scores)

        self.pop[scores_tuple] = new_solution

    @staticmethod
    def dominates(p, q):
        pscores = np.array([score for name, score in p])
        qscores = np.array([score for name, score in q])
        score_diffs = qscores - pscores
        return min(score_diffs) >= 0 and max(score_diffs) > 0

    @staticmethod
    def reduce_nds(S, p):
        return S - {q for q in S if Evo.dominates(p, q)}

    def remove_dominated(self):
        nds = reduce(Evo.reduce_nds, self.pop.keys(), self.pop.keys())
        self.pop = {k: self.pop[k] for k in nds}

    def evolve(self, n=1, dom=100, sync=1000, time_limit=None):
        """ Run n invocations of agents with optional time limit (in seconds) """
        start_time = time.time()
        agent_names = list(self.agents.keys())

        i = 0
        while i < n:
            # Check time limit
            if time_limit and (time.time() - start_time) > time_limit:
                print(f"Time limit of {time_limit}s reached after {i} iterations")
                break

            pick = rnd.choice(agent_names)
            self.run_agent(pick)

            if i % sync == 0:
                # merge saved solutions into the population
                try:
                    with open('solutions.dat', 'rb') as file:
                        loaded = pickle.load(file)
                        for eval, sol in loaded.items():
                            self.pop[eval] = sol
                except Exception as e:
                    pass  # File might not exist on first run

                # removing dominated solutions
                self.remove_dominated()


                with open('solutions.dat', 'wb') as file:
                    pickle.dump(self.pop, file)

            if i % dom == 0:
                self.remove_dominated()
                elapsed = time.time() - start_time
                print(f"Generation {i}: Population size = {len(self.pop)}, Elapsed time = {elapsed:.1f}s")

            i += 1

        self.remove_dominated()
        total_time = time.time() - start_time
        print(f"Evolution completed in {total_time:.2f} seconds with {len(self.pop)} solutions")

    def summarize(self, group_name="AlexK"):
        """Convert population to summary table format for CSV output"""
        summary_data = []

        for scores, solution in self.pop.items():

            score_dict = dict(scores)

            row = {
                'groupname': group_name,
                'overallocation': score_dict.get('overallocation', 0),
                'conflicts': score_dict.get('conflicts', 0),
                'undersupport': score_dict.get('undersupport', 0),
                'unavailable': score_dict.get('unavailable', 0),
                'unpreferred': score_dict.get('unpreferred', 0)
            }
            summary_data.append(row)

        return pd.DataFrame(summary_data)

    def save_summary(self, filename, group_name="AlexK"):
        """Save summary to CSV file in the required format"""
        df = self.summarize(group_name)
        path = get_output_path(filename)
        df.to_csv(path, index=False)
        return df

    def __str__(self):
        """ Displaying the contents of the population """
        rslt = f"Population size: {len(self.pop)}\n"
        rslt += "=" * 50 + "\n"

        count = 0
        for scores, sol in self.pop.items():
            if count >= 5:  # Only show first 5 solutions
                rslt += f"... and {len(self.pop) - 5} more solutions\n"
                break
            rslt += str(dict(scores)) + "\n"
            count += 1

        return rslt


