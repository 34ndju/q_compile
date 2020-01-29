import pytest
import os
from src.parser import Parser
from testfixtures import TempDirectory


@pytest.fixture
def parser():
    return Parser()


def test_netlist_length(parser):
    fn = 'test_circ.txt'
    with TempDirectory() as d:
        d.write(fn, b'INIT 4\nCNOT 0 2\nH 2\nCCZ 0 3 4\n')
        fullpath = os.path.join(d.path, fn)
        nl = parser.get_netlist(fullpath)
        assert len(nl) == 3


