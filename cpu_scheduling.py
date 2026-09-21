"""
CPU Scheduling Simulator
========================
Simulates four scheduling algorithms:

  Non-Preemptive : 1) First Come First Serve (FCFS)
                   2) Shortest Job First (SJF)
  Preemptive     : 3) Shortest Remaining Time First (Preemptive SJF)
                   4) Round Robin (RR)

Input  : number of processes, arrival time + burst time of each process,
         time quantum (Round Robin only) -- all entered through the console.
Output : Gantt chart, per-process table, Average Waiting Time,
         Average Turnaround Time.

Formulas used:
  Turnaround Time (TAT) = Completion Time (CT) - Arrival Time (AT)
  Waiting Time    (WT)  = Turnaround Time      - Burst Time (BT)
"""

import sys
from collections import deque


# ----------------------------------------------------------------------
# Input helpers
# ----------------------------------------------------------------------
def ask(prompt):
    """input() wrapper. When input is piped from a file, echo the value so
    the saved output still shows what was 'typed'."""
    value = input(prompt)
    if not sys.stdin.isatty():
        print(value)
    return value


def read_int(prompt, minimum=0, maximum=None):
    """Keep asking until the user enters a whole number in the valid range."""
    while True:
        try:
            value = int(ask(prompt).strip())
        except ValueError:
            print("  Invalid input. Please enter a whole number.")
            continue
        if value < minimum or (maximum is not None and value > maximum):
            rng = f">= {minimum}" if maximum is None else f"between {minimum} and {maximum}"
            print(f"  Please enter a number {rng}.")
            continue
        return value


def read_process(number):
    """Read 'arrival burst' for one process on a single line."""
    while True:
        parts = ask(f"P{number} - Arrival time and Burst time (e.g. 0 5): ").split()
        try:
            if len(parts) != 2:
                raise ValueError
            at, bt = int(parts[0]), int(parts[1])
        except ValueError:
            print("  Please enter two whole numbers separated by a space.")
            continue
        if at < 0 or bt < 1:
            print("  Arrival time must be >= 0 and burst time must be >= 1.")
            continue
        return {"pid": f"P{number}", "at": at, "bt": bt}


# ----------------------------------------------------------------------
# Gantt chart helpers
# ----------------------------------------------------------------------
def add_segment(segments, name, start, end):
    """Append (name, start, end) to the Gantt list. If the same process keeps
    running without a break, extend the previous block instead of adding a new one."""
    if segments and segments[-1][0] == name and segments[-1][2] == start:
        segments[-1] = (name, segments[-1][1], end)
    else:
        segments.append((name, start, end))


def print_gantt(segments):
    """Draw the Gantt chart as text, e.g.
        |  P1  |  P2  |
        0      5      9
    """
    bar = "|"
    times = ""
    for name, start, end in segments:
        width = max(len(name) + 2, len(str(start)) + 1)
        bar += name.center(width) + "|"
        times += str(start).ljust(width + 1)
    times += str(segments[-1][2])          # final end time
    print("Gantt Chart:")
    print(bar)
    print(times)


# ----------------------------------------------------------------------
# Scheduling algorithms  (each returns a list of Gantt segments)
# ----------------------------------------------------------------------
def fcfs(processes):
    """FCFS (non-preemptive): run processes strictly in order of arrival."""
    segments, time = [], 0
    for p in sorted(processes, key=lambda p: p["at"]):   # stable sort keeps input order on ties
        if time < p["at"]:                               # CPU sits idle until the process arrives
            add_segment(segments, "IDLE", time, p["at"])
            time = p["at"]
        add_segment(segments, p["pid"], time, time + p["bt"])
        time += p["bt"]
    return segments


def sjf(processes):
    """Non-preemptive SJF: when the CPU is free, pick the arrived process with
    the shortest burst time and let it run to completion."""
    segments, time = [], 0
    remaining = list(processes)
    while remaining:
        ready = [p for p in remaining if p["at"] <= time]
        if not ready:                                    # nobody has arrived yet -> idle
            nxt = min(p["at"] for p in remaining)
            add_segment(segments, "IDLE", time, nxt)
            time = nxt
            continue
        p = min(ready, key=lambda p: (p["bt"], p["at"]))  # shortest burst, tie -> earliest arrival
        add_segment(segments, p["pid"], time, time + p["bt"])
        time += p["bt"]
        remaining.remove(p)
    return segments


def srtf(processes):
    """Preemptive SJF (Shortest Remaining Time First): whenever a new process
    arrives, compare its burst with the remaining time of the running process
    and switch if it is shorter."""
    segments, time = [], 0
    rem = {p["pid"]: p["bt"] for p in processes}
    while rem:
        ready = [p for p in processes if p["pid"] in rem and p["at"] <= time]
        future = [p["at"] for p in processes if p["pid"] in rem and p["at"] > time]
        if not ready:                                    # idle until next arrival
            nxt = min(future)
            add_segment(segments, "IDLE", time, nxt)
            time = nxt
            continue
        p = min(ready, key=lambda p: (rem[p["pid"]], p["at"]))
        # Run until it finishes OR until the next arrival (a chance to preempt).
        run = rem[p["pid"]]
        if future:
            run = min(run, min(future) - time)
        add_segment(segments, p["pid"], time, time + run)
        time += run
        rem[p["pid"]] -= run
        if rem[p["pid"]] == 0:
            del rem[p["pid"]]
    return segments


