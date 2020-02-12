from src.circuit_dag import CircuitDAG, Vertex
from src.gate import Gate

GARBAGE = 'IGNORE_THIS_GATE'

def topological_sort_help(v, visited, stack):
    visited.add(v.get_id())

    for v_neighbor in v.get_output():
        if not v_neighbor.get_id() in visited:
            topological_sort_help(v_neighbor, visited, stack)


    stack.insert(0, v)

def topological_sort(cd):
    v_map = cd.get_vertex_map()
    visited = set()
    stack = []

    for _,v in v_map.items():
        if not v.get_id() in visited:
            topological_sort_help(v, visited, stack)

    return stack

def circuit_dag_to_netlist(cd):
    netlist = []

    top_sort_dag = topological_sort(cd)
    for v in top_sort_dag:
        netlist.append(v.get_gate().copy())

    return netlist


def netlist_to_circuit_dag(num_qubits, netlist):
    return CircuitDAG(num_qubits, netlist)
