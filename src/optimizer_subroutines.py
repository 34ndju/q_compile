from src.circuit_dag import CircuitDAG, Vertex, get_all_vertices_on_wires
from src.gate import Gate
from src.parser import Parser
from queue import Queue

GARBAGE = 'IGNORE_THIS_GATE'

def circuit_dag_to_netlist(cd):
    netlsit = []
    for iden, vertex in cd.get_vertex_map().items():
        netlist.append(vertex.get_gate().copy())

    return netlist

def netlist_to_circuit_dag(num_qubits, netlist):
    return CircuitDAG(num_qubits, netlist)
    

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


# type: (CirctuitDAG) -> None
def hadamard_gate_reduction(cd):
    q = Queue()
    H_gate_ids = cd.collect_gate_ids('H')  # type: set
    for iden in H_gate_ids:
        q.put(iden)

    while not q.empty():
        H_gate_id = q.get()
        H_vertex = cd.get_vertex_map().get(H_gate_id, None)

        if H_vertex is None or H_vertex.get_gate_name() != 'H':
            # this happens when a previous rewrite rule changes the gate of a vertex or deletes the vertex
            continue
    
        # rule 1, rule 2
        for vertex1, vertex2 in get_2_vertices_forward(H_vertex):
            if vertex1.get_gate_name() == 'P' and vertex2.get_gate_name() == 'H': 
                H_vertex.set_gate_name('P_dag')
                vertex1.set_gate_name('H')
                vertex2.set_gate_name('P_dag')
                q.put(vertex1.get_id())
                break
            elif vertex1.get_gate_name() == 'P_dag' and vertex2.get_gate_name() == 'H':
                H_vertex.set_gate_name('P')
                vertex1.set_gate_name('H')
                vertex2.set_gate_name('P')
                q.put(vertex1.get_id())
                break

        # rule 3
        H_target = H_vertex.get_gate_target()
        for vertex1, vertex2 in get_2_vertices_forward(H_vertex):
            if vertex1.get_gate_name() == 'CNOT' and vertex2.get_gate_name() == 'H':
                cnot_gate = vertex1.get_gate()
                if cnot_gate.get_controls() == [H_target] and vertex2.get_gate().get_target() == H_target:
                    # H_target wire is correct
                    cnot_target = cnot_gate.get_target()
                    inp = vertex1.get_input()
                    out = vertex1.get_output()
                    assert len(inp) == 2 and len(out) == 2
                    assert cnot_target != H_target
                    
                    # bottom-left
                    list_inp = list(inp)
                    if list_inp[0].get_gate_target() == cnot_target:
                        bl_v = list_inp[0]
                    else:
                        bl_v = list_inp[1]

                    # bottom-right
                    list_out = list(out)
                    if list_out[0].get_gate_target() == cnot_target:
                        br_v = list_out[0]
                    else:
                        br_v = list_out[1]
            
                    if bl_v.get_gate_name() == br_v.get_gate_name() == 'H':
                        # bottom wire is correct
                        # remove the Hadamards and swap the target and control for CNOT
                        cd.remove_vertex_and_merge(H_vertex)
                        cd.remove_vertex_and_merge(vertex2) 
                        cd.remove_vertex_and_merge(bl_v)
                        cd.remove_vertex_and_merge(br_v)

                        vertex1.set_target(H_target)
                        vertex1.set_controls([cnot_target])
                        break

        # rule 4
        for vertex1, vertex2 in get_2_vertices_forward(H_vertex):
            if vertex1.get_gate_name() == 'P' and vertex2.get_gate_name() == 'CNOT' and vertex2.get_gate_target() == H_target:
                for vertex3, vertex4 in get_2_vertices_forward(vertex2):
                    if vertex3.get_gate_target() == vertex4.get_gate_target() == H_target and vertex3.get_gate_name() == 'P_dag' and vertex4.get_gate_name() == 'H':
                        # wires are correct
                        cd.remove_vertex_and_merge(H_vertex)
                        cd.remove_vertex_and_merge(vertex4)
                        vertex1.set_gate_name('P_dag')
                        vertex3.set_gate_name('P')
                        break

        # rule 5
        for vertex1, vertex2 in get_2_vertices_forward(H_vertex):
            if vertex1.get_gate_name() == 'P_dag' and vertex2.get_gate_name() == 'CNOT' and vertex2.get_gate_target() == H_target:
                for vertex3, vertex4 in get_2_vertices_forward(vertex2):
                    if vertex3.get_gate_target() == vertex4.get_gate_target() == H_target and vertex3.get_gate_name() == 'P' and vertex4.get_gate_name() == 'H':
                        # wires are correct
                        cd.remove_vertex_and_merge(H_vertex)
                        cd.remove_vertex_and_merge(vertex4)
                        vertex1.set_gate_name('P')
                        vertex3.set_gate_name('P_dag')
                        break



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
    
# TODO
def find_R_z_combination(cd, v):
    assert v.get_gate_name() == 'R_z'
    # make deep copy, then find combinations
    pass
    
    
# TODO
# type: (CircuitDAG) -> None
def single_qubit_gate_cancellation(cd):
    pass
 
