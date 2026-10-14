"""
Unit Tests for CPU Scheduling Algorithms
Tests FCFS, SJF (Non-preemptive), and Round Robin (RR).
Covers standard scenarios, arrival order handling, CPU idle periods, ties, and edge cases.
"""

import pytest
from scheduler import (
    Process,
    GanttSegment,
    schedule_fcfs,
    schedule_sjf_non_preemptive,
    schedule_round_robin,
    run_all_schedulers,
)


def test_fcfs_basic():
    """
    Standard textbook FCFS test case:
    P1: AT=0, BT=4 -> CT=4, TAT=4, WT=0, RT=0
    P2: AT=1, BT=3 -> CT=7, TAT=6, WT=3, RT=3
    P3: AT=2, BT=1 -> CT=8, TAT=6, WT=5, RT=5
    P4: AT=3, BT=2 -> CT=10, TAT=7, WT=5, RT=5
    Avg TAT = 23/4 = 5.75, Avg WT = 13/4 = 3.25
    """
    procs = [
        Process("P1", 0, 4),
        Process("P2", 1, 3),
        Process("P3", 2, 1),
        Process("P4", 3, 2),
    ]
    res = schedule_fcfs(procs)

    # Check process results
    p_map = {p.pid: p for p in res.processes}
    assert p_map["P1"].completion_time == 4
    assert p_map["P1"].waiting_time == 0
    assert p_map["P1"].turnaround_time == 4

    assert p_map["P2"].completion_time == 7
    assert p_map["P2"].waiting_time == 3
    assert p_map["P2"].turnaround_time == 6

    assert p_map["P3"].completion_time == 8
    assert p_map["P3"].waiting_time == 5
    assert p_map["P3"].turnaround_time == 6

    assert p_map["P4"].completion_time == 10
    assert p_map["P4"].waiting_time == 5
    assert p_map["P4"].turnaround_time == 7

    assert res.avg_turnaround_time == 5.75
    assert res.avg_waiting_time == 3.25
    assert res.total_time == 10
    assert res.cpu_idle_time == 0
    assert res.cpu_utilization == 100.0


def test_fcfs_with_idle_periods():
    """
    FCFS with idle periods at start and in between:
    t=0 to 2: IDLE
    P1: AT=2, BT=3 -> runs [2, 5]
    t=5 to 7: IDLE
    P2: AT=7, BT=2 -> runs [7, 9]
    """
    procs = [
        Process("P1", 2, 3),
        Process("P2", 7, 2),
    ]
    res = schedule_fcfs(procs)

    p_map = {p.pid: p for p in res.processes}
    assert p_map["P1"].completion_time == 5
    assert p_map["P1"].waiting_time == 0
    assert p_map["P1"].turnaround_time == 3

    assert p_map["P2"].completion_time == 9
    assert p_map["P2"].waiting_time == 0
    assert p_map["P2"].turnaround_time == 2

    assert res.total_time == 9
    assert res.cpu_busy_time == 5
    assert res.cpu_idle_time == 4
    assert res.cpu_utilization == pytest.approx(55.56, 0.01)

    # Check Gantt segments
    assert len(res.gantt_chart) == 4
    assert res.gantt_chart[0] == GanttSegment("IDLE", 0, 2, is_idle=True)
    assert res.gantt_chart[1] == GanttSegment("P1", 2, 5, is_idle=False)
    assert res.gantt_chart[2] == GanttSegment("IDLE", 5, 7, is_idle=True)
    assert res.gantt_chart[3] == GanttSegment("P2", 7, 9, is_idle=False)


def test_sjf_non_preemptive_basic():
    """
    Standard textbook SJF Non-preemptive test case:
    P1: AT=1, BT=7
    P2: AT=2, BT=4
    P3: AT=3, BT=1
    P4: AT=4, BT=4
    Timeline:
      [0, 1] IDLE
      [1, 8] P1
      [8, 9] P3 (BT=1)
      [9, 13] P2 (BT=4, earlier arrival than P4)
      [13, 17] P4 (BT=4)
    """
    procs = [
        Process("P1", 1, 7),
        Process("P2", 2, 4),
        Process("P3", 3, 1),
        Process("P4", 4, 4),
    ]
    res = schedule_sjf_non_preemptive(procs)

    p_map = {p.pid: p for p in res.processes}
    assert p_map["P1"].completion_time == 8
    assert p_map["P1"].waiting_time == 0
    assert p_map["P1"].turnaround_time == 7

    assert p_map["P3"].completion_time == 9
    assert p_map["P3"].waiting_time == 5
    assert p_map["P3"].turnaround_time == 6

    assert p_map["P2"].completion_time == 13
    assert p_map["P2"].waiting_time == 7
    assert p_map["P2"].turnaround_time == 11

    assert p_map["P4"].completion_time == 17
    assert p_map["P4"].waiting_time == 9
    assert p_map["P4"].turnaround_time == 13

    assert res.avg_turnaround_time == 9.25
    assert res.avg_waiting_time == 5.25
    assert res.total_time == 17
    assert res.cpu_idle_time == 1


