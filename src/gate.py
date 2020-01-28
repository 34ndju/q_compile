GARBARGE = 'IGNORE_THIS_GATE'

class Gate:
    def __init__(self, text):
        arr = text.split()
        self.text = text
        self.gate_name = arr[0]
        self.target = int(arr[-1])
        self.controls = [int(a) for a in arr[1:-1]] if len(arr) > 2 else []
        self.all_qubits = [int(a) for a in arr[1:]]

    def set_gate_name(self, name):
        self.gate_name = name

    def get_name(self):
        return self.gate_name

    def get_target(self):
        return int(self.target)

    def get_controls(self):
        return self.controls.copy()

    def get_all_qubits(self):
        return self.all_qubits
    
    def copy(self):
        return Gate(self.text)

    def delete(self):
        self.gate_name = GARBAGE

