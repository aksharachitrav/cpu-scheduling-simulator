"""
CPU Scheduling Algorithms Engine
Implements:
  - First-Come, First-Served (FCFS)
  - Non-Preemptive Shortest Job First (SJF)
  - Round Robin (RR) with configurable Time Quantum

Handles arrival times, arbitrary arrival order, CPU idle periods, and edge cases.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from collections import deque


@dataclass
class Process:
    pid: str
    arrival_time: int
    burst_time: int
    priority: int = 0

    def __post_init__(self):
        if self.burst_time <= 0:
            raise ValueError(f"Process {self.pid}: Burst time must be positive (> 0), got {self.burst_time}.")
        if self.arrival_time < 0:
            raise ValueError(f"Process {self.pid}: Arrival time cannot be negative, got {self.arrival_time}.")


@dataclass
class GanttSegment:
    pid: str
    start_time: int
    end_time: int
    is_idle: bool = False

    @property
    def duration(self) -> int:
        return self.end_time - self.start_time


@dataclass
class ProcessResult:
    pid: str
    arrival_time: int
    burst_time: int
    start_time: int
    completion_time: int
    turnaround_time: int
    waiting_time: int
    response_time: int


@dataclass
class ScheduleResult:
    algorithm: str
    processes: List[ProcessResult]
    gantt_chart: List[GanttSegment]
    avg_turnaround_time: float
    avg_waiting_time: float
    avg_response_time: float
    total_time: int
    cpu_busy_time: int
    cpu_idle_time: int
    cpu_utilization: float
    throughput: float
    time_quantum: Optional[int] = None


def _calculate_summary(
    algorithm: str,
    results: List[ProcessResult],
    gantt: List[GanttSegment],
    time_quantum: Optional[int] = None,
) -> ScheduleResult:
    """Computes summary statistics given completed process results and Gantt segments."""
    n = len(results)
    if n == 0:
        return ScheduleResult(
            algorithm=algorithm,
            processes=[],
            gantt_chart=[],
            avg_turnaround_time=0.0,
            avg_waiting_time=0.0,
            avg_response_time=0.0,
            total_time=0,
            cpu_busy_time=0,
            cpu_idle_time=0,
            cpu_utilization=0.0,
            throughput=0.0,
            time_quantum=time_quantum,
        )

    avg_tat = sum(p.turnaround_time for p in results) / n
    avg_wt = sum(p.waiting_time for p in results) / n
    avg_rt = sum(p.response_time for p in results) / n

    total_time = gantt[-1].end_time if gantt else 0
    cpu_idle_time = sum(seg.duration for seg in gantt if seg.is_idle)
    cpu_busy_time = total_time - cpu_idle_time
    cpu_utilization = (cpu_busy_time / total_time * 100.0) if total_time > 0 else 0.0
    throughput = (n / total_time) if total_time > 0 else 0.0

    return ScheduleResult(
        algorithm=algorithm,
        processes=results,
        gantt_chart=gantt,
        avg_turnaround_time=round(avg_tat, 2),
        avg_waiting_time=round(avg_wt, 2),
        avg_response_time=round(avg_rt, 2),
        total_time=total_time,
        cpu_busy_time=cpu_busy_time,
        cpu_idle_time=cpu_idle_time,
        cpu_utilization=round(cpu_utilization, 2),
        throughput=round(throughput, 4),
        time_quantum=time_quantum,
    )


def schedule_fcfs(processes: List[Process]) -> ScheduleResult:
    """
    First-Come, First-Served (FCFS) Scheduling (Non-preemptive).
    Processes are executed in order of arrival time.
    Ties are broken by original input index.
    """
    if not processes:
        return _calculate_summary("First Come First Serve (FCFS)", [], [])

    # Keep track of original order for tie-breaking
    indexed_procs = sorted(
        enumerate(processes),
        key=lambda item: (item[1].arrival_time, item[0])
    )

    current_time = 0
    gantt: List[GanttSegment] = []
    results: List[ProcessResult] = []

    for idx, proc in indexed_procs:
        # Check if CPU is idle before this process arrives
        if current_time < proc.arrival_time:
            gantt.append(
                GanttSegment(
                    pid="IDLE",
                    start_time=current_time,
                    end_time=proc.arrival_time,
                    is_idle=True,
                )
            )
            current_time = proc.arrival_time

        start_time = current_time
        completion_time = start_time + proc.burst_time
        gantt.append(
            GanttSegment(
                pid=proc.pid,
                start_time=start_time,
                end_time=completion_time,
                is_idle=False,
            )
        )

        tat = completion_time - proc.arrival_time
        wt = tat - proc.burst_time
        rt = start_time - proc.arrival_time

        results.append(
            ProcessResult(
                pid=proc.pid,
                arrival_time=proc.arrival_time,
                burst_time=proc.burst_time,
                start_time=start_time,
                completion_time=completion_time,
                turnaround_time=tat,
                waiting_time=wt,
                response_time=rt,
            )
        )

        current_time = completion_time

    # Re-sort results by original process order for intuitive display
    pid_to_result = {r.pid: r for r in results}
    ordered_results = [pid_to_result[p.pid] for p in processes]

    return _calculate_summary("First Come First Serve (FCFS)", ordered_results, gantt)


def schedule_sjf_non_preemptive(processes: List[Process]) -> ScheduleResult:
    """
    Shortest Job First (SJF) Scheduling (Non-preemptive).
    At any decision point, the ready process with the shortest burst time is selected.
    Ties broken by arrival time, then original order.
    """
    if not processes:
        return _calculate_summary("Shortest Job First (SJF Non-preemptive)", [], [])

    # Associate each process with its initial index
    remaining = [
        {"idx": i, "proc": p}
        for i, p in enumerate(processes)
    ]

    current_time = 0
    gantt: List[GanttSegment] = []
    results: List[ProcessResult] = []

    while remaining:
        # Ready processes: arrival_time <= current_time
        ready = [item for item in remaining if item["proc"].arrival_time <= current_time]

        if not ready:
            # CPU is idle until the earliest next arrival
            earliest_arrival = min(item["proc"].arrival_time for item in remaining)
            gantt.append(
                GanttSegment(
                    pid="IDLE",
                    start_time=current_time,
                    end_time=earliest_arrival,
                    is_idle=True,
                )
            )
            current_time = earliest_arrival
            continue

        # Pick process with smallest burst time, then earliest arrival, then original index
        best_item = min(
            ready,
            key=lambda item: (item["proc"].burst_time, item["proc"].arrival_time, item["idx"])
        )
        remaining.remove(best_item)

        proc = best_item["proc"]
        start_time = current_time
        completion_time = start_time + proc.burst_time

        gantt.append(
            GanttSegment(
                pid=proc.pid,
                start_time=start_time,
                end_time=completion_time,
                is_idle=False,
            )
        )

        tat = completion_time - proc.arrival_time
        wt = tat - proc.burst_time
        rt = start_time - proc.arrival_time

        results.append(
            ProcessResult(
                pid=proc.pid,
                arrival_time=proc.arrival_time,
                burst_time=proc.burst_time,
                start_time=start_time,
                completion_time=completion_time,
                turnaround_time=tat,
                waiting_time=wt,
                response_time=rt,
            )
        )

        current_time = completion_time

    # Return results ordered by original process order
    pid_to_result = {r.pid: r for r in results}
    ordered_results = [pid_to_result[p.pid] for p in processes]

    return _calculate_summary("Shortest Job First (SJF Non-preemptive)", ordered_results, gantt)


def schedule_round_robin(processes: List[Process], time_quantum: int) -> ScheduleResult:
    """
    Round Robin (RR) Scheduling (Preemptive).
    Standard queue semantics:
      - Arriving processes enter the ready queue.
      - A process executes for at most time_quantum units.
      - Processes that arrive while a process is executing are queued before
        the currently executing preempted process re-enters the queue.
    """
    if time_quantum <= 0:
        raise ValueError(f"Time quantum must be a positive integer (> 0), got {time_quantum}.")

    if not processes:
        return _calculate_summary("Round Robin (RR)", [], [], time_quantum=time_quantum)

    # Track process state
    indexed_procs = [
        {"idx": i, "proc": p, "rem_bt": p.burst_time}
        for i, p in enumerate(processes)
    ]

    # Sort candidates by arrival time and initial index
    unarrived = sorted(
        indexed_procs,
        key=lambda item: (item["proc"].arrival_time, item["idx"])
    )

    ready_queue: deque = deque()
    first_start_times: Dict[str, int] = {}
    completion_times: Dict[str, int] = {}
    gantt: List[GanttSegment] = []

    current_time = 0

    # If first arrival is > 0, idle until then
    if unarrived and unarrived[0]["proc"].arrival_time > 0:
        first_arr = unarrived[0]["proc"].arrival_time
        gantt.append(
            GanttSegment(
                pid="IDLE",
                start_time=0,
                end_time=first_arr,
                is_idle=True,
            )
        )
        current_time = first_arr

    # Enqueue initial arrivals at current_time
    while unarrived and unarrived[0]["proc"].arrival_time <= current_time:
        ready_queue.append(unarrived.pop(0))

    while ready_queue or unarrived:
        if not ready_queue:
            # Idle jump
            next_arr = unarrived[0]["proc"].arrival_time
            gantt.append(
                GanttSegment(
                    pid="IDLE",
                    start_time=current_time,
                    end_time=next_arr,
                    is_idle=True,
                )
            )
            current_time = next_arr
            while unarrived and unarrived[0]["proc"].arrival_time <= current_time:
                ready_queue.append(unarrived.pop(0))
            continue

        current_item = ready_queue.popleft()
        proc = current_item["proc"]

        if proc.pid not in first_start_times:
            first_start_times[proc.pid] = current_time

        exec_duration = min(current_item["rem_bt"], time_quantum)
        start_time = current_time
        end_time = current_time + exec_duration

        # Merge with last segment if it's the exact same PID to keep Gantt clean
        # (Only if consecutive run without preemption, though standard RR records each slice)
        gantt.append(
            GanttSegment(
                pid=proc.pid,
                start_time=start_time,
                end_time=end_time,
                is_idle=False,
            )
        )

        current_time = end_time
        current_item["rem_bt"] -= exec_duration

        # Canonical OS rule: Enqueue any newly arrived processes before re-enqueueing current process
        while unarrived and unarrived[0]["proc"].arrival_time <= current_time:
            ready_queue.append(unarrived.pop(0))

        if current_item["rem_bt"] > 0:
            ready_queue.append(current_item)
        else:
            completion_times[proc.pid] = current_time

    # Calculate final process results
    results: List[ProcessResult] = []
    for proc in processes:
        ct = completion_times[proc.pid]
        st = first_start_times.get(proc.pid, proc.arrival_time)
        tat = ct - proc.arrival_time
        wt = tat - proc.burst_time
        rt = st - proc.arrival_time

        results.append(
            ProcessResult(
                pid=proc.pid,
                arrival_time=proc.arrival_time,
                burst_time=proc.burst_time,
                start_time=st,
                completion_time=ct,
                turnaround_time=tat,
                waiting_time=wt,
                response_time=rt,
            )
        )

    return _calculate_summary("Round Robin (RR)", results, gantt, time_quantum=time_quantum)


def run_all_schedulers(processes: List[Process], time_quantum: int = 2) -> Dict[str, ScheduleResult]:
    """Runs all three algorithms on the same process dataset for direct comparison."""
    return {
        "FCFS": schedule_fcfs(processes),
        "SJF (Non-Preemptive)": schedule_sjf_non_preemptive(processes),
        "Round Robin": schedule_round_robin(processes, time_quantum=time_quantum),
    }
