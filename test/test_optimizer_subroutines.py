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


FLOAT_DELTA = 0.0000000001

def test_R_z_commute_rule1(parser):
    fn = 'test_circ.txt'
    with TempDirectory() as d:
        d.write(fn, b'INIT 2\nR_z 123 1\nH 1\nCNOT 0 1\nH 1\n')
        fullpath = os.path.join(d.path, fn)
        nl = parser.get_netlist(fullpath)
        cd = CircuitDAG(2, nl)

        v1,v2,v3,v4 = None, None, None, None
        vertices = {v for _,v in cd.get_vertex_map().items()}
        for v in vertices:
            if v.get_gate_name() == 'R_z':
                v1 = v
            if v.get_gate_name() == 'H' and list(v.get_input())[0].get_gate_name() == 'R_z':
                v2 = v
            if v.get_gate_name() == 'CNOT':
                v3 = v
            if v.get_gate_name() == 'H' and list(v.get_input())[0].get_gate_name() != 'R_z':
                v4 = v
        assert v1 is not None and v2 is not None and v3 is not None and v4 is not None
        
        assert single_R_z_commute(v1) 

        assert v2.get_input() == set()
        assert v2.get_output() == {v3}
        assert v3.get_input() == {v2}
        assert v3.get_output() == {v4}
        assert v4.get_input() == {v3}
        assert v4.get_output() == {v1}
        assert v1.get_input() == {v4}
        assert v1.get_output() == set()


def test_R_z_commute_rule2(parser):
    fn = 'test_circ.txt'
    with TempDirectory() as d:
        d.write(fn, b'INIT 2\nR_z 123 1\nCNOT 0 1\nR_z 456 1\nCNOT 0 1\n')
        fullpath = os.path.join(d.path, fn)
        nl = parser.get_netlist(fullpath)
        cd = CircuitDAG(2, nl)

        v1,v2,v3,v4 = None, None, None, None
        vertices = {v for _,v in cd.get_vertex_map().items()}
        for v in vertices:
            if v.get_gate_name() == 'R_z' and v.get_input() == set():
                v1 = v
            if v.get_gate_name() == 'CNOT' and v.get_output() != set():
                v2 = v
            if v.get_gate_name() == 'R_z' and v.get_input() != set():
                v3 = v
            if v.get_gate_name() == 'CNOT' and v.get_output() == set():
                v4 = v
        assert v1 is not None and v2 is not None and v3 is not None and v4 is not None

        assert single_R_z_commute(v1)

        assert v2.get_input() == set()
        assert v2.get_output() == {v3, v4}
        assert v3.get_input() == {v2}
        assert v3.get_output() == {v4}
        assert v4.get_input() == {v2, v3}
        assert v4.get_output() == {v1}
        assert v1.get_input() == {v4}
        assert v1.get_output() == set()


def test_R_z_commute_rule3(parser):
    fn = 'test_circ.txt'
    with TempDirectory() as d:
        d.write(fn, b'INIT 2\nR_z 123 0\nCNOT 0 1\n')
        fullpath = os.path.join(d.path, fn)
        nl = parser.get_netlist(fullpath)
        cd = CircuitDAG(2, nl)

        v1,v2 = None, None
        vertices = {v for _,v in cd.get_vertex_map().items()}
        for v in vertices:
            if v.get_gate_name() == 'R_z':
                v1 = v
            if v.get_gate_name() == 'CNOT':
                v2 = v
        assert v1 is not None and v2 is not None 

        assert single_R_z_commute(v1)

        assert v2.get_input() == set()
        assert v2.get_output() == {v1}
        assert v1.get_input() == {v2}
        assert v1.get_output() == set()

