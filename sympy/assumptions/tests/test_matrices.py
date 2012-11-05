from sympy import MatrixSymbol, Q, ask, Identity, ZeroMatrix, Trace
from sympy.utilities.pytest import XFAIL

X = MatrixSymbol('X', 2, 2)
Y = MatrixSymbol('Y', 2, 3)
Z = MatrixSymbol('Z', 2, 2)


def test_invertible():
    assert ask(Q.invertible(X), Q.invertible(X))
    assert ask(Q.invertible(Y)) is False
    assert ask(Q.invertible(X*Y), Q.invertible(X)) is False
    assert ask(Q.invertible(X*Z), Q.invertible(X)) is None
    assert ask(Q.invertible(X*Z), Q.invertible(X) & Q.invertible(Z)) is True
    assert ask(Q.invertible(X.T)) is None
    assert ask(Q.invertible(X.T), Q.invertible(X)) is True
    assert ask(Q.invertible(X.I)) is True
    assert ask(Q.invertible(Identity(3))) is True
    assert ask(Q.invertible(ZeroMatrix(3, 3))) is False


def test_symmetric():
    assert ask(Q.symmetric(X), Q.symmetric(X))
    assert ask(Q.symmetric(X*Z), Q.symmetric(X)) is None
    assert ask(Q.symmetric(X*Z), Q.symmetric(X) & Q.symmetric(Z)) is True
    assert ask(Q.symmetric(X+Z), Q.symmetric(X) & Q.symmetric(Z)) is True
    assert ask(Q.symmetric(Y)) is False
    assert ask(Q.symmetric(Y*Y.T)) is True
    assert ask(Q.symmetric(Y.T*X*Y)) is None
    assert ask(Q.symmetric(Y.T*X*Y), Q.symmetric(X)) is True
    assert ask(Q.symmetric(X*X*X*X*X*X*X*X*X*X), Q.symmetric(X)) is True


def test_orthogonal():
    assert ask(Q.orthogonal(X), Q.orthogonal(X))
    assert ask(Q.orthogonal(X.T), Q.orthogonal(X)) is True
    assert ask(Q.orthogonal(X.I), Q.orthogonal(X)) is True
    assert ask(Q.orthogonal(Y)) is False
    assert ask(Q.orthogonal(X)) is None
    assert ask(Q.orthogonal(X*Z*X), Q.orthogonal(X) & Q.orthogonal(Z)) is True
    assert ask(Q.orthogonal(Identity(3))) is True
    assert ask(Q.orthogonal(ZeroMatrix(3, 3))) is False
    assert ask(Q.invertible(X), Q.orthogonal(X))
    assert not ask(Q.orthogonal(X+Z), Q.orthogonal(X) & Q.orthogonal(Z))


def test_positive_definite():
    assert ask(Q.positive_definite(X), Q.positive_definite(X))
    assert ask(Q.positive_definite(X.T), Q.positive_definite(X)) is True
    assert ask(Q.positive_definite(X.I), Q.positive_definite(X)) is True
    assert ask(Q.positive_definite(Y)) is False
    assert ask(Q.positive_definite(X)) is None
    assert ask(Q.positive_definite(X*Z*X),
            Q.positive_definite(X) & Q.positive_definite(Z)) is True
    assert ask(Q.positive_definite(X), Q.orthogonal(X))
    assert ask(Q.positive_definite(Y.T*X*Y),
            Q.positive_definite(X) & Q.orthogonal(Y)) is True
    assert ask(Q.positive_definite(Identity(3))) is True
    assert ask(Q.positive_definite(ZeroMatrix(3, 3))) is False
    assert ask(Q.positive_definite(X+Z), Q.positive_definite(X) &
            Q.positive_definite(Z)) is True
    assert not ask(Q.positive_definite(-X), Q.positive_definite(X))


def test_triangular():
    assert ask(Q.upper_triangular(X+Z.T+Identity(2)), Q.upper_triangular(X) &
            Q.lower_triangular(Z)) is True
    assert ask(Q.upper_triangular(X*Z.T), Q.upper_triangular(X) &
            Q.lower_triangular(Z)) is True
    assert ask(Q.lower_triangular(Identity(3))) is True
    assert ask(Q.lower_triangular(ZeroMatrix(3, 3))) is True


def test_diagonal():
    assert ask(Q.diagonal(X+Z.T+Identity(2)), Q.diagonal(X) &
               Q.diagonal(Z)) is True
    assert ask(Q.diagonal(ZeroMatrix(3, 3)))
    assert ask(Q.lower_triangular(X) & Q.upper_triangular(X), Q.diagonal(X))

def test_non_atoms():
    assert ask(Q.real(Trace(X)), Q.positive(Trace(X)))

@XFAIL
def test_non_trivial_implies():
    X = MatrixSymbol('X', 3, 3)
    Y = MatrixSymbol('Y', 3, 3)
    assert ask(Q.lower_triangular(X+Y), Q.lower_triangular(X) &
               Q.lower_triangular(Y))
    assert ask(Q.triangular(X), Q.lower_triangular(X))
    assert ask(Q.triangular(X+Y), Q.lower_triangular(X) &
               Q.lower_triangular(Y))