def test_round_robin_basic():
    """
    Standard Round Robin test with Quantum=2:
    P1: AT=0, BT=5
    P2: AT=1, BT=3
    P3: AT=2, BT=1
    Queue transitions:
      t=0: P1 (exec 2, rem=3, interval [0, 2]). Arrive: P2(1), P3(2). Q=[P2, P3, P1]
      t=2: P2 (exec 2, rem=1, interval [2, 4]). Q=[P3, P1, P2]
      t=4: P3 (exec 1, rem=0, interval [4, 5], finishes CT=5). Q=[P1, P2]
      t=5: P1 (exec 2, rem=1, interval [5, 7]). Q=[P2, P1]
      t=7: P2 (exec 1, rem=0, interval [7, 8], finishes CT=8). Q=[P1]
      t=8: P1 (exec 1, rem=0, interval [8, 9], finishes CT=9). Q=[]
    """
    procs = [
        Process("P1", 0, 5),
        Process("P2", 1, 3),
        Process("P3", 2, 1),
    ]
    res = schedule_round_robin(procs, time_quantum=2)

    p_map = {p.pid: p for p in res.processes}
    assert p_map["P1"].completion_time == 9
    assert p_map["P1"].turnaround_time == 9
    assert p_map["P1"].waiting_time == 4
    assert p_map["P1"].response_time == 0

    assert p_map["P2"].completion_time == 8
    assert p_map["P2"].turnaround_time == 7
    assert p_map["P2"].waiting_time == 4
    assert p_map["P2"].response_time == 1

    assert p_map["P3"].completion_time == 5
    assert p_map["P3"].turnaround_time == 3
    assert p_map["P3"].waiting_time == 2
    assert p_map["P3"].response_time == 2

    assert res.avg_turnaround_time == pytest.approx(6.33, 0.01)
    assert res.avg_waiting_time == pytest.approx(3.33, 0.01)
    assert res.avg_response_time == 1.0


def test_round_robin_with_idle():
    """Round Robin when CPU starts idle."""
    procs = [
        Process("P1", 3, 2),
    ]
    res = schedule_round_robin(procs, time_quantum=1)
    assert res.total_time == 5
    assert res.cpu_idle_time == 3
    assert res.cpu_busy_time == 2
    assert res.gantt_chart[0] == GanttSegment("IDLE", 0, 3, is_idle=True)
    assert res.processes[0].completion_time == 5


def test_unsorted_input_order():
    """Ensure schedulers correctly handle processes passed in out-of-order arrival times."""
    procs = [
        Process("P2", 4, 3),
        Process("P1", 0, 2),
        Process("P3", 2, 1),
    ]
    # FCFS should execute P1(0-2), P3(2-3), IDLE(3-4), P2(4-7)
    res = schedule_fcfs(procs)
    p_map = {p.pid: p for p in res.processes}
    assert p_map["P1"].completion_time == 2
    assert p_map["P3"].completion_time == 3
    assert p_map["P2"].completion_time == 7


def test_input_validation():
    """Ensure invalid parameters raise appropriate ValueErrors."""
    with pytest.raises(ValueError):
        Process("P1", -1, 5)

    with pytest.raises(ValueError):
        Process("P1", 0, 0)

    with pytest.raises(ValueError):
        Process("P1", 0, -3)

    procs = [Process("P1", 0, 5)]
    with pytest.raises(ValueError):
        schedule_round_robin(procs, time_quantum=0)

    with pytest.raises(ValueError):
        schedule_round_robin(procs, time_quantum=-2)


def test_run_all_schedulers():
    """Ensure run_all_schedulers returns results for all three algorithms."""
    procs = [
        Process("P1", 0, 4),
        Process("P2", 1, 2),
    ]
    all_res = run_all_schedulers(procs, time_quantum=2)
    assert "FCFS" in all_res
    assert "SJF (Non-Preemptive)" in all_res
    assert "Round Robin" in all_res
    for algo, res in all_res.items():
        assert len(res.processes) == 2
        assert res.total_time > 0
