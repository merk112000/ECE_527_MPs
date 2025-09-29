import os
from collections import deque, defaultdict

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
def write_asap(nodes):
    with open("asap.txt", 'w') as f:
        for n_id in sorted(nodes):
            f.write(f"Node {n_id}: t={nodes[n_id].asap}\n")
        finish_time = max(n.asap + timing[n.operator] for n in nodes.values())
        f.write(f"Finished t={finish_time}\n")

def write_alap(nodes):
    with open("alap.txt", 'w') as f:
        for n_id in sorted(nodes):
            f.write(f"Node {n_id}: t={nodes[n_id].alap}\n")
        finish_time = max(n.alap + timing[n.operator] for n in nodes.values())
        f.write(f"Finished t={finish_time}\n")

def write_slack(nodes):
    with open("slack.txt", 'w') as f:
        for n_id in sorted(nodes):
            f.write(f"Node {n_id}: slack={nodes[n_id].slack}\n")

def write_list_schedule(nodes):
    # Sort nodes by ID
    nodes.sort(key=lambda n: n.id)
    with open("list_scheduling.txt", 'w') as f:
        for node in nodes:
            line = f"Node {node.id}: Ready t={node.ready_time}; Running t={node.running_time}; Finished t={node.finish_time}\n"
            f.write(line)
        finish_time = max(n.finish_time for n in nodes) + 1
        f.write(f"Finished t={finish_time}\n")

# Main
if __name__ == "__main__":
    graph_file = "graph.txt"
    timing_file = "timing.txt"
    constraints_file = "constraints.txt"

    tasks, num_tasks = load_graph(graph_file)
    timing = load_timing(timing_file)
    constraints = load_constraints(constraints_file)

    compute_asap(tasks, timing)
    compute_alap(tasks, timing)
    compute_slack(tasks)

    scheduled_order, total_time = list_scheduling(tasks, timing, constraints)

    write_asap(tasks)
    write_alap(tasks)
    write_slack(tasks)
    write_list_schedule(scheduled_order)


    print(f"All output files written")
