"""
Author: Alex Khinno
Filename: Profiler.py
Enhanced with timing profiler functionality
"""

import pandas as pd
import time
from functools import wraps
from collections import defaultdict
from dstrut.evo_p import get_output_path

class Section:
    def __init__(self, section_id, instructor, daytime, location, students, topic, min_ta, max_ta):
        self.section_id = section_id
        self.instructor = instructor
        self.daytime = daytime
        self.location = location
        self.students = int(students)
        self.topic = topic
        self.min_ta = int(min_ta)
        self.max_ta = int(max_ta)

class TA:
    def __init__(self, ta_id, name, max_assigned, preferences):
        self.ta_id = int(ta_id)
        self.name = name
        self.max_assigned = int(max_assigned)
        self.preferences = preferences

class Profiler:
    """Simple profiler to track function calls and execution times"""

    def __init__(self):
        self.call_counts = defaultdict(int)
        self.total_times = defaultdict(float)
        self.start_time = None
        self.end_time = None

    def start_profiling(self):
        """Start the overall timing"""
        self.start_time = time.time()
        print("Profiling started...")

    def stop_profiling(self):
        """Stop the overall timing"""
        self.end_time = time.time()
        print(f"Profiling stopped. Total time: {self.get_total_time():.2f} seconds")

    def get_total_time(self):
        """Get total execution time"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0

    def profile(self, func):
        """Decorator to profile a function"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()

            func_name = func.__name__
            self.call_counts[func_name] += 1
            self.total_times[func_name] += (end - start)

            return result
        return wrapper

    def report(self):
        """Generate profiling report"""
        print("\n" + "="*50)
        print("PROFILING REPORT")
        print("="*50)
        print(f"Total execution time: {self.get_total_time():.2f} seconds")
        print(f"Time limit check: {'PASS' if self.get_total_time() <= 300 else 'FAIL'} (limit: 300s)")
        print()
        print(f"{'Function':<25} {'Calls':<10} {'Total Time':<12} {'Avg Time':<12}")
        print("-" * 60)

        for func_name in sorted(self.call_counts.keys()):
            calls = self.call_counts[func_name]
            total_time = self.total_times[func_name]
            avg_time = total_time / calls if calls > 0 else 0

            print(f"{func_name:<25} {calls:<10} {total_time:<12.4f} {avg_time:<12.6f}")

        print("="*50)
        return self.get_report_string()

    def get_report_string(self):
        """Get report as string for saving to file"""
        report = []
        report.append(f"Total execution time: {self.get_total_time():.2f} seconds")
        report.append("")
        report.append(f"{'Function':<25} {'Calls':<10} {'Total Time':<12} {'Avg Time':<12}")

        for func_name in sorted(self.call_counts.keys()):
            calls = self.call_counts[func_name]
            total_time = self.total_times[func_name]
            avg_time = total_time / calls if calls > 0 else 0

            report.append(f"{func_name:<25} {calls:<10} {total_time:<12.4f} {avg_time:<12.6f}")
        return "\n".join(report)

    def save_report(self, filename):
        """Save report to file"""
        filepath = get_output_path(filename)
        with open(filepath, 'w') as f:
            f.write(self.get_report_string())

profiler = Profiler()

def profile(func):
    """Decorator function that uses the global profiler instance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()

        func_name = func.__name__
        profiler.call_counts[func_name] += 1
        profiler.total_times[func_name] += (end - start)

        return result
    return wrapper

def load_data(section_directory, ta_directory):
    section = pd.read_csv(section_directory)
    ta = pd.read_csv(ta_directory)
    return section, ta

def build_profiles(section_directory, ta_directory):
    sections_df, tas_df = load_data(section_directory, ta_directory)

    sections = [
        Section(row['section'], row['instructor'], row['daytime'], row['location'],
                row['students'], row['topic'], row['min_ta'], row['max_ta'])
        for _, row in sections_df.iterrows()
    ]

    tas = []
    for _, row in tas_df.iterrows():
        preferences = row[3:].to_dict()
        tas.append(TA(row['ta_id'], row['name'], row['max_assigned'], preferences))

    return sections, tas

def main():
    sections, tas = build_profiles("../assignta_data/sections.csv", "../assignta_data/tas.csv")
    print("Sections Loaded:", len(sections))
    print("TAs Loaded:", len(tas))

if __name__ == "__main__":
    main()