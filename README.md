# ⚡ CPU Scheduling Simulator

An interactive, beginner-friendly **Operating Systems Mini Project** built with **Python** and **Streamlit**.

This simulator visualizes and compares fundamental CPU scheduling algorithms, handles arbitrary process arrival times, identifies CPU idle periods, generates dynamic **Gantt Charts**, and computes essential scheduling metrics like Turnaround Time, Waiting Time, Response Time, and CPU Utilization.

---

## 🚀 Features

- **3 Core Scheduling Algorithms**:
  - **First-Come, First-Served (FCFS)** (Non-preemptive)
  - **Shortest Job First (SJF)** (Non-preemptive)
  - **Round Robin (RR)** (Preemptive with configurable Time Quantum)
- **Side-by-Side Algorithm Comparison**:
  - Compare FCFS, SJF, and Round Robin on the exact same dataset.
  - Interactive performance bar chart for Average Waiting Time and Turnaround Time.
- **Dynamic Gantt Chart Visualization**:
  - Color-coded process blocks with exact start and finish time markers.
  - Explicit hatched indicators for **CPU IDLE** periods when no process is ready.
  - Detailed step-by-step execution timeline log.
- **Complete Metric Calculations**:
  - Completion Time ($CT$)
  - Turnaround Time ($TAT = CT - AT$)
  - Waiting Time ($WT = TAT - BT$)
  - Response Time ($RT = \text{First Run Time} - AT$)
  - Averages: Average Waiting Time, Average Turnaround Time, Average Response Time
  - System performance: CPU Utilization (%) and Makespan (total completion time)
- **User-Friendly Input**:
  - Interactive spreadsheet-like data editor to add, edit, or delete processes.
  - **Pre-loaded Sample Scenarios** (Textbook standard, CPU idle gaps, SJF showdown, Simultaneous arrivals).
  - Validation to prevent negative arrival times, zero burst times, or duplicate Process IDs.
- **Data Export**:
  - One-click CSV download for simulation results.
- **Automated Unit Testing**:
  - Comprehensive `pytest` test suite verifying scheduling calculations and edge cases.

---

## 📁 Project Structure

```text
CPU scheduling simulator/
│
├── app.py              # Streamlit web application & user interface
├── scheduler.py        # Core scheduling algorithms & metric computation engine
├── test_scheduler.py   # Automated unit tests covering all algorithms & edge cases
├── requirements.txt    # Project dependencies (streamlit, pandas, pytest)
├── README.md           # Project documentation and user guide
└── .gitignore          # Git ignore configuration
```

---

## 🧠 Scheduling Formulas & Concepts

| Metric | Formula | Description |
| :--- | :--- | :--- |
| **Arrival Time ($AT$)** | User Input | Time at which a process enters the ready queue. |
| **Burst Time ($BT$)** | User Input | Total CPU execution time required by the process. |
| **Completion Time ($CT$)** | Algorithm output | Time at which the process finishes its final execution. |
| **Turnaround Time ($TAT$)** | $CT - AT$ | Total elapsed time from process arrival to termination. |
| **Waiting Time ($WT$)** | $TAT - BT$ | Total time the process spent waiting in the ready queue. |
| **Response Time ($RT$)** | $\text{Start Time} - AT$ | Time from arrival until first execution on the CPU. |
| **CPU Utilization** | $\frac{\text{Total Time} - \text{Idle Time}}{\text{Total Time}} \times 100\%$ | Percentage of time the CPU was actively executing processes. |

---

## 🛠️ Installation & Setup

### 1. Prerequisites
Ensure you have **Python 3.9+** installed on your system. Verify with:
```bash
python --version
```

### 2. (Optional) Create a Virtual Environment
It is recommended to run inside a virtual environment:
```bash
# Windows (PowerShell / Command Prompt)
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install all required libraries using `pip`:
```bash
python -m pip install -r requirements.txt
```

---

## 🧪 Running Automated Tests

Run the test suite to verify algorithm calculations, idle period handling, and validation:

```bash
python -m pytest test_scheduler.py -v
```

All tests should pass:
```text
test_scheduler.py::test_fcfs_basic PASSED
test_scheduler.py::test_fcfs_with_idle_periods PASSED
test_scheduler.py::test_sjf_non_preemptive_basic PASSED
test_scheduler.py::test_round_robin_basic PASSED
test_scheduler.py::test_round_robin_with_idle PASSED
test_scheduler.py::test_unsorted_input_order PASSED
test_scheduler.py::test_input_validation PASSED
test_scheduler.py::test_run_all_schedulers PASSED
```

---

## 💻 Launching the Application

Start the Streamlit simulator with:

```bash
python -m streamlit run app.py
```

Streamlit will launch a local web server (usually at `http://localhost:8501`). Your default browser will open automatically.

### How to Use:
1. **Choose an Algorithm** in the left sidebar (FCFS, Non-Preemptive SJF, Round Robin, or Compare All).
2. If **Round Robin** is selected, set your desired **Time Quantum** (e.g. 2, 3, 4).
3. Select a **Sample Scenario** from the dropdown or manually edit rows in the **Process Inputs** table.
4. View the generated **Gantt Chart**, key summary metrics, and the detailed calculation table.
5. Click **Download Results as CSV** if you need to submit or export your output table.

---

## 📝 Example Walkthrough (Round Robin, Quantum = 2)

### Input Processes:
| Process | Arrival Time | Burst Time |
| :---: | :---: | :---: |
| **P1** | 0 | 5 |
| **P2** | 1 | 3 |
| **P3** | 2 | 1 |

### Execution Timeline (Gantt Chart):
`[0-2: P1] -> [2-4: P2] -> [4-5: P3] -> [5-7: P1] -> [7-8: P2] -> [8-9: P1]`

### Result Metrics:
| Process | AT | BT | Start Time | CT | Turnaround Time (TAT) | Waiting Time (WT) | Response Time (RT) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **P1** | 0 | 5 | 0 | 9 | 9 | 4 | 0 |
| **P2** | 1 | 3 | 2 | 8 | 7 | 4 | 1 |
| **P3** | 2 | 1 | 4 | 5 | 3 | 2 | 2 |

- **Average Waiting Time**: $3.33 \text{ ms}$
- **Average Turnaround Time**: $6.33 \text{ ms}$
- **CPU Utilization**: $100\%$

---

## 👨‍💻 Author & Submission Info
- **Project Name:** CPU Scheduling Simulator
- **Course:** Operating Systems
- **Technology Stack:** Python 3, Streamlit, Pandas, Pytest
