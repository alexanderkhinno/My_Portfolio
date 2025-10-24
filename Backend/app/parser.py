import os

def get_output_path(filename):
    """Return full path to backend/output/filename"""
    base_dir = os.path.dirname(__file__)
    output_dir = os.path.join(base_dir, "output")
    return os.path.join(output_dir, filename)

def parse_best_solution(filename="best_solution.txt"):
    """Parse best_solution.txt into a dictionary"""
    filepath = get_output_path(filename)
    result = {}
    with open(filepath) as f:
        for line in f:
            if ":" in line:
                key, val = line.strip().split(":")
                result[key.strip()] = val.strip()
    return result

def parse_profiler_summary(filename="AlexK_profile.txt"):
    """Parse profiler summary"""
    data = []
    with open(filename, "r") as f:
        lines = f.readlines()

    # Skip first 3 lines: total execution time, empty, header
    for line in lines[3:]:
        line = line.strip()
        if not line:
            continue
        # Split by whitespace
        parts = line.split()
        if len(parts) < 4:
            continue
        # The last 3 parts are Calls, Total Time, Avg Time
        func_name = " ".join(parts[:-3])
        try:
            calls = int(parts[-3])
            total_time = float(parts[-2])
            avg_time = float(parts[-1])
            data.append({
                "function": func_name,
                "calls": calls,
                "total_time": total_time,
                "avg_time": avg_time
            })
        except ValueError:
            # skip lines that can't be parsed
            continue
    return data