def test_swap_only_vertices_one_qubit(parser):
    fn = 'test_circ.txt'
    with TempDirectory() as d:
        d.write(fn, b'INIT 1\nH 0\nP 0\n')
        fullpath = os.path.join(d.path, fn)
        nl = parser.get_netlist(fullpath)
        cd = CircuitDAG(1, nl)

        v1,v2 = None, None
        vertices = {v for _,v in cd.get_vertex_map().items()}
        for v in vertices:
            if v.get_gate_name() == 'H':
                v1 = v
            if v.get_gate_name() == 'P':
                v2 = v

        assert v1 != None and v2 != None 

        swap_2_vertex_neighbors(v1, v2)
        
        assert v2.get_input() == set()
        assert v2.get_output() == {v1}

        assert v1.get_input() == {v2}
        assert v1.get_output() == set()

def test_swap_two_vertices_one_qubit(parser):
    fn = 'test_circ.txt'
    with TempDirectory() as d:
        d.write(fn, b'INIT 1\nH 0\nP_dag 0\nP 0\nH_dag 0\n')
        fullpath = os.path.join(d.path, fn)
        nl = parser.get_netlist(fullpath)
        cd = CircuitDAG(1, nl)

        v1,v2,v3,v4 = None, None, None, None
        vertices = {v for _,v in cd.get_vertex_map().items()}
        for v in vertices:
            if v.get_gate_name() == 'H':
                v1 = v
            if v.get_gate_name() == 'P_dag':
                v2 = v
            if v.get_gate_name() == 'P':
                v3 = v
            if v.get_gate_name() == 'H_dag':
                v4 = v

        assert v1 != None and v2 != None and v3 != None and v4 != None

        swap_2_vertex_neighbors(v2, v3)

        assert len(v1.get_input()) == 0
        assert len(v1.get_output()) == 1
        assert list(v1.get_output())[0] == v3

        assert len(v2.get_input()) == 1
        assert list(v2.get_input())[0] == v3
        assert len(v2.get_output()) == 1
        assert list(v2.get_output())[0] == v4

        assert len(v3.get_input()) == 1
        assert list(v3.get_input())[0] == v1
        assert len(v3.get_output()) == 1
        assert list(v3.get_output())[0] == v2

        assert len(v4.get_input()) == 1
        assert list(v4.get_input())[0] == v2
        assert len(v4.get_output()) == 0
    
def test_swap_two_vertices_left_barrier(parser):
    fn = 'test_circ.txt'
    with TempDirectory() as d:
        d.write(fn, b'INIT 3\nCX 0 2\nCY 1 2\nCZ 0 2\n')
        fullpath = os.path.join(d.path, fn)
        nl = parser.get_netlist(fullpath)
        cd = CircuitDAG(3, nl)

        v1,v2,v3 = None, None, None
        vertices = {v for _,v in cd.get_vertex_map().items()}
        for v in vertices:
            if v.get_gate_name() == 'CX':
                v1 = v
            if v.get_gate_name() == 'CY':
                v2 = v
            if v.get_gate_name() == 'CZ':
                v3 = v

        assert v1 != None and v2 != None and v3 != None

        assert len(v1.get_output()) == 2

        swap_2_vertex_neighbors(v2, v3)

        assert len(v1.get_output()) == 1
        assert list(v1.get_output())[0] == v3

        assert len(v3.get_input()) == 1
        assert list(v3.get_input())[0] == v1
        assert len(v3.get_output()) == 1
        assert list(v3.get_output())[0] == v2

        assert len(v2.get_input()) == 1
        assert list(v2.get_input())[0] == v3
        

def test_swap_two_vertices_left_leak_right_barrier(parser):
    fn = 'test_circ.txt'
    with TempDirectory() as d:
        d.write(fn, b'INIT 3\nCCX 0 1 2\nCCY 0 1 2\nCNOT 0 2\nCCZ 0 1 2')
        fullpath = os.path.join(d.path, fn)
        nl = parser.get_netlist(fullpath)
        cd = CircuitDAG(3, nl)

        v1,v2,v3,v4 = None, None, None, None
        vertices = {v for _,v in cd.get_vertex_map().items()}
        for v in vertices:
            if v.get_gate_name() == 'CCX':
                v1 = v
            if v.get_gate_name() == 'CCY':
                v2 = v
            if v.get_gate_name() == 'CNOT':
                v3 = v
            if v.get_gate_name() == 'CCZ':
                v4 = v

        assert v1 != None and v2 != None and v3 != None and v4 != None

        swap_2_vertex_neighbors(v2, v3)

        assert len(v1.get_output()) == 2
        assert v1.get_output() == {v2, v3}

        assert len(v3.get_input()) == 1
        assert list(v3.get_input())[0] == v1
        assert len(v3.get_output()) == 1
        assert list(v3.get_output())[0] == v2

        assert len(v2.get_input()) == 2
        assert v2.get_input() == {v1, v3}
        assert v2.get_output() == {v4}

        assert v4.get_input() == {v2}
        assert len(v4.get_output()) == 0


