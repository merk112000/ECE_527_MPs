# ECE 527 MP2: List Scheduling Scheduler

This project implements **ASAP, ALAP, Slack, and List Scheduling** for task graphs with operator latencies and hardware constraints, as specified in the MP2 assignment.

It is written in **Python 3.8+** and generates four output files:

* `asap.txt` – earliest start schedule
* `alap.txt` – latest start schedule
* `slack.txt` – slack for each node
* `list_scheduling.txt` – final scheduled order using list scheduling

---

## Requirements

* Python 3.8 or later
* Packages (install via pip):

```bash
pip install networkx
pip install pydot
```

> **Note:** `pydot` is used for graph visualization; optional if you skip generating diagrams.

---

## Project Structure

```
MP2/
├── scheduler.py        # Main program
├── inputs/             # Graph, timing, constraints files
├── mp2_outputs/        # Output files will be written here
├── README.md
└── venv/               # Optional Python virtual environment
```

---

## Usage

Run the program with **three positional arguments**:

```bash
python scheduler.py <graph_file> <timing_file> <constraints_file>
```

* `<graph_file>` – Graph input file describing nodes, children, and operator
* `<timing_file>` – Operator latencies
* `<constraints_file>` – Number of hardware units per operator

Outputs are written automatically to the `mp2_outputs` folder.

---

## Windows Instructions

1. **Install Python**
   Download from [python.org](https://www.python.org/downloads/) and ensure `python` is added to PATH.

2. **Open Command Prompt**
   Navigate to the project folder:

   ```cmd
   cd C:\path\to\MP2
   ```

3. **Create Virtual Environment (optional)**

   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

4. **Install Dependencies**

   ```cmd
   pip install networkx pydot
   ```

5. **Run the Scheduler**

   ```cmd
   python scheduler.py inputs\graph.txt inputs\timing.txt inputs\constraints.txt
   ```

---

## macOS Instructions

1. **Install Python** (if not already installed)

   ```bash
   brew install python
   ```

2. **Open Terminal**
   Navigate to the project folder:

   ```bash
   cd /Users/username/Documents/MP2
   ```

3. **Create Virtual Environment (optional)**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install Dependencies**

   ```bash
   pip install networkx pydot
   ```

5. **Run the Scheduler**

   ```bash
   python3 scheduler.py inputs/graph.txt inputs/timing.txt inputs/constraints.txt
   ```

---

## Notes

* Ensure input files are properly formatted according to MP2 instructions.
* List scheduling respects **hardware constraints** and **slack-based priority**, with ties broken by **lowest node ID**.
* Output files match the **autograder’s expected format exactly**.
