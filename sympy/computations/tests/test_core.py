from sympy.computations.core import (Computation, unique, CompositeComputation,
        Identity)

a,b,c,d,e,f,g,h = 'abcdefgh'

def test_Computation():
    C = Computation()
    assert hasattr(C, 'inputs')
    assert hasattr(C, 'outputs')
    assert hasattr(C, 'edges')

def test_unique():
    assert tuple(unique((1, 3, 1, 2))) == (1, 3, 2)

class TComp(Computation):
    """ Test Computation class """
    def __init__(self, op, inputs, outputs):
        self.op = op
        self.inputs = tuple(inputs)
        self.outputs = tuple(outputs)

    def __str__(self):
        ins  = "["+', '.join(self.inputs) +"]"
        outs = "["+', '.join(self.outputs)+"]"
        return "%s -> %s -> %s"%(ins, str(self.op), outs)

def test_testcomp():
    A = TComp('add', (a, b, c), (d,))
    assert A.inputs == (a, b, c)
    assert tuple(A.edges()) == ((a, A), (b, A), (c, A), (A, d))

def test_composite():
    A = TComp('add', (a, b, c), (d,))
    M = TComp('mul', (d, e), (f,))
    C = CompositeComputation(A, M)
    assert tuple(C.inputs)  == (a, b, c, e)
    assert tuple(C.outputs) == (f,)
    assert tuple(C.edges()) == ((a, A), (b, A), (c, A), (A, d), (d, M), (e, M),
            (M, f))
    assert set(C.variables) == set((a,b,c,d,e,f))

def test_composite_dag():
    A = TComp('add', (a, b, c), (d,))
    M = TComp('mul', (d, e), (f,))
    C = CompositeComputation(A, M)

    assert C.dag_io() == {A: set([M]), M: set()}
    assert C.dag_oi() == {M: set([A]), A: set()}

def test_toposort():
    A = TComp('add', (a, b, c), (d,))
    M = TComp('mul', (d, e), (f,))
    C = CompositeComputation(A, M)

    assert tuple(C.toposort()) == (A, M)

def test_multi_out():
    MM = TComp('minmax', (a, b), (d, e))
    A =  TComp('foo', (d,), (f,))
    B =  TComp('bar', (a, f), (g, h))
    C =  CompositeComputation(MM, A, B)
    assert set(C.inputs) == set((a, b))
    assert set(C.outputs) == set((e, g, h))
    assert tuple(C.toposort()) == (MM, A, B)

def test_add():
    MM = TComp('minmax', (a, b), (d, e))
    A =  TComp('foo', (d,), (f,))
    B =  TComp('bar', (a, f), (g, h))
    C =  CompositeComputation(MM, A, B)
    C2 = MM+A+B
    assert set(C.inputs) == set(C2.inputs)
    assert set(C.outputs) == set(C2.outputs)

def test_computation_eq():
    assert TComp('foo', (a,), (b,)) == TComp('foo', (a,), (b,))
    assert TComp('foo', (a,), (b,)) != TComp('foo', (a,), (c,))

def test_computation_eq():
    A =  TComp('foo', (d,), (f,))
    B =  TComp('bar', (a, f), (g, h))
    assert A+B == A+B

def test_canonicalize():
    A = TComp('foo', (d,), (f,))
    B = TComp('bar', (a,), (b,))

    assert A + B == B + A

    I = Identity(f)
    assert I + A is A
    assert CompositeComputation(A) is A
    I2 = Identity(f, e)
    I3 = Identity(e)

    assert I2 + A == I3 + A

def test_dot():
    from sympy.computations.core import OpComp
    MM = OpComp('minmax', (a, b), (d, e))
    A =  OpComp('foo', (d,), (f,))
    B =  OpComp('bar', (a, f), (g, h))
    C =  CompositeComputation(MM, A, B)

    assert isinstance(MM.dot(), str)
    assert isinstance(C.dot(), str)
