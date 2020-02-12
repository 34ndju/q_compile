from src.circuit_dag import CircuitDAG, Vertex, get_all_vertices_on_wires
from src.gate import Gate
from src.adapter import *

GARBAGE = 'IGNORE_THIS_GATE'

def get_2_vertices_forward(v):
    for vertex1 in v.get_output():
        for vertex2 in vertex1.get_output():
            yield vertex1, vertex2

# type: (Vertex, Vertex) -> None
def swap_2_vertex_neighbors(v1, v2):
    # v1 is to the left of v2
    assert v2 in v1.get_output()
    assert v1 in v2.get_input()
    v1.remove_output(v2)
    v2.remove_input(v1)

    v1_wires = set(v1.get_gate_all_qubits())
    v2_wires = set(v2.get_gate_all_qubits())

    v2_new_predecessors = get_all_vertices_on_wires(v1.get_input(), v2_wires)
    for v in v2_new_predecessors:
        # v has 1+ wires that host both v1 and v2
        v.add_output(v2)
        v2.add_input(v)
        if len(set(v.get_gate_all_qubits()).difference(set(v2.get_gate_all_qubits())).intersection(set(v1.get_gate_all_qubits()))) == 0:
            # when v1 and v2 swap, v2 will completely barricade v from v1
            v.remove_output(v1)
            v1.remove_input(v)

    v1_new_children = get_all_vertices_on_wires(v2.get_output(), v1_wires)
    for v in v1_new_children:
        v.add_input(v1)
        v1.add_output(v)
        if len(set(v.get_gate_all_qubits()).difference(set(v1.get_gate_all_qubits())).intersection(set(v2.get_gate_all_qubits()))) == 0:
            # barrier
            v.remove_input(v2)
            v2.remove_output(v)

    v1.add_input(v2)
    v2.add_output(v1)

# type: (CircuitDAG, Vertex) -> Bool
# returns True is successfuly cummuted, returns false otherwise
def single_R_z_commute(v):
    assert v.get_gate_name() == 'R_z'

    v_wire = v.get_gate_target()
    v1 = list(v.get_output())[0]

    # rule 1
    if v1.get_gate_name() == 'H':
        v2 = list(v1.get_output())[0]
        if v2.get_gate_name() == 'CNOT' and v2.get_gate_target() == v_wire:
            v3 = None
            for v_cand in v2.get_output():
                if v_cand.get_gate_all_qubits() == [v_wire] and v_cand.get_gate_name() == 'H':
                    v3 = v_cand
            if v3 is not None:
                swap_2_vertex_neighbors(v, v1)
                swap_2_vertex_neighbors(v, v2)
                swap_2_vertex_neighbors(v, v3)
                return True

    # rule 2
    if v1.get_gate_name() == 'CNOT' and v1.get_gate_target() == v_wire:
        control_wire = v1.get_gate_controls()[0]
        v2 = None
        for v_cand in v1.get_output():
            if v_cand.get_gate_all_qubits() == [v_wire] and v_cand.get_gate_name() == 'R_z':
                v2 = v_cand
        if v2 is not None:
            v3 = list(v2.get_output())[0]
            if v3.get_gate_name() == 'CNOT' and v3.get_gate_target() == v_wire and v3.get_gate_controls() == [control_wire]:
                swap_2_vertex_neighbors(v, v1)
                swap_2_vertex_neighbors(v, v2)
                swap_2_vertex_neighbors(v, v3)
                return True

    # rule 3
    if v1.get_gate_name() == 'CNOT' and v1.get_gate_controls() == [v_wire]:
        swap_2_vertex_neighbors(v, v1)
        return True

    return False

def rotation_merge(cd, v):
    if len(v.get_output()) == 1 and list(v.get_output())[0].get_gate_name() == 'R_z':
        next_R_z = list(v.get_output())[0]
        next_R_z_theta = next_R_z.get_gate().get_theta()
        new_theta = v.get_gate().get_theta() + next_R_z_theta
        v.get_gate().set_theta(new_theta)
        cd.remove_vertex_and_merge(next_R_z)
        return True
    return False

def exists_path_to_vertex(v, end_v):
    if v == end_v:
        return True

    for v_neighbor in v.get_output():
        if exists_path_to_vertex(v_neighbor, end_v):
            return True

    return False


def single_cnot_commute(v):
    assert v.get_gate_name() == 'CNOT'

    # rule 1, 2
    for v1 in v.get_output():
        if v1.get_gate_name() == 'CNOT':
            # rule 1
            if v.get_gate_controls() != v1.get_gate_controls() and v.get_gate_target() == v1.get_gate_target():
                other_vertex = None
                control_wire = v.get_gate_controls()[0]
                for v_other in v.get_output():
                    if control_wire in set(v_other.get_gate_all_qubits()):
                        other_vertex = v_other
                        break
                if other_vertex is None or not exists_path_to_vertex(other_vertex, v1):
                    swap_2_vertex_neighbors(v, v1)
                    return True

            # rule 2
            if v.get_gate_controls() == v1.get_gate_controls() and v.get_gate_target() != v1.get_gate_target():
                other_vertex = None
                target_wire = v.get_gate_target()
                for v_other in v.get_output():
                    if target_wire in set(v_other.get_gate_all_qubits()):
                        other_vertex = v_other
                        break
                if other_vertex is None or not exists_path_to_vertex(other_vertex, v1):
                    swap_2_vertex_neighbors(v, v1)
                    return True

    # rule 3
    for v1, v2 in get_2_vertices_forward(v):
        if v1.get_gate_name() == 'H' and v1.get_gate_target() == v.get_gate_target():
            if v2.get_gate_name() == 'CNOT' and v2.get_gate_controls() == [v.get_gate_target()] and [v2.get_gate_target()] != v.get_gate_controls():
                for v3 in v2.get_output():
                    if v3.get_gate_name() == 'H' and v2.get_gate_controls() == [v3.get_gate_target()]:
                        swap_2_vertex_neighbors(v,v1)
                        swap_2_vertex_neighbors(v,v2)
                        swap_2_vertex_neighbors(v,v3)
                        return True

    return False

def cnot_merge(cd, v):
    assert v.get_gate_name() == 'CNOT'
    list_out = list(v.get_output())

    if len(list_out) == 1 and list_out[0].get_gate_name() == 'CNOT' and list_out[0].get_gate_target() == v.get_gate_target() and list_out[0].get_gate_controls() == v.get_gate_controls():
        next_cnot = list_out[0]
        cd.remove_vertex_and_merge(next_cnot)
        cd.remove_vertex_and_merge(v)
        return True
    return False


def find_cnot_combination(cd, v):
    assert v.get_gate_name() == 'CNOT'

    snapshot_nl = circuit_dag_to_netlist(cd)
    if cnot_merge(cd, v):
        return cd

    while single_cnot_commute(v):
        if cnot_merge(cd, v):
            return cd

    snapshot_cd = netlist_to_circuit_dag(cd.get_num_qubits(), snapshot_nl)
    return snapshot_cd

# type: (CircuitDAG, Vertex) -> CircuitDAG
def find_R_z_combination(cd, v):
    assert v.get_gate_name() == 'R_z'
    # make deep copy, then find combinations
    snapshot_nl = circuit_dag_to_netlist(cd)

    if rotation_merge(cd, v):
        return cd

    while single_R_z_commute(v):
        if rotation_merge(cd, v):
            return cd

    snapshot_cd = netlist_to_circuit_dag(cd.get_num_qubits(), snapshot_nl)
    return snapshot_cd
