import pytest
import os

from src.optimizer_subroutines import *
from src.circuit_dag import Vertex, CircuitDAG
from src.parser import Parser
from src.gate import Gate

from testfixtures import TempDirectory

@pytest.fixture
def parser():
    return Parser()


def test_hadamard_rule1(parser):
    fn = 'test_circ.txt'
    with TempDirectory() as d:
        d.write(fn, b'INIT 1\nH 0\nP 0\nH 0\n')
        fullpath = os.path.join(d.path, fn)
        nl = parser.get_netlist(fullpath)
        cd = CircuitDAG(1, nl)

        hadamard_gate_reduction(cd)

        vertices = {v for _,v in cd.get_vertex_map().items()}
        assert len(vertices) == 3

        for v in vertices:
            if v.get_gate_name() == 'H':
                assert len(v.get_input()) == 1
                assert list(v.get_input())[0].get_gate_name() == 'P_dag'
                assert list(v.get_output())[0].get_gate_name() == 'P_dag'
            else:
                assert len(v.get_input()) + len(v.get_output()) == 1


def test_hadamard_rule2(parser):
    fn = 'test_circ.txt'
    with TempDirectory() as d:
        d.write(fn, b'INIT 1\nH 0\nP_dag 0\nH 0\n')
        fullpath = os.path.join(d.path, fn)
        nl = parser.get_netlist(fullpath)
        cd = CircuitDAG(1, nl)

        hadamard_gate_reduction(cd)

        vertices = {v for _,v in cd.get_vertex_map().items()}
        assert len(vertices) == 3

        for v in vertices:
            if v.get_gate_name() == 'H':
                assert len(v.get_input()) == 1
                assert list(v.get_input())[0].get_gate_name() == 'P'
                assert list(v.get_output())[0].get_gate_name() == 'P'
            else:
                assert len(v.get_input()) + len(v.get_output()) == 1


def test_hadamard_rule3(parser):
    fn = 'test_circ.txt'
    with TempDirectory() as d:
        d.write(fn, b'INIT 2\nH 0\nH 1\nCNOT 0 1\nH 0\nH 1\n')
        fullpath = os.path.join(d.path, fn)
        nl = parser.get_netlist(fullpath)
        cd = CircuitDAG(2, nl)

        hadamard_gate_reduction(cd)

        vertices = {v for _,v in cd.get_vertex_map().items()}
        assert len(vertices) == 1

        v = list(vertices)[0]
        assert len(v.get_input()) + len(v.get_output()) == 0
        assert v.get_gate_name() == 'CNOT'
        assert v.get_gate_target() == 0
        assert v.get_gate_controls() == [1]

def test_hadamard_rule4(parser):
    fn = 'test_circ.txt'
    with TempDirectory() as d:
        d.write(fn, b'INIT 2\nH 1\nP 1\nCNOT 0 1\nP_dag 1\nH 1\n')
        fullpath = os.path.join(d.path, fn)
        nl = parser.get_netlist(fullpath)
        cd = CircuitDAG(2, nl)

        hadamard_gate_reduction(cd)

        vertices = {v for _,v in cd.get_vertex_map().items()}
        assert len(vertices) == 3

        seen = [False, False, False]
        for v in vertices:
            if v.get_gate_name() == 'P_dag':
                seen[0] = True
                assert len(v.get_input()) == 0
                assert len(v.get_output()) == 1
                assert list(v.get_output())[0].get_gate_name() == 'CNOT'
            if v.get_gate_name() == 'CNOT':
                seen[1] = True
                assert len(v.get_input()) == 1
                assert list(v.get_input())[0].get_gate_name() == 'P_dag'
                assert len(v.get_output()) == 1
                assert list(v.get_output())[0].get_gate_name() == 'P'
                assert v.get_gate_target() == 1
                assert v.get_gate_controls() == [0]
            if v.get_gate_name() == 'P':
                seen[2] = True
                assert len(v.get_output()) == 0
                assert len(v.get_input()) == 1
                assert list(v.get_input())[0].get_gate_name() == 'CNOT'
        
        assert seen == [True, True, True]
