from pytest import fixture

@fixture
def equation() -> str:
    return r"""
$$
E = mc^2
$$
""" 

def test_scanning(equation):
    assert equation == r"""
$$
E = mc^2
$$
""" 
