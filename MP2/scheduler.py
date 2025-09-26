import os
from collections import deque, defaultdict
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_pydot import graphviz_layout

# Task Node
class TaskNode:
    def __init__(self, node_id, children, operator):
        self.id = node_id
        self.children = children
        self.parents = []
        self.operator = operator
        self.asap = None
        self.alap = None
        self.slack = None
        self.ready_time = None
        self.start_time = None
        self.finish_time = None
        self.running_time = None
        self.priority = None

# File Parsing
def load_graph(file_path):
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f.readlines()]

    total_nodes = int(lines[0])
    nodes = {}
    for line in lines[1:]:
        node_str, children_str, op_str = line.split(',')
        node_id = int(node_str.strip())
        operator = op_str.strip()
        children = [int(x) for x in children_str.strip()[1:-1].split()] if children_str.strip() != "[]" else []
        nodes[node_id] = TaskNode(node_id, children, operator)

    # populate parents
    for node in nodes.values():
        for child_id in node.children:
            nodes[child_id].parents.append(node.id)

    return nodes, total_nodes

def load_timing(file_path):
    timing = {}
    with open(file_path, 'r') as f:
        for line in f:
            op, cycles = line.strip().split()
            timing[op] = int(cycles)
    return timing

def load_constraints(file_path):
    constraints = {}
    with open(file_path, 'r') as f:
        for line in f:
            op, count = line.strip().split()
            constraints[op] = int(count)
    return constraints

# Scheduling
def compute_asap(nodes, timing):
    queue = deque([n for n in nodes.values() if not n.parents])
    for n in queue:
        n.asap = 0

    while queue:
        node = queue.popleft()
        finish = node.asap + timing[node.operator]
        for child_id in node.children:
            child = nodes[child_id]
            proposed = finish
            if child.asap is None or proposed > child.asap:
                child.asap = proposed
            queue.append(child)

def compute_alap(nodes, timing):
    max_finish = max(n.asap + timing[n.operator] for n in nodes.values())
    queue = deque([n for n in nodes.values() if not n.children])
    for n in queue:
        n.alap = max_finish - timing[n.operator]

    while queue:
        node = queue.popleft()
        start_time = node.alap
        for parent_id in node.parents:
            parent = nodes[parent_id]
            proposed = start_time - timing[parent.operator]
            if parent.alap is None or proposed < parent.alap:
                parent.alap = proposed
            queue.append(parent)

def compute_slack(nodes):
    for n in nodes.values():
        n.slack = n.alap - n.asap

# List Scheduling
def list_scheduling(nodes, timing, constraints):
    unscheduled = set(nodes.keys())
    scheduled_order = []
    time = 0

    # Track units in use: operator -> list of finish times
    running_units = defaultdict(list)

    # Initialize node priority = slack
    for n in nodes.values():
        n.priority = n.slack

    while unscheduled:
        # 1. Identify ready nodes
        ready_nodes = []
        for n_id in unscheduled:
            node = nodes[n_id]
            if all(nodes[p].finish_time is not None for p in node.parents):
                node.ready_time = max([nodes[p].finish_time for p in node.parents], default=-1) + 1
                if node.ready_time <= time:
                    ready_nodes.append(node)

        # 2. Sort by priority (lower = higher), then Node ID
        ready_nodes.sort(key=lambda n: (n.priority, n.id))

        scheduled_this_cycle = []

        for node in ready_nodes:
            # Clean finished units
            running_units[node.operator] = [ft for ft in running_units[node.operator] if ft >= time]

            # Schedule if hardware unit is available
            if len(running_units[node.operator]) < constraints[node.operator]:
                node.running_time = time
                node.start_time = time
                node.finish_time = node.start_time + timing[node.operator] - 1
                running_units[node.operator].append(node.finish_time)
                scheduled_order.append(node)
                unscheduled.remove(node.id)
                scheduled_this_cycle.append(node.id)
            else:
                # Node is ready but blocked, decrease priority
                node.priority = node.priority - 1

        # 3. Advance time
        time += 1

    total_time = max(n.finish_time for n in scheduled_order)
    return scheduled_order, total_time


