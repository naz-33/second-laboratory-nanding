"""
Banker's Algorithm - Deadlock Avoidance (Safety Algorithm)
==========================================================
Checks whether a system is in a SAFE state and, if so, prints a safe
sequence in which every process can finish.

Input  : number of processes, number of resources, Allocation matrix,
         Maximum matrix, Available resources (entered through the console).
Output : Need matrix, Safe / Unsafe state, and the Safe Sequence.

Usage:
  python bankers_algorithm.py               -> enter your own data
  python bankers_algorithm.py --demo        -> built-in textbook example (safe)
  python bankers_algorithm.py --demo-unsafe -> same example, but unsafe
"""

import sys


# ----------------------------------------------------------------------
# Input helpers
# ----------------------------------------------------------------------
def ask(prompt):
    """input() wrapper that echoes the value when input is piped from a file."""
    value = input(prompt)
    if not sys.stdin.isatty():
        print(value)
    return value


def read_int(prompt, minimum=1):
    while True:
        try:
            value = int(ask(prompt).strip())
            if value >= minimum:
                return value
            print(f"  Please enter a number >= {minimum}.")
        except ValueError:
            print("  Invalid input. Please enter a whole number.")


def read_row(prompt, length):
    """Read `length` non-negative integers separated by spaces."""
    while True:
        try:
            row = [int(x) for x in ask(prompt).split()]
            if len(row) == length and all(x >= 0 for x in row):
                return row
            print(f"  Please enter exactly {length} non-negative numbers.")
        except ValueError:
            print("  Invalid input. Please enter whole numbers only.")


def read_matrix(name, n, m):
    print(f"\nEnter the {name} matrix ({n} rows x {m} columns):")
    return [read_row(f"  P{i}: ", m) for i in range(n)]


# ----------------------------------------------------------------------
# Banker's Algorithm
# ----------------------------------------------------------------------
def calculate_need(allocation, maximum):
    """Need[i][j] = Max[i][j] - Allocation[i][j]"""
    return [[maximum[i][j] - allocation[i][j] for j in range(len(maximum[i]))]
            for i in range(len(maximum))]


def is_safe(allocation, need, available):
    """Safety algorithm.
    Work   = copy of Available (resources we can hand out right now)
    Finish = which processes have completed
    Repeatedly find an unfinished process whose Need <= Work; pretend it runs
    to completion and releases its Allocation back into Work.
    Returns (safe?, safe_sequence)."""
    n, m = len(allocation), len(available)
    work = available[:]
    finish = [False] * n
    sequence = []

    while len(sequence) < n:
        found = False
        for i in range(n):
            if not finish[i] and all(need[i][j] <= work[j] for j in range(m)):
                # Process i can finish -> it releases everything it holds.
                for j in range(m):
                    work[j] += allocation[i][j]
                finish[i] = True
                sequence.append(i)
                found = True
        if not found:        # no process can proceed -> unsafe
            break

    return len(sequence) == n, sequence


# ----------------------------------------------------------------------
# Demo data (classic textbook example: 5 processes, 3 resource types)
# ----------------------------------------------------------------------
DEMO_ALLOCATION = [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]]
DEMO_MAXIMUM    = [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]]
DEMO_AVAILABLE  = [3, 3, 2]


def main():
    if "--demo" in sys.argv or "--demo-unsafe" in sys.argv:
        allocation, maximum = DEMO_ALLOCATION, DEMO_MAXIMUM
        available = [0, 0, 0] if "--demo-unsafe" in sys.argv else DEMO_AVAILABLE
    else:
        n = read_int("Enter number of processes: ")
        m = read_int("Enter number of resources: ")
        allocation = read_matrix("Allocation", n, m)
        maximum = read_matrix("Maximum", n, m)
        print("\nEnter the Available resources:")
        available = read_row("  Available: ", m)
        print()

    need = calculate_need(allocation, maximum)

    # A process can never hold more than its declared maximum.
    if any(x < 0 for row in need for x in row):
        print("Error: Allocation exceeds Maximum for at least one process.")
        return

    print("Need Matrix:")
    for i, row in enumerate(need):
        print(f"P{i}: {row}")

    safe, sequence = is_safe(allocation, need, available)

    print()
    if safe:
        print("System is in a Safe State.")
        print("Safe Sequence: " + " → ".join(f"P{i}" for i in sequence))
    else:
        print("System is NOT in a Safe State (Unsafe State - deadlock possible).")
        print("No safe sequence exists.")


if __name__ == "__main__":
    main()
