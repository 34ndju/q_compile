GARBAGE = 'IGNORE_THIS_GATE'

class Gate:
    def __init__(self, text):
        arr = text.split()
        self.text = text
        self.gate_name = arr[0]

        if self.gate_name == 'R_z':
            assert len(arr) == 3
            self.theta = int(arr[1])
            self.target = int(arr[2])
            self.controls = []
            self.all_qubits = [self.target]
        else:
            self.theta = None
            self.target = int(arr[-1])
            self.controls = [int(a) for a in arr[1:-1]] if len(arr) > 2 else []
            self.all_qubits = [int(a) for a in arr[1:]]

    def get_theta(self):
        return self.theta

    def set_theta(self, theta):
        self.theta = theta

    def set_name(self, name):
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
