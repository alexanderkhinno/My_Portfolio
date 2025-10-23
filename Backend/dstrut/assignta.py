
from dstrut.evo_p import Evo
from dstrut.profiler import build_profiles, profile, profiler
import numpy as np
import random
import time
from dstrut.evo_p import get_output_path


@profile
def overallocation(solution, tas):
    """ Counts the overallocation of each TA"""
    assigned = solution.sum(axis=1) # array summing all the ta's/cols
    max_allowed = np.array([ta.max_assigned for ta in tas]) # extracts max from each ta object in list
    overallocations = np.maximum(0, assigned - max_allowed) # removes underallocations

    return int(overallocations.sum())

@profile
def conflicts(solution, sections):
    """ Check for time conflicts"""

    ta_assignments = {}

    for ta_id in range(solution.shape[0]):
        for section_id in range(solution.shape[1]):
            if solution[ta_id][section_id] == 1:
                if ta_id not in ta_assignments:
                    ta_assignments[ta_id] = []
                ta_assignments[ta_id].append(section_id)

    conflict_count = 0

    for ta_id, assigned_sections in ta_assignments.items():
        if len(assigned_sections) <= 1:
            continue

        has_conflict = False
        for i in range(len(assigned_sections)):
            for j in range(i + 1, len(assigned_sections)):
                section1_id = assigned_sections[i]
                section2_id = assigned_sections[j]

                time1 = sections[section1_id].daytime
                time2 = sections[section2_id].daytime

                if time1 == time2:
                    has_conflict = True
                    break
            if has_conflict:
                break

        if has_conflict:
            conflict_count += 1

    return conflict_count

@profile
def undersupport(solution, sections):
    """ Ensure there is enough TA's per class"""
    per_class = solution.sum(axis=0)
    min_class = np.array([section.min_ta for section in sections])
    support = np.maximum(0, min_class - per_class)

    return int(support.sum())

@profile
def unavailable(solution, tas):
    """ Checks for TA availability"""
    unavailable_set = set()
    for ta_idx, ta in enumerate(tas):
        for section_id, preference in ta.preferences.items():
            if preference == 'U':
                unavailable_set.add((ta_idx, int(section_id)))

    assigned_tas, assigned_sections = np.where(solution == 1)

    violations = 0
    for ta_idx, section_idx in zip(assigned_tas, assigned_sections):
        if (ta_idx, section_idx) in unavailable_set:
            violations += 1

    return violations

@profile
def unpreferred(solution, tas):
    """ Checks for TA willing to but not wanting to"""
    unpreferred_set = set()
    for ta_idx, ta in enumerate(tas):
        for section_id, preference in ta.preferences.items():
            if preference == 'W':
                unpreferred_set.add((ta_idx, int(section_id)))

    assigned_tas, assigned_sections = np.where(solution == 1)

    violations = 0
    for ta_idx, section_idx in zip(assigned_tas, assigned_sections):
        if (ta_idx, section_idx) in unpreferred_set:
            violations += 1

    return violations


@profile
def random_solution_agent(solutions):
    """Generate a completely random solution"""
    return np.random.randint(0, 2, size=(40, 17))


@profile
def swap_assignment_agent(solutions):
    """Randomly swap some TA assignments"""
    if not solutions:
        return random_solution_agent([])

    solution = solutions[0].copy()

    num_swaps = random.randint(1, 10)

    for _ in range(num_swaps):
        ta = random.randint(0, 39)
        section = random.randint(0, 16)
        solution[ta][section] = 1 - solution[ta][section]

    return solution


@profile
def conflict_reduction_agent(solutions):
    """Try to reduce conflicts by removing some assignments from overloaded TAs"""
    if not solutions:
        return random_solution_agent([])

    solution = solutions[0].copy()

    for ta in range(40):
        assigned_sections = np.where(solution[ta] == 1)[0]
        if len(assigned_sections) > 2:
            sections_to_remove = random.sample(
                list(assigned_sections),
                random.randint(1, min(3, len(assigned_sections) - 1))
            )
            for section in sections_to_remove:
                solution[ta][section] = 0

    return solution


@profile
def workload_balancing_agent(solutions):
    """Try to balance workloads by redistributing assignments"""
    if not solutions:
        return random_solution_agent([])

    solution = solutions[0].copy()

    workloads = solution.sum(axis=1)
    overloaded = np.where(workloads > 3)[0]
    underloaded = np.where(workloads < 2)[0]

    if len(overloaded) > 0 and len(underloaded) > 0:
        for _ in range(min(5, len(overloaded))):
            from_ta = random.choice(overloaded)
            to_ta = random.choice(underloaded)

            assigned_sections = np.where(solution[from_ta] == 1)[0]
            if len(assigned_sections) > 0:
                section = random.choice(assigned_sections)
                solution[from_ta][section] = 0
                solution[to_ta][section] = 1

    return solution


