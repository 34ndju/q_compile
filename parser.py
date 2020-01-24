from gate import Gate
from circuit_dag import CircuitDAG, Vertex

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
            

if __name__ == '__main__':
    parser = Parser()
    netlist = parser.get_netlist('circuit_format.txt')
    
    circuit_dag = CircuitDAG(5, netlist)
    import pdb; pdb.set_trace()
