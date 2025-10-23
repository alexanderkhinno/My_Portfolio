import os

def parse_test_profile(filename="test_profile.txt"):
    """Parse test_profile.txt into list of {test, avg_time, calls}"""
    filepath = get_output_path(filename)
    data = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("Function") or line.startswith("="):
                continue
            parts = line.split()
            if len(parts) >= 4:
                func_name = parts[0]
                calls = int(parts[1])
                total_time = float(parts[2])
                avg_time = float(parts[3])
                data.append({
                    "function": func_name,
                    "calls": calls,
                    "total_time": total_time,
                    "avg_time": avg_time
                })
    return data

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

def parse_profiler_summary(filename="profiler_summary.txt", top_n=10):
    """Parse profiler summary and return top N functions by calls"""
    filepath = get_output_path(filename)
    data = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("Function") or line.startswith("="):
                continue
            parts = line.split()
            if len(parts) >= 4:
                func_name = parts[0]
                calls = int(parts[1])
                total_time = float(parts[2])
                avg_time = float(parts[3])
                data.append({
                    "function": func_name,
                    "calls": calls,
                    "total_time": total_time,
                    "avg_time": avg_time
                })
    data = sorted(data, key=lambda x: x["calls"], reverse=True)
    return data[:top_n]
