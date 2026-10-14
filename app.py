"""
CPU Scheduling Simulator - Streamlit Web Application
An interactive, educational simulator for Operating Systems students & faculty.
Supports: FCFS, Non-Preemptive SJF, and Round Robin (RR).
"""

import streamlit as st
import pandas as pd
from typing import List, Dict
from scheduler import (
    Process,
    GanttSegment,
    ProcessResult,
    ScheduleResult,
    schedule_fcfs,
    schedule_sjf_non_preemptive,
    schedule_round_robin,
    run_all_schedulers,
)

# Set page configuration
st.set_page_config(
    page_title="CPU Scheduling Simulator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    /* Metric Card Styling */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1e3a8a;
    }
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-card h3 {
        margin: 0;
        font-size: 0.9rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-card .value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0f172a;
        margin-top: 4px;
    }

    /* Gantt Chart Styling */
    .gantt-container {
        display: flex;
        flex-direction: column;
        margin: 20px 0;
        background: #ffffff;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        overflow-x: auto;
    }
    .gantt-bar-row {
        display: flex;
        align-items: center;
        width: 100%;
        min-width: 600px;
        height: 60px;
        position: relative;
    }
    .gantt-block {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #ffffff;
        font-weight: 700;
        font-size: 0.95rem;
        border-right: 1px solid rgba(255, 255, 255, 0.4);
        border-radius: 4px;
        margin: 0 1px;
        height: 100%;
        position: relative;
        transition: transform 0.15s ease;
    }
    .gantt-block:hover {
        transform: translateY(-2px);
        filter: brightness(1.08);
    }
    .gantt-block.idle {
        background: repeating-linear-gradient(
            45deg,
            #cbd5e1,
            #cbd5e1 8px,
            #94a3b8 8px,
            #94a3b8 16px
        );
        color: #1e293b;
        font-weight: 800;
    }
    .gantt-sublabel {
        font-size: 0.72rem;
        font-weight: 500;
        opacity: 0.9;
    }
    .gantt-timeline-row {
        display: flex;
        width: 100%;
        min-width: 600px;
        position: relative;
        height: 25px;
        margin-top: 6px;
    }
    .time-marker {
        position: absolute;
        transform: translateX(-50%);
        font-size: 0.78rem;
        font-weight: 600;
        color: #475569;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Process Colors Palette for Gantt Chart
PROCESS_COLORS = [
    "#2563eb",  # Blue
    "#16a34a",  # Green
    "#d97706",  # Amber
    "#9333ea",  # Purple
    "#0891b2",  # Cyan
    "#e11d48",  # Rose
    "#4f46e5",  # Indigo
    "#ca8a04",  # Yellow
    "#0d9488",  # Teal
    "#c026d3",  # Fuchsia
]


def get_color_for_pid(pid: str, pids: List[str]) -> str:
    if pid == "IDLE":
        return "#94a3b8"
    try:
        idx = pids.index(pid)
        return PROCESS_COLORS[idx % len(PROCESS_COLORS)]
    except ValueError:
        return "#3b82f6"


def render_html_gantt_chart(gantt: List[GanttSegment], distinct_pids: List[str]):
    """Renders an interactive, proportional HTML/CSS Gantt Chart."""
    if not gantt:
        st.info("No Gantt chart to display.")
        return

    total_duration = gantt[-1].end_time
    if total_duration <= 0:
        return

    # Build blocks
    blocks_html = []
    markers_html = []

    # First time marker at 0
    markers_html.append(
        '<span class="time-marker" style="left: 0%;">0</span>'
    )

    for seg in gantt:
        dur = seg.duration
        pct = (dur / total_duration) * 100.0
        end_pct = (seg.end_time / total_duration) * 100.0

        if seg.is_idle:
            block = f"""
            <div class="gantt-block idle" style="flex: {dur};" title="CPU Idle ({seg.start_time} - {seg.end_time})">
                <span>IDLE</span>
                <span class="gantt-sublabel">{seg.start_time}→{seg.end_time}</span>
            </div>
            """
        else:
            color = get_color_for_pid(seg.pid, distinct_pids)
            block = f"""
            <div class="gantt-block" style="flex: {dur}; background-color: {color};" title="{seg.pid}: {seg.start_time} to {seg.end_time} (dur: {dur})">
                <span>{seg.pid}</span>
                <span class="gantt-sublabel">{seg.start_time}→{seg.end_time}</span>
            </div>
            """
        blocks_html.append(block)

        # Marker at segment end
        markers_html.append(
            f'<span class="time-marker" style="left: {end_pct:.2f}%;">{seg.end_time}</span>'
        )

    gantt_html = f"""
    <div class="gantt-container">
        <div class="gantt-bar-row">
            {''.join(blocks_html)}
        </div>
        <div class="gantt-timeline-row">
            {''.join(markers_html)}
        </div>
    </div>
    """
    st.markdown(gantt_html, unsafe_allow_html=True)


# Preset configurations for quick testing and grading
PRESETS = {
    "Textbook Standard (Mixed Arrival)": [
        {"pid": "P1", "arrival_time": 0, "burst_time": 5},
        {"pid": "P2", "arrival_time": 1, "burst_time": 3},
        {"pid": "P3", "arrival_time": 2, "burst_time": 8},
        {"pid": "P4", "arrival_time": 3, "burst_time": 6},
    ],
    "CPU Idle Periods (Gaps in Arrivals)": [
        {"pid": "P1", "arrival_time": 2, "burst_time": 3},
        {"pid": "P2", "arrival_time": 8, "burst_time": 4},
        {"pid": "P3", "arrival_time": 15, "burst_time": 2},
    ],
    "SJF Showdown (Short vs Long)": [
        {"pid": "P1", "arrival_time": 0, "burst_time": 7},
        {"pid": "P2", "arrival_time": 2, "burst_time": 4},
        {"pid": "P3", "arrival_time": 4, "burst_time": 1},
        {"pid": "P4", "arrival_time": 5, "burst_time": 4},
    ],
    "Simultaneous Arrivals (All AT=0)": [
        {"pid": "P1", "arrival_time": 0, "burst_time": 8},
        {"pid": "P2", "arrival_time": 0, "burst_time": 4},
        {"pid": "P3", "arrival_time": 0, "burst_time": 9},
        {"pid": "P4", "arrival_time": 0, "burst_time": 5},
    ],
}


def main():
    # Header Section
    st.title("⚡ CPU Scheduling Simulator")
    st.caption("Operating Systems Mini Project • Interactive Visualization & Analysis")

    # Sidebar Controls
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Mode Selection
        algorithm_choice = st.selectbox(
            "Select Scheduling Algorithm:",
            [
                "First-Come, First-Served (FCFS)",
                "Shortest Job First (SJF - Non-Preemptive)",
                "Round Robin (RR)",
                "Compare All Algorithms",
            ],
            index=0,
        )

        time_quantum = 2
        if "Round Robin" in algorithm_choice or algorithm_choice == "Compare All Algorithms":
            time_quantum = st.number_input(
                "Round Robin Time Quantum (TQ):",
                min_value=1,
                max_value=100,
                value=2,
                step=1,
                help="CPU time slice allocated to each process in Round Robin.",
            )

        st.divider()

        # Preset Loader
        st.subheader("📋 Load Sample Scenarios")
        selected_preset = st.selectbox(
            "Choose a Preset Example:",
            ["Custom Input"] + list(PRESETS.keys()),
        )

        st.divider()
        st.markdown(
            """
            **Quick OS Reference:**
            - **TAT** = Completion Time − Arrival Time
            - **WT** = Turnaround Time − Burst Time
            - **RT** = First Execution − Arrival Time
            """
        )

    # Initialize Session State for Process Table
    if "process_data" not in st.session_state or selected_preset != st.session_state.get("last_preset"):
        st.session_state["last_preset"] = selected_preset
        if selected_preset in PRESETS:
            st.session_state["process_data"] = pd.DataFrame(PRESETS[selected_preset])
        else:
            if "process_data" not in st.session_state:
                st.session_state["process_data"] = pd.DataFrame(PRESETS["Textbook Standard (Mixed Arrival)"])

    # Process Input Section
    st.subheader("📥 Process Inputs")
    st.write(
        "You can edit cells directly in the table below, add new rows, or remove rows. "
        "Arrival Time $\\ge 0$ and Burst Time $> 0$."
    )

    edited_df = st.data_editor(
        st.session_state["process_data"],
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "pid": st.column_config.TextColumn("Process ID (PID)", required=True),
            "arrival_time": st.column_config.NumberColumn(
                "Arrival Time (AT)", min_value=0, step=1, required=True
            ),
            "burst_time": st.column_config.NumberColumn(
                "Burst Time (BT)", min_value=1, step=1, required=True
            ),
        },
        key="process_editor",
    )

    # Validate process inputs
    error_msg = None
    processes: List[Process] = []

    if edited_df.empty:
        error_msg = "Please enter at least one process to simulate."
    else:
        # Check nulls
        if edited_df["pid"].isnull().any() or edited_df["arrival_time"].isnull().any() or edited_df["burst_time"].isnull().any():
            error_msg = "Table contains empty cells. Please fill all PID, Arrival Time, and Burst Time values."
        else:
            # Check unique PIDs
            pids = edited_df["pid"].astype(str).str.strip().tolist()
            if len(pids) != len(set(pids)):
                error_msg = "Duplicate Process IDs detected! Each process must have a unique PID (e.g. P1, P2, P3)."
            else:
                try:
                    for _, row in edited_df.iterrows():
                        p = Process(
                            pid=str(row["pid"]).strip(),
                            arrival_time=int(row["arrival_time"]),
                            burst_time=int(row["burst_time"]),
                        )
                        processes.append(p)
                except ValueError as ve:
                    error_msg = str(ve)

    if error_msg:
        st.error(f"⚠️ Validation Error: {error_msg}")
        return

    # Simulation Execution
    st.divider()

    if algorithm_choice == "Compare All Algorithms":
        st.header("📊 Comparative Analysis")
        st.write("Comparing **FCFS**, **SJF (Non-Preemptive)**, and **Round Robin** on your processes.")

        results_dict = run_all_schedulers(processes, time_quantum=time_quantum)

        # Comparison Metrics Cards
        cols = st.columns(3)
        algo_names = list(results_dict.keys())

        for idx, algo_name in enumerate(algo_names):
            res = results_dict[algo_name]
            with cols[idx]:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <h3>{algo_name}</h3>
                        <div class="value">{res.avg_waiting_time} <span style="font-size: 1rem; color: #64748b;">ms avg WT</span></div>
                        <p style="margin: 8px 0 0 0; color: #475569; font-size: 0.9rem;">
                            Avg Turnaround: <strong>{res.avg_turnaround_time} ms</strong><br>
                            CPU Utilization: <strong>{res.cpu_utilization}%</strong><br>
                            Makespan: <strong>{res.total_time} ms</strong>
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.write("")

        # Visual Comparison Bar Chart
        comp_df = pd.DataFrame(
            [
                {
                    "Algorithm": name,
                    "Avg Waiting Time (WT)": res.avg_waiting_time,
                    "Avg Turnaround Time (TAT)": res.avg_turnaround_time,
                    "Avg Response Time (RT)": res.avg_response_time,
                    "CPU Utilization (%)": res.cpu_utilization,
                }
                for name, res in results_dict.items()
            ]
        )

        st.subheader("📈 Performance Comparison Chart")
        chart_data = comp_df.set_index("Algorithm")[["Avg Waiting Time (WT)", "Avg Turnaround Time (TAT)"]]
        st.bar_chart(chart_data)

        # Tabbed Gantt Charts & Detailed Tables for Each Algorithm
        st.subheader("🔍 Individual Execution Breakdown")
        tabs = st.tabs([f"📌 {name}" for name in algo_names])

        distinct_pids = [p.pid for p in processes]

        for tab, name in zip(tabs, algo_names):
            with tab:
                res = results_dict[name]
                display_single_schedule_result(res, distinct_pids)

    else:
        # Single Algorithm Execution
        if "FCFS" in algorithm_choice:
            result = schedule_fcfs(processes)
        elif "SJF" in algorithm_choice:
            result = schedule_sjf_non_preemptive(processes)
        else:
            result = schedule_round_robin(processes, time_quantum=time_quantum)

        distinct_pids = [p.pid for p in processes]
        st.header(f"📈 Results: {result.algorithm}")
        display_single_schedule_result(result, distinct_pids)

    # OS Educational Guide Footer
    with st.expander("📚 How CPU Scheduling Calculations Work"):
        st.markdown(
            """
            ### Formulas & Definitions
            - **Arrival Time (AT):** Time at which the process enters the ready queue.
            - **Burst Time (BT):** CPU execution time required by the process.
            - **Completion Time (CT):** Exact time when the process finishes execution.
            - **Turnaround Time (TAT):** Total time spent by process from arrival to completion.  
              $$\\text{TAT} = \\text{Completion Time (CT)} - \\text{Arrival Time (AT)}$$
            - **Waiting Time (WT):** Total time the process spent waiting in the ready queue.  
              $$\\text{WT} = \\text{Turnaround Time (TAT)} - \\text{Burst Time (BT)}$$
            - **Response Time (RT):** Time from process arrival until its very first CPU allocation.  
              $$\\text{RT} = \\text{First Start Time} - \\text{Arrival Time (AT)}$$
            - **CPU Utilization:** Percentage of total time CPU spent running processes.  
              $$\\text{CPU Utilization} = \\frac{\\text{Total Time} - \\text{Idle Time}}{\\text{Total Time}} \\times 100\\%$$
            - **Throughput:** Number of processes completed per unit time.
            """
        )


