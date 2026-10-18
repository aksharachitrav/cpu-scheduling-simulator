# ⚡ CPU Scheduling Simulator

An interactive, beginner-friendly **Operating Systems Mini Project** built with **Python** and **Streamlit**.

This simulator visualizes and compares CPU scheduling algorithms, handles process arrival times, identifies CPU idle periods, generates Gantt charts, and calculates scheduling metrics such as turnaround time, waiting time, response time, and CPU utilization.

## 🚀 Features

- **Three scheduling algorithms:** First-Come, First-Served (FCFS), Shortest Job First (SJF), and Round Robin (RR).
- **Algorithm comparison:** Compare FCFS, SJF, and RR using the same process dataset.
- **Gantt chart visualization:** View process execution, start and finish times, and CPU idle periods.
- **Scheduling metrics:** Calculate completion time, turnaround time, waiting time, response time, and CPU utilization.
- **Interactive process input:** Add, edit, or delete processes using the data editor.
- **Sample scenarios:** Explore predefined process scheduling examples.
- **CSV export:** Download simulation results.
- **Automated testing:** Verify scheduling algorithms using pytest.

## 📁 Project Structure

```text
CPU scheduling simulator/
├── app.py
├── scheduler.py
├── test_scheduler.py
├── requirements.txt
├── README.md
└── .gitignore
```

## 🧠 Scheduling Formulas

| Metric | Formula |
|---|---|
| Completion Time (CT) | Time when a process finishes |
| Turnaround Time (TAT) | CT − Arrival Time |
| Waiting Time (WT) | TAT − Burst Time |
| Response Time (RT) | First Start Time − Arrival Time |
| CPU Utilization | (Busy Time / Total Elapsed Time) × 100% |

## 🛠️ Installation and Setup

### 1. Prerequisites

Install Python 3.9 or later and check your version:

```bash
python --version
```

### 2. Install Dependencies

Open PowerShell in the project folder and run:

```bash
python -m pip install -r requirements.txt
```

### 3. Run Automated Tests

```bash
python -m pytest test_scheduler.py -v
```

### 4. Launch the Application

```bash
python -m streamlit run app.py
```

Open the local URL shown in the terminal, usually `http://localhost:8501`.

## 💻 How to Use

1. Choose FCFS, SJF, Round Robin, or Compare All in the application.
2. For Round Robin, configure the time quantum.
3. Select a sample scenario or enter process arrival and burst times.
4. Review the Gantt chart and scheduling metrics.
5. Download the results as a CSV file if needed.

## 🎓 Project Information

- **Project:** CPU Scheduling Simulator
- **Course:** Operating Systems
- **Technology:** Python, Streamlit, Pandas, and Pytest
- **Purpose:** To demonstrate and compare CPU scheduling algorithms interactively.
