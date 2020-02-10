from src.gate import Gate

class Vertex:
    def __init__(self, iden, gate):
        self.gate = gate
        self.iden = iden
        self.input = set() # type: Set[Vertex]
        self.output = set() #  type: Set[Vertex]

    def get_id(self):
        return self.iden
   
    def get_gate(self):
        return self.gate

    # type: (None) -> Int
    def get_gate_target(self):
        return self.gate.get_target()

    def get_gate_controls(self):
        return self.gate.get_controls()

    def get_gate_name(self):
        return self.gate.get_name()

    def set_gate_name(self, new_name):
        self.gate.set_name(new_name)

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
        else: 
            self.input.update(inp)

    def add_output(self, out):
        # search for repeats
        if type(out) == Vertex:
            self.output.add(out)
        else:
            self.output.update(out)

    def remove_input(self, inp):
        self.input.remove(inp)

    def remove_output(self, out):
        self.output.remove(out)


    def set_target(self, target):
        self.gate.target = target

    def set_controls(self, controls):
        self.gate.controls = controls

    def is_dagger_to(v):
        if v.get_gate_name().find('_dag') > -1 and self.get_gate_name().find('_dag') == -1:
            dag_gate = v
            undag_gate = self
        elif self.get_gate_name().find('_dag') > -1 and c.get_gate_name().find('_dag') == -1:
            dag_gate = self
            undag_gate = v
        else:
            return False

        dag_gate_name = "".join(dag_gate.get_gate_name().split('_dag'))
        undag_gate_name = undag.get_gate_name()

        return dag_gate_name == undag_gate_name 

    def is_gate_delted(self):
        return self.gate.is_deleted()


# type: (Iterable[Vertex], Set[Int]) -> List[Vertex]
def get_all_vertices_on_wires(vertices, wires):
    ret = []
    for vertex in vertices:
        if len(set(vertex.get_gate_all_qubits()).intersection(wires)) > 0:
            ret.append(vertex)
    return ret


class CircuitDAG:
    def __init__(self, num_qubits, netlist):
        self.vertex_map = {}
        self.num_qubits = num_qubits

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


    def get_num_qubits(self):
        return self.num_qubits

    def collect_gate_ids(self, gate_name):
        ids = set()
        for iden, vertex in self.vertex_map.items():
            if vertex.get_gate().get_name() == gate_name:
                ids.add(vertex.get_id())
        return ids


    # type: (Vertex) -> None
    def remove_vertex_and_merge(self, vertex):
        iden = vertex.get_id()
        inp = vertex.get_input()
        out = vertex.get_output()

        # remove this vertex's references in its neighbors and connect neighbors together
        for inp_v in inp:
            inp_v.remove_output(vertex)
            new_wires = get_all_vertices_on_wires(vertex.get_output(), set(inp_v.get_gate_all_qubits()))
            inp_v.add_output(new_wires)
            
        for out_v in out:
            out_v.remove_input(vertex)
            new_wires = get_all_vertices_on_wires(vertex.get_input(), set(out_v.get_gate_all_qubits()))
            out_v.add_input(new_wires)
           

        del self.vertex_map[vertex.get_id()]
        vertex.get_gate().delete() # renames the gate name for deletion

    '''
    # TODO
    # type (None) -> CircuitDAG
    def copy():
    ''' 
        
            
        



        
 
    