def display_single_schedule_result(result: ScheduleResult, distinct_pids: List[str]):
    """Renders the Gantt chart, metrics, and data tables for a given schedule result."""

    # 1. Gantt Chart
    st.subheader("📅 Gantt Chart")
    render_html_gantt_chart(result.gantt_chart, distinct_pids)

    # 2. Key Metrics Row
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Avg Waiting Time", f"{result.avg_waiting_time} ms")
    m2.metric("Avg Turnaround Time", f"{result.avg_turnaround_time} ms")
    m3.metric("Avg Response Time", f"{result.avg_response_time} ms")
    m4.metric("CPU Utilization", f"{result.cpu_utilization} %")
    m5.metric("Total Makespan", f"{result.total_time} ms")

    # 3. Process Table
    st.subheader("📋 Process Scheduling Table")
    table_data = []
    for p in result.processes:
        table_data.append(
            {
                "Process ID": p.pid,
                "Arrival Time (AT)": p.arrival_time,
                "Burst Time (BT)": p.burst_time,
                "Start Time": p.start_time,
                "Completion Time (CT)": p.completion_time,
                "Turnaround Time (TAT)": p.turnaround_time,
                "Waiting Time (WT)": p.waiting_time,
                "Response Time (RT)": p.response_time,
            }
        )
    df_res = pd.DataFrame(table_data)
    st.dataframe(df_res, use_container_width=True, hide_index=True)

    # CSV Download Button
    csv_bytes = df_res.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Results as CSV",
        data=csv_bytes,
        file_name=f"{result.algorithm.replace(' ', '_').lower()}_results.csv",
        mime="text/csv",
    )

    # 4. Step-by-Step Gantt Execution Log
    with st.expander("🕒 Step-by-Step Execution Segments"):
        gantt_records = []
        for i, seg in enumerate(result.gantt_chart, 1):
            gantt_records.append(
                {
                    "Step": i,
                    "Entity": "CPU IDLE" if seg.is_idle else seg.pid,
                    "Start Time": seg.start_time,
                    "End Time": seg.end_time,
                    "Duration": seg.duration,
                    "Type": "Idle Period" if seg.is_idle else "Process Execution",
                }
            )
        st.dataframe(pd.DataFrame(gantt_records), use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