def test_hadamard_rule1(parser):
    fn = 'test_circ.txt'
    with TempDirectory() as d:
        d.write(fn, b'INIT 1\nH 0\nP 0\nH 0\n')
        fullpath = os.path.join(d.path, fn)
        nl = parser.get_netlist(fullpath)
        cd = CircuitDAG(1, nl)

        cd = hadamard_gate_reduction(cd)

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

        cd = hadamard_gate_reduction(cd)

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

        cd = hadamard_gate_reduction(cd)

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

        cd = hadamard_gate_reduction(cd)

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

def test_hadamard_rule5(parser):
    fn = 'test_circ.txt'
    with TempDirectory() as d:
        d.write(fn, b'INIT 2\nH 1\nP_dag 1\nCNOT 0 1\nP 1\nH 1\n')
        fullpath = os.path.join(d.path, fn)
        nl = parser.get_netlist(fullpath)
        cd = CircuitDAG(2, nl)

        cd = hadamard_gate_reduction(cd)

        vertices = {v for _,v in cd.get_vertex_map().items()}
        assert len(vertices) == 3

        seen = [False, False, False]
        for v in vertices:
            if v.get_gate_name() == 'P':
                seen[0] = True
                assert len(v.get_input()) == 0
                assert len(v.get_output()) == 1
                assert list(v.get_output())[0].get_gate_name() == 'CNOT'
            if v.get_gate_name() == 'CNOT':
                seen[1] = True
                assert len(v.get_input()) == 1
                assert list(v.get_input())[0].get_gate_name() == 'P'
                assert len(v.get_output()) == 1
                assert list(v.get_output())[0].get_gate_name() == 'P_dag'
                assert v.get_gate_target() == 1
                assert v.get_gate_controls() == [0]
            if v.get_gate_name() == 'P_dag':
                seen[2] = True
                assert len(v.get_output()) == 0
                assert len(v.get_input()) == 1
                assert list(v.get_input())[0].get_gate_name() == 'CNOT'

        assert seen == [True, True, True]

def test_cd_to_netlist(parser):
    fn = 'test_circ.txt'
    with TempDirectory() as d:
        d.write(fn, b'INIT 2\nCNOT 0 1\nX 1\nCZ 1 0\n')
        fullpath = os.path.join(d.path, fn)
        nl = parser.get_netlist(fullpath)
        cd = CircuitDAG(2, nl)

        new_nl = circuit_dag_to_netlist(cd)

        assert new_nl == nl        

def test_commute_R_z_combination(parser):
    fn = 'test_circ.txt'
    with TempDirectory() as d:
        d.write(fn, b'INIT 2\nR_z 3 0\nCNOT 0 1\nCNOT 0 1\nCNOT 0 1\nR_z 2 0\n')
        fullpath = os.path.join(d.path, fn)
        nl = parser.get_netlist(fullpath)
        cd = CircuitDAG(2, nl)

        v_target = None
        for _,v in cd.get_vertex_map().items():
            if v.get_gate_name() == 'R_z' and abs(v.get_gate().get_theta() - 3.0) < FLOAT_DELTA:
                v_target = v

        assert not v_target is None

        cd = find_R_z_combination(cd, v_target)
        nl = circuit_dag_to_netlist(cd)

        assert nl[0].get_name() == 'CNOT'
        assert nl[1].get_name() == 'CNOT'
        assert nl[2].get_name() == 'CNOT'
        assert nl[3].get_name() == 'R_z'
        assert abs(nl[3].get_theta() - 5.0) < FLOAT_DELTA