@profile
def section_coverage_agent(solutions):
    """Try to ensure all sections have adequate coverage"""
    if not solutions:
        return random_solution_agent([])

    solution = solutions[0].copy()

    section_coverage = solution.sum(axis=0)
    low_coverage_sections = np.where(section_coverage < 2)[0]

    for section in low_coverage_sections:
        available_tas = np.where(solution[:, section] == 0)[0]
        if len(available_tas) > 0:
            tas_to_assign = random.sample(
                list(available_tas),
                min(random.randint(1, 2), len(available_tas))
            )
            for ta in tas_to_assign:
                solution[ta][section] = 1

    return solution


@profile
def crossover_agent(solutions):
    """Combine two solutions to create a new one"""
    if len(solutions) < 2:
        return random_solution_agent([])

    parent1, parent2 = solutions[0], solutions[1]
    child = parent1.copy()

    for ta in range(40):
        if random.random() < 0.5:
            child[ta] = parent2[ta].copy()

    return child


@profile
def mutation_agent(solutions):
    """Apply small random mutations to a solution"""
    if not solutions:
        return random_solution_agent([])

    solution = solutions[0].copy()

    num_mutations = random.randint(1, 5)

    for _ in range(num_mutations):
        ta = random.randint(0, 39)
        section = random.randint(0, 16)
        if random.random() < 0.5:
            solution[ta][section] = 1 - solution[ta][section]

    return solution


@profile
def constraint_repair_agent(solutions):
    """Try to repair constraint violations"""
    if not solutions:
        return random_solution_agent([])

    solution = solutions[0].copy()

    for ta in range(40):
        assigned_sections = np.where(solution[ta] == 1)[0]
        if len(assigned_sections) > 4:
            excess = len(assigned_sections) - 4
            sections_to_remove = random.sample(list(assigned_sections), excess)
            for section in sections_to_remove:
                solution[ta][section] = 0

    return solution


def main():
    """Main optimization function"""

    profiler.start_profiling()

    print("Loading data...")
    sections, tas = build_profiles("assignta_data/sections.csv", "assignta_data/tas.csv")
    print(f"Loaded {len(sections)} sections and {len(tas)} TAs")

    E = Evo()

    # objectives
    E.add_objective("overallocation", lambda sol: overallocation(sol, tas))
    E.add_objective("conflicts", lambda sol: conflicts(sol, sections))
    E.add_objective("undersupport", lambda sol: undersupport(sol, sections))
    E.add_objective("unavailable", lambda sol: unavailable(sol, tas))
    E.add_objective("unpreferred", lambda sol: unpreferred(sol, tas))

    # agents
    E.add_agent("random_solution", random_solution_agent, 0)
    E.add_agent("swap_assignment", swap_assignment_agent, 1)
    E.add_agent("conflict_reduction", conflict_reduction_agent, 1)
    E.add_agent("workload_balancing", workload_balancing_agent, 1)
    E.add_agent("section_coverage", section_coverage_agent, 1)
    E.add_agent("crossover", crossover_agent, 2)
    E.add_agent("mutation", mutation_agent, 1)
    E.add_agent("constraint_repair", constraint_repair_agent, 1)

    # Seed with some initial solutions
    for _ in range(20):
        E.add_solution(np.random.randint(0, 2, size=(40, 17)))

    print(f"Initial population: {len(E.pop)} solutions")

    # starting the optomization
    start_time = time.time()
    E.evolve(n=1000000, dom=50, sync=999999, time_limit=15)
    end_time = time.time()

    optimization_time = end_time - start_time
    print(f"\nOptimization completed in {optimization_time:.2f} seconds")
    print(f"Final population size: {len(E.pop)} non-dominated solutions")

    # Stop profiling
    profiler.stop_profiling()


    summary_df = E.save_summary("AlexK_summary.csv")
    profiler.save_report("AlexK_profile.txt")

    best_solution_path = get_output_path("best_solution.txt")

    # Calculate total penalty for each solution
    summary_df['total_penalty'] = (summary_df['overallocation'] +
                                   summary_df['conflicts'] +
                                   summary_df['undersupport'] +
                                   summary_df['unavailable'] +
                                   summary_df['unpreferred'])

    # Find best solution (lowest total penalty)
    best_idx = summary_df['total_penalty'].idxmin()
    best_solution = summary_df.iloc[best_idx]

    # Save best solution justification
    with open(best_solution_path, "w") as f:

        f.write(f"Overallocation: {best_solution['overallocation']}\n")
        f.write(f"Conflicts: {best_solution['conflicts']}\n")
        f.write(f"Undersupport: {best_solution['undersupport']}\n")
        f.write(f"Unavailable: {best_solution['unavailable']}\n")
        f.write(f"Unpreferred: {best_solution['unpreferred']}\n")
        f.write(f"Total Penalty: {best_solution['total_penalty']}\n\n")

    # Display final summary

    print(f"Optimization time: {optimization_time:.2f} seconds")
    for obj in ['overallocation', 'conflicts', 'undersupport', 'unavailable', 'unpreferred']:
        min_val = summary_df[obj].min()
        max_val = summary_df[obj].max()
        print(f"  {obj}: {min_val} - {max_val}")

main()