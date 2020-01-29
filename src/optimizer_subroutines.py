from src.circuit_dag import CircuitDAG, Vertex
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
                    if vertex3.get_gate_target() == vertex4().get_gate_target() == H_target and vertex3.get_gate_name() == 'P' and vertex4.get_gate_name() == 'H':
                        # wires are correct
                        cd.remove_vertex_and_merge(H_vertex)
                        cd.remove_vertex_and_merge(vertex4)
                        vertex1.set_gate_name('P')
                        vertex3.set_gate_name('P_dag')
                        break