def test_no_R_z_combination(parser):
    fn = 'test_circ.txt'
    with TempDirectory() as d:
        d.write(fn, b'INIT 2\nR_z 3 0\nCNOT 0 1\nCZ 0 1\nCNOT 0 1\nR_z 2 0\n')
        fullpath = os.path.join(d.path, fn)
        nl = parser.get_netlist(fullpath)
        cd = CircuitDAG(2, nl)

        v_target = None
        for _,v in cd.get_vertex_map().items():
            if v.get_gate_name() == 'R_z' and abs(v.get_gate().get_theta() - 3.0) < FLOAT_DELTA:
                v_target = v

        assert not v_target is None

        cd = find_R_z_combination(cd, v_target)
        new_nl = circuit_dag_to_netlist(cd)

        assert new_nl == nl


def test_commute_cnot_combination(parser):
    fn = 'test_circ.txt'
    with TempDirectory() as d:
        d.write(fn, b'INIT 3\n\nCNOT 0 2\nCNOT 1 2\nCNOT 0 2\n')
        fullpath = os.path.join(d.path, fn)
        nl = parser.get_netlist(fullpath)
        cd = CircuitDAG(3, nl)

        v_target = None
        for _,v in cd.get_vertex_map().items():
            if len(v.get_input()) == 0:
                v_target = v

        assert not v_target is None

        cd = find_cnot_combination(cd, v_target)
        nl = circuit_dag_to_netlist(cd)

        assert len(nl) == 1
        assert nl[0].get_controls() == [1]

def test_hard_swaps_combination(parser):
    fn = 'test_circ.txt'
    with TempDirectory() as d:
        d.write(fn, b'INIT 3\n\nC1 0 1\nH1 1\nC2 1 2\nH2 1\nC3 0 2\nC4 0 1\n')
        fullpath = os.path.join(d.path, fn)
        nl = parser.get_netlist(fullpath)
        cd = CircuitDAG(3, nl)

        v_target = None

        for _,v in cd.get_vertex_map().items():
            if v.get_gate_name() == 'C1':
                v1 = v
            if v.get_gate_name() == 'H1':
                v2 = v
            if v.get_gate_name() == 'C2':
                v3 = v
            if v.get_gate_name() == 'H2':
                v4 = v
            if v.get_gate_name() == 'C3':
                v5 = v
            if v.get_gate_name() == 'C4':
                v6 = v

        assert len(v1.get_output()) == 2
        swap_2_vertex_neighbors(v1, v2)
        assert len(v1.get_output()) == 2
        swap_2_vertex_neighbors(v1, v3)
        assert len(v1.get_output()) == 2
        swap_2_vertex_neighbors(v1, v4)
        assert len(v1.get_output()) == 2
        swap_2_vertex_neighbors(v1, v5)
        assert len(v1.get_output()) == 1
        swap_2_vertex_neighbors(v1, v6)
        assert len(v1.get_output()) == 0




def test_hard_commute_cnot_combination(parser):
    fn = 'test_circ.txt'
    with TempDirectory() as d:
        d.write(fn, b'INIT 3\n\nCNOT 0 1\nH 1\nCNOT 1 2\nH 1\nCNOT 2 1\nCNOT 0 1\n')
        fullpath = os.path.join(d.path, fn)
        nl = parser.get_netlist(fullpath)
        cd = CircuitDAG(3, nl)

        v_target = None

        for _,v in cd.get_vertex_map().items():
            if v.get_gate_name() == 'CNOT' and len(v.get_input()) == 0:
                v_target = v
                
        assert v_target is not None

        cd = find_cnot_combination(cd, v_target)
        new_nl = circuit_dag_to_netlist(cd)

        assert len(new_nl) == 4
        assert new_nl == nl[1:-1]
