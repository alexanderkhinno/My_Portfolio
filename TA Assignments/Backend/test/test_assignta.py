"""

Py test for assignta.py

"""

import numpy as np
from dstrut.profiler import build_profiles, profiler
from dstrut.assignta import overallocation, conflicts, undersupport, unavailable, unpreferred
import time
from dstrut.evo_p import get_output_path

def load_test_solution(filename):
    return np.loadtxt(f"../assignta_data/{filename}", delimiter=",", dtype=int)

def test_test1_scores():
    sol = load_test_solution("test1.csv")
    sections, tas = build_profiles("../assignta_data/sections.csv", "../assignta_data/tas.csv")
    assert overallocation(sol, tas) == 34, "Overallocation wrong"
    assert conflicts(sol, sections) == 7, "Conflict wrong"
    assert undersupport(sol, sections) == 1, "Undersupport wrong"
    assert unavailable(sol, tas) == 59, "Unavailable wrong"
    assert unpreferred(sol, tas) == 10, "Unpreferred wrong"

def test_test2_scores():
    sol = load_test_solution("test2.csv")
    sections, tas = build_profiles("../assignta_data/sections.csv", "../assignta_data/tas.csv")
    assert overallocation(sol, tas) == 37, "Overallocation wrong"
    assert conflicts(sol, sections) == 5, "Conflict wrong"
    assert undersupport(sol, sections) == 0, "Undersupport wrong"
    assert unavailable(sol, tas) == 57, "Unavailable wrong"
    assert unpreferred(sol, tas) == 16, "Unpreferred wrong"

def test_test3_scores():
    sol = load_test_solution("test3.csv")
    sections, tas = build_profiles("../assignta_data/sections.csv", "../assignta_data/tas.csv")
    assert overallocation(sol, tas) == 19, "Overallocation wrong"
    assert conflicts(sol, sections) == 2, "Conflict wrong"
    assert undersupport(sol, sections) == 11, "Undersupport wrong"
    assert unavailable(sol, tas) == 34, "Unavailable wrong"
    assert unpreferred(sol, tas) == 17, "Unpreferred wrong"


def test_profiler():
    """Test the profiler with your objective functions"""

    # Start profiling
    profiler.start_profiling()

    # Load test data
    sections, tas = build_profiles("../assignta_data/sections.csv", "../assignta_data/tas.csv")

    test_solution = np.random.randint(0, 2, size=(40, 17))

    print("Testing profiler with objective functions...")

    for i in range(5):
        print(f"Test iteration {i + 1}")

        over_score = overallocation(test_solution, tas)
        conf_score = conflicts(test_solution, sections)
        under_score = undersupport(test_solution, sections)
        unav_score = unavailable(test_solution, tas)
        unpref_score = unpreferred(test_solution, tas)

        print(
            f"  Scores: over={over_score}, conf={conf_score}, under={under_score}, unav={unav_score}, unpref={unpref_score}")

        # Add a small delay to make timing visible
        time.sleep(0.1)

    # Stop profiling
    profiler.stop_profiling()

    profiler.report()
    profiler.save_report("test_profile.txt")