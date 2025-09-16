import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_pydot import graphviz_layout

class TaskNode:
    def __init__(self, node_id, children, operator):
        self.id = node_id
        self.children = children          # list of child node IDs
        self.parents = []                 # will be filled in later
        self.operator = operator
        # scheduling attributes
        self.asap = None
        self.alap = None
        self.slack = None
        self.ready_time = None
        self.start_time = None
        self.finish_time = None

def load_graph(file_path):
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f.readlines()]
    
    total_nodes = int(lines[0])
    nodes = {}

    for line in lines[1:]:
        node_str, children_str, op_str = line.split(',')
        node_id = int(node_str.strip())
        operator = op_str.strip()
        # parse children list "[3 4 7]" into integers
        if children_str.strip() == "[]":
            children = []
        else:
            children = [int(x) for x in children_str.strip()[1:-1].split()]
        nodes[node_id] = TaskNode(node_id, children, operator)

    # assign parents for each node
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

def draw_task_graph(nodes):
    G = nx.DiGraph()

    # add nodes with labels showing operator and ASAP time
    for node in nodes.values():
        label = f"{node.id}\n{node.operator}\nASAP={node.asap}"
        G.add_node(node.id, label=label)

    # add edges from parent to child
    for node in nodes.values():
        for child_id in node.children:
            G.add_edge(node.id, child_id)

    # hierarchical DAG layout (Cleaner Visualization, not really needed)
    pos = graphviz_layout(G, prog='dot')
    labels = nx.get_node_attributes(G, 'label')

    plt.figure(figsize=(10,6))
    nx.draw(G, pos, labels=labels, with_labels=True,
            node_size=2000, node_color='lightblue',
            font_size=10, font_weight='bold', arrowsize=20)
    plt.title("Task Graph - DAG Layout")
    plt.show()

if __name__ == "__main__":
    graph_file = "mp2_example_files/graph.txt"
    timing_file = "mp2_example_files/timing.txt"
    constraints_file = "mp2_example_files/constraints.txt"

    tasks, num_tasks = load_graph(graph_file)
    latencies = load_timing(timing_file)
    hw_constraints = load_constraints(constraints_file)

    print("Graph Nodes:")
    for t in tasks.values():
        print(f"ID: {t.id}, Children: {t.children}, Parents: {t.parents}, Operator: {t.operator}")

    draw_task_graph(tasks)
