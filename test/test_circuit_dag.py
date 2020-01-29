import pytest
import os
from src.circuit_dag import Vertex, CircuitDAG
from src.parser import Parser
from src.gate import Gate


def test_vertex_init():
    iden = 12
    gate = Gate('CNOT 2 3')
    v = Vertex(iden, gate)

    assert v.get_id() == iden
    assert v.get_gate() == gate
    assert v.get_gate_name() == 'CNOT'

    new_target = 4
    v.set_target(4)
    assert v.get_gate().get_target() == new_target


from testfixtures import TempDirectory


@pytest.fixture
def parser():
    return Parser()


def test_dag_structure(parser):
    fn = 'test_circ.txt'
    with TempDirectory() as d:
        d.write(fn, b'INIT 5\nCNOT 0 2\nH 2\nCCZ 0 3 4\n')
        fullpath = os.path.join(d.path, fn)
        nl = parser.get_netlist(fullpath)

        cd = CircuitDAG(5, nl)
        vertices = {v for _,v in cd.get_vertex_map().items()}
        assert len(vertices) == 3
        
        for v in vertices:
            if v.get_gate_name() == 'CNOT':
                assert len(v.get_output()) == 2
                assert (list(v.get_output())[0].get_gate_name() == 'H' and list(v.get_output())[1].get_gate_name() == 'CCZ') or (list(v.get_output())[1].get_gate_name() == 'H' and list(v.get_output())[0].get_gate_name() == 'CCZ')
                assert len(v.get_input()) == 0

            if v.get_gate_name() == 'H':
                assert len(v.get_output()) == 0
                assert len(v.get_input()) == 1
                assert list(v.get_input())[0].get_gate_name() == 'CNOT'

            if v.get_gate_name() == 'CCZ':
                assert len(v.get_output()) == 0
                assert len(v.get_input()) == 1
                assert list(v.get_input())[0].get_gate_name() == 'CNOT'

def test_delete_vertex(parser):
    fn = 'test_circ.txt'
    with TempDirectory() as d:
        d.write(fn, b'INIT 5\nCNOT 0 2\nH 2\nCCZ 0 2 4\n')
        fullpath = os.path.join(d.path, fn)
        nl = parser.get_netlist(fullpath)
        cd = CircuitDAG(5, nl)

        vertices = {v for _,v in cd.get_vertex_map().items()}
        assert len(vertices) == 3
        for v in vertices:
            if v.get_gate_name() == 'H':
                assert len(v.get_input()) == 1
                assert len(v.get_output()) == 1
                cd.remove_vertex_and_merge(v.get_id())
                break

        vertices = {v for _,v in cd.get_vertex_map().items()}
        assert len(vertices) == 2
        for v in vertices:
            if v.get_gate_name() == 'CNOT':
                assert len(v.get_input()) == 0
                assert len(v.get_output()) == 1
                assert list(v.get_output())[0].get_gate_name() == 'CCZ'
            if v.get_gate_name() == 'CCZ':
                assert len(v.get_output()) == 0
                assert len(v.get_input()) == 1
                assert list(v.get_input())[0].get_gate_name() == 'CNOT'


