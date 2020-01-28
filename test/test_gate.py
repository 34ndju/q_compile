import pytest
from src.gate import Gate

def test_single_qubit():
    gate = Gate('H 1')
    assert gate.get_name() == 'H'
    assert gate.get_target() == 1
    assert gate.get_controls() == []
    assert gate.get_all_qubits() == [1]


def test_two_qubit():
    gate = Gate('CNOT 1 3')
    assert gate.get_name() == 'CNOT'
    assert gate.get_target() == 3
    assert gate.get_controls() == [1]
    assert gate.get_all_qubits() == [1,3]