def round_robin(processes, quantum):
    """Round Robin (preemptive): each process gets at most `quantum` units of
    CPU, then goes to the back of the ready queue."""
    segments, time = [], 0
    rem = {p["pid"]: p["bt"] for p in processes}
    arrivals = sorted(processes, key=lambda p: p["at"])
    queue, i = deque(), 0                                # i = next process waiting to arrive

    def admit(now):
        """Move every process that has arrived by `now` into the ready queue."""
        nonlocal i
        while i < len(arrivals) and arrivals[i]["at"] <= now:
            queue.append(arrivals[i]["pid"])
            i += 1

    admit(time)
    while queue or i < len(arrivals):
        if not queue:                                    # idle until next arrival
            nxt = arrivals[i]["at"]
            add_segment(segments, "IDLE", time, nxt)
            time = nxt
            admit(time)
            continue
        pid = queue.popleft()
        run = min(quantum, rem[pid])
        add_segment(segments, pid, time, time + run)
        time += run
        rem[pid] -= run
        admit(time)                                      # newcomers enter BEFORE the preempted process
        if rem[pid] > 0:
            queue.append(pid)
    return segments


# ----------------------------------------------------------------------
# Results
# ----------------------------------------------------------------------
def report(title, processes, segments):
    """Print Gantt chart, per-process table and the two averages.
    Returns (avg_waiting, avg_turnaround)."""
    # Completion time = end of the last Gantt block that belongs to the process.
    ct = {}
    for name, _, end in segments:
        if name != "IDLE":
            ct[name] = end

    print("\n" + "=" * 56)
    print(f" {title}")
    print("=" * 56)
    print_gantt(segments)

    print("\nPID   AT   BT   CT   TAT   WT")
    print("-" * 30)
    total_wt = total_tat = 0
    for p in processes:
        tat = ct[p["pid"]] - p["at"]        # Turnaround = Completion - Arrival
        wt = tat - p["bt"]                  # Waiting    = Turnaround - Burst
        total_tat += tat
        total_wt += wt
        print(f"{p['pid']:<5}{p['at']:>3}{p['bt']:>5}{ct[p['pid']]:>5}{tat:>6}{wt:>5}")

    n = len(processes)
    avg_wt, avg_tat = total_wt / n, total_tat / n
    print(f"\nAverage Waiting Time    : {avg_wt:.2f}")
    print(f"Average Turnaround Time : {avg_tat:.2f}")
    return avg_wt, avg_tat


def run_algorithm(choice, processes, quantum=None):
    """Dispatch to the chosen algorithm and print its results."""
    if choice == 1:
        return report("First Come First Serve (Non-Preemptive)", processes, fcfs(processes))
    if choice == 2:
        return report("Shortest Job First (Non-Preemptive)", processes, sjf(processes))
    if choice == 3:
        return report("Shortest Remaining Time First (Preemptive SJF)", processes, srtf(processes))
    if quantum is None:
        quantum = read_int("Enter time quantum: ", minimum=1)
    return report(f"Round Robin (Preemptive, Quantum = {quantum})",
                  processes, round_robin(processes, quantum))


# ----------------------------------------------------------------------
# Main program
# ----------------------------------------------------------------------
def main():
    print("=" * 56)
    print("          CPU SCHEDULING SIMULATOR")
    print("=" * 56)

    n = read_int("Enter number of processes: ", minimum=1)
    processes = [read_process(i + 1) for i in range(n)]

    while True:
        print("\n--- MENU ---")
        print("1. FCFS                (Non-Preemptive)")
        print("2. SJF                 (Non-Preemptive)")
        print("3. SRTF / Preemptive SJF")
        print("4. Round Robin         (Preemptive)")
        print("5. Run ALL and compare")
        print("0. Exit")
        choice = read_int("Choose an option: ", minimum=0, maximum=5)

        if choice == 0:
            print("Goodbye!")
            break
        if choice in (1, 2, 3, 4):
            run_algorithm(choice, processes)
        else:                                            # option 5: run everything
            quantum = read_int("Enter time quantum for Round Robin: ", minimum=1)
            names = ["FCFS", "SJF", "SRTF", f"RR (q={quantum})"]
            results = [run_algorithm(c, processes, quantum) for c in (1, 2, 3, 4)]
            print("\n" + "=" * 56)
            print(" COMPARISON SUMMARY")
            print("=" * 56)
            print(f"{'Algorithm':<14}{'Avg WT':>10}{'Avg TAT':>12}")
            print("-" * 36)
            for name, (wt, tat) in zip(names, results):
                print(f"{name:<14}{wt:>10.2f}{tat:>12.2f}")


if __name__ == "__main__":
    main()
