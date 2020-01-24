from gate import Gate

class Vertex:
    def __init__(self, iden, gate):
        self.gate = gate
        self.iden = iden
        self.input = set() # type: Set[Vertex]
        self.output = set() # type: Set[Vertex]

    def get_id(self):
        return self.iden
   
    def get_gate(self):
        return self.gate

    # type: (None) -> Int
    def get_gate_target(self):
        return self.gate.get_target()

    def get_gate_name(self):
        return self.gate.get_name()

    # type: (None) -> List[Int]
    def get_gate_all_qubits(self):
        return self.gate.get_all_qubits()

    def get_input(self):
        return self.input

    def get_output(self):
        return self.output

    def add_input(self, inp):
        # search for repeats
        if type(inp) == Vertex:
            self.input.add(inp)
        elif type(inp) == list:
            self.input.append(inp)

    def add_output(self, out):
        # search for repeats
        if type(out) == Vertex:
            self.output.add(out)
        elif type(out) == list:
            self.output.append(out)

    def remove_input(self, inp):
        self.input.remove(inp)

    def remove_output(self, out):
        self.output.remove(out)


    def set_target(self, target)
        self.target = target

    def set_controls(self, controls):
        self.controls = controls


class CircuitDAG:
    def __init__(self, num_qubits, netlist):
        self.vertex_map = {}
        
        lru_qubits = [-1] * num_qubits
        for i, gate in enumerate(netlist):
            vertex = Vertex(i, gate.copy())
            self.vertex_map[i] = vertex
           
            # Find any predecessors if they exist to update DAG, then update the LRU per qubit with the current gate
            all_qubits = gate.get_all_qubits()
            for qub in all_qubits:
                lru_gate_index = lru_qubits[qub]
                if lru_gate_index > -1:
                    in_vertex = self.vertex_map[lru_gate_index]
                    vertex.add_input(in_vertex)
                    in_vertex.add_output(vertex)
                lru_qubits[qub] = vertex.get_id()

    def get_vertex_map(self):
        return self.vertex_map


    def collect_gate_ids(self, gate_name):
        ids = set()
        for iden, vertex in self.vertex_map.items():
            if vertex.get_gate().get_name() == gate_name:
                ids.add(vertex.get_id())
        return ids


    # type: (List[Vertex], Set[Int]) -> List[Vertex]
    def get_all_vertices_on_wires(self, vertices, wires)
        ret = []
        for vertex in vertices:
            if len(set(vertex.get_gate_all_qubits()).intersection(wires)) > 0:
                ret.append(vertex)
        return ret
        

    # TODO test
    def remove_vertex_and_merge(self, iden):
        vertex = self.vertex_map[iden]
        inp = vertex.get_input()
        out = vertex.get_output()

        # remove this vertex's references in its neighbors and connect neighbors together
        for inp_v in inp:
            inp_v.remove_output(vertex)
            new_wires = get_all_vertices_on_wires(vertex.get_outputs(), set(inp_v.get_gate_all_qubits()))
            inp_v.add_output(new_wires)
            
        for out_v in out:
            out_v.remove_input(vertex)
            new_wires = get_all_vertices_on_wires(vertex.get_inputs(), set(out_v.get_gate_all_qubits()))
            out_v.add_output(new_wires)
            
        vertex.get_gate().delete() # renames the gate name for deletion
        
            
        



        
 
    