# Output Functions
def write_asap(nodes, folder):
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "asap.txt"), 'w') as f:
        for n_id in sorted(nodes):
            f.write(f"Node {n_id}: t={nodes[n_id].asap}\n")
        finish_time = max(n.asap + timing[n.operator] for n in nodes.values())
        f.write(f"Finished t={finish_time}\n")

def write_alap(nodes, folder):
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "alap.txt"), 'w') as f:
        for n_id in sorted(nodes):
            f.write(f"Node {n_id}: t={nodes[n_id].alap}\n")
        finish_time = max(n.alap + timing[n.operator] for n in nodes.values())
        f.write(f"Finished t={finish_time}\n")

def write_slack(nodes, folder):
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "slack.txt"), 'w') as f:
        for n_id in sorted(nodes):
            f.write(f"Node {n_id}: slack={nodes[n_id].slack}\n")

def write_list_schedule(nodes, folder):
    os.makedirs(folder, exist_ok=True)
    # Sort nodes by ID
    nodes.sort(key=lambda n: n.id)
    with open(os.path.join(folder, "list_scheduling.txt"), 'w') as f:
        for node in nodes:
            line = f"Node {node.id}: Ready t={node.ready_time}; Running t={node.running_time}; Finished t={node.finish_time}\n"
            f.write(line)
        finish_time = max(n.finish_time for n in nodes) + 1
        f.write(f"Finished t={finish_time}\n")


# Visualization (with List Scheduling)
def draw_task_graph(nodes):
    G = nx.DiGraph()
    for node in nodes.values():
        label = (f"{node.id}\n{node.operator}\n"
                 f"ASAP={node.asap}\nALAP={node.alap}\nSlack={node.slack}\n"
                 f"Ready={node.ready_time}\nStart={node.start_time}\nFinish={node.finish_time-1}")
        G.add_node(node.id, label=label)
    for node in nodes.values():
        for child_id in node.children:
            G.add_edge(node.id, child_id)

    pos = graphviz_layout(G, prog='dot')
    labels = nx.get_node_attributes(G, 'label')

    plt.figure(figsize=(14,10))
    nx.draw(G, pos, labels=labels, with_labels=True,
            node_size=8500, node_color='lightblue',
            font_size=10, font_weight='bold', arrowsize=40)
    plt.title("Task Graph with ASAP, ALAP, Slack, and List Scheduling")
    plt.show()


# Comparison/Grading
def grade_outputs(folder, expected_folder):
    import difflib
    all_files = ["asap.txt", "alap.txt", "slack.txt", "list_scheduling.txt"]
    score = 0
    for file in all_files:
        path_generated = os.path.join(folder, file)
        path_expected = os.path.join(expected_folder, file)
        with open(path_generated, 'r') as f1, open(path_expected, 'r') as f2:
            gen_lines = f1.readlines()
            exp_lines = f2.readlines()
            if gen_lines == exp_lines:
                score += 1
            else:
                print(f"Mismatch in {file}:")
                for line in difflib.unified_diff(exp_lines, gen_lines, fromfile='expected', tofile='generated', lineterm=''):
                    print(line)
    print(f"Total score: {score}/{len(all_files)}")

# Main
if __name__ == "__main__":
    graph_file = "mp2_example_files/graph.txt"
    timing_file = "mp2_example_files/timing.txt"
    constraints_file = "mp2_example_files/constraints.txt"

    output_folder = "mp2_outputs"
    expected_folder = "mp2_example_files"

    tasks, num_tasks = load_graph(graph_file)
    timing = load_timing(timing_file)
    constraints = load_constraints(constraints_file)

    compute_asap(tasks, timing)
    compute_alap(tasks, timing)
    compute_slack(tasks)

    scheduled_order, total_time = list_scheduling(tasks, timing, constraints)

    write_asap(tasks, output_folder)
    write_alap(tasks, output_folder)
    write_slack(tasks, output_folder)
    write_list_schedule(scheduled_order, output_folder)

    draw_task_graph(tasks)

    print(f"All output files written to '{output_folder}'")
    grade_outputs(output_folder, expected_folder)
