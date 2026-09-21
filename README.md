# CPU Scheduling & Banker's Algorithm

Simulations of CPU scheduling algorithms and the Banker's Algorithm (deadlock avoidance).

## Files
| File | Description |
|------|-------------|
| `cpu_scheduling.py` | FCFS, SJF (non-preemptive), SRTF / preemptive SJF, Round Robin |
| `bankers_algorithm.py` | Banker's Algorithm safety check |
| `sample_input_cpu_scheduling.txt` | Sample console input for the scheduler |
| `sample_output_cpu_scheduling.txt` | Output produced from that input |
| `sample_output_bankers.txt` | Banker's Algorithm output (safe and unsafe example) |

## 1. CPU Scheduling

```
python cpu_scheduling.py
```

**Input (typed in the console)**
1. Number of processes
2. For each process, its **arrival time** and **burst time** on one line, e.g. `2 8`
3. A menu choice: 1 = FCFS, 2 = SJF, 3 = SRTF, 4 = Round Robin, 5 = run all and compare, 0 = exit
4. Time quantum (only asked when Round Robin runs)

**Output:** Gantt chart (idle time shown as `IDLE`), a per-process table (AT, BT, CT, TAT, WT), Average Waiting Time and Average Turnaround Time.

Formulas: `TAT = Completion Time - Arrival Time`, `WT = TAT - Burst Time`.

To reproduce the sample output without typing:
```
python cpu_scheduling.py < sample_input_cpu_scheduling.txt
```

## 2. Banker's Algorithm

```
python bankers_algorithm.py               # enter your own data
python bankers_algorithm.py --demo        # built-in textbook example (safe state)
python bankers_algorithm.py --demo-unsafe # same example with Available = [0,0,0] (unsafe)
```

**Input (typed in the console):** number of processes, number of resources, then the Allocation matrix, Maximum matrix (one row per process, values separated by spaces) and the Available resources.

**Output:** the Need matrix (`Need = Max - Allocation`), whether the system is in a Safe or Unsafe state, and the Safe Sequence if one exists.

Example run for entering data manually (5 processes, 3 resources):
```
5
3
0 1 0
2 0 0
3 0 2
2 1 1
0 0 2
7 5 3
3 2 2
9 0 2
2 2 2
4 3 3
3 3 2
```

## How it works (short)
- **FCFS** runs processes in arrival order.
- **SJF** picks the shortest burst among arrived processes and runs it to completion.
- **SRTF** re-checks whenever a process arrives and switches to the one with the shortest remaining time.
- **Round Robin** gives each process at most one time quantum, then sends it to the back of the queue. New arrivals join the queue before the preempted process.
- **Banker's Algorithm** repeatedly finds a process whose Need can be satisfied by the currently available resources, lets it finish, and reclaims its Allocation. If every process can finish, the order is a safe sequence.
