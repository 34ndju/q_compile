from src.gate import Gate
from src.circuit_dag import CircuitDAG, Vertex

class Parser:
    def __init__(self):
        pass

    def get_netlist(self, filename):
        netlist = []

        f = open(filename, 'r')
        for line in f:
            line = line.replace('\n', '')
            if len(line) > 0:
                gate = Gate(line)
                if gate.get_name() != 'INIT':
                    netlist.append(gate)
        return netlist
            

