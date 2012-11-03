from sympy import cos, Lambda, Mul, S, simplify, sin, sqrt, symbols, Tuple
from sympy.matrices import (
    BlockDiagMatrix, BlockMatrix, block_collapse, eye, FunctionMatrix,
    Identity, ImmutableMatrix, Inverse, MatAdd, MatMul, MatPow, Matrix,
    MatrixExpr, MatrixSymbol, ShapeError, Trace, Transpose, ZeroMatrix,
)
from sympy.utilities.pytest import raises

n, m, l, k, p = symbols('n m l k p', integer=True)
x = symbols('x')
A = MatrixSymbol('A', n, m)
B = MatrixSymbol('B', m, l)
C = MatrixSymbol('C', n, n)
D = MatrixSymbol('D', n, n)
E = MatrixSymbol('E', m, n)


def test_transpose():
    Sq = MatrixSymbol('Sq', n, n)

    assert Transpose(A).shape == (m, n)
    assert Transpose(A*B).shape == (l, n)
    assert Transpose(Transpose(A)) == A

    assert Transpose(eye(3)) == eye(3)

    assert Transpose(S(5)) == S(5)

    assert Transpose(Matrix([[1, 2], [3, 4]])) == Matrix([[1, 3], [2, 4]])

    assert Transpose(Trace(Sq)) == Trace(Sq)


def test_inverse():
    raises(ShapeError, lambda: Inverse(A))
    assert Inverse(Inverse(C)) == C

    assert Inverse(C)*C == Identity(C.rows)

    assert Inverse(eye(3)) == eye(3)

    assert Inverse(S(3)) == S(1)/3

    assert Inverse(Identity(n)) == Identity(n)

    # Simplifies Muls if possible (i.e. submatrices are square)
    assert Inverse(C*D) == D.I*C.I
    # But still works when not possible
    assert Inverse(A*E).is_Inverse

    # We play nice with traditional explicit matrices
    assert Inverse(Matrix([[1, 2], [3, 4]])) == Matrix([[1, 2], [3, 4]]).inv()


def test_trace():
    A = MatrixSymbol('A', n, n)
    B = MatrixSymbol('B', n, n)
    assert isinstance(Trace(A), Trace)
    assert not isinstance(Trace(A), MatrixExpr)
    raises(ShapeError, lambda: Trace(MatrixSymbol('B', 3, 4)))
    assert Trace(eye(3)) == 3
    assert Trace(Matrix(3, 3, [1, 2, 3, 4, 5, 6, 7, 8, 9])) == 15

    A / Trace(A)  # Make sure this is possible

    # Some easy simplifications
    assert Trace(Identity(5)) == 5
    assert Trace(ZeroMatrix(5, 5)) == 0
    assert Trace(2*A*B) == 2 * Trace(A*B)
    assert Trace(A.T) == Trace(A)

    i, j = symbols('i,j')
    F = FunctionMatrix(3, 3, Lambda((i, j), i + j))
    assert Trace(F).doit() == (0 + 0) + (1 + 1) + (2 + 2)

    raises(TypeError, lambda: Trace(S.One))

    assert Trace(A).arg is A


def test_shape():
    assert A.shape == (n, m)
    assert (A*B).shape == (n, l)
    raises(ShapeError, lambda: B*A)


def test_matexpr():
    assert (x*A).shape == A.shape
    assert (x*A).__class__ == MatMul
    assert 2*A - A - A == ZeroMatrix(*A.shape)
    assert (A*B).shape == (n, l)


def test_subs():
    A = MatrixSymbol('A', n, m)
    B = MatrixSymbol('B', m, l)
    C = MatrixSymbol('C', m, l)

    assert A.subs(n, m).shape == (m, m)

    assert (A*B).subs(B, C) == A*C

    assert (A*B).subs(l, n).is_square


def test_BlockMatrix():
    A = MatrixSymbol('A', n, m)
    B = MatrixSymbol('B', n, k)
    C = MatrixSymbol('C', l, m)
    D = MatrixSymbol('D', l, k)
    M = MatrixSymbol('M', m + k, p)
    N = MatrixSymbol('N', l + n, k + m)
    X = BlockMatrix(Matrix([[A, B], [C, D]]))

    # block_collapse does nothing on normal inputs
    E = MatrixSymbol('E', n, m)
    assert block_collapse(A + 2*E) == A + 2*E
    F = MatrixSymbol('F', m, m)
    assert block_collapse(E.T*A*F) == E.T*A*F

    assert X.shape == (l + n, k + m)
    assert (block_collapse(Transpose(X)) ==
            BlockMatrix(Matrix([[A.T, C.T], [B.T, D.T]])))
    assert Transpose(X).shape == X.shape[::-1]
    assert X.blockshape == (2, 2)

    # Test that BlockMatrices and MatrixSymbols can still mix
    assert (X*M).is_MatMul
    assert X._blockmul(M).is_MatMul
    assert (X*M).shape == (n + l, p)
    assert (X + N).is_MatAdd
    assert X._blockadd(N).is_MatAdd
    assert (X + N).shape == X.shape

    E = MatrixSymbol('E', m, 1)
    F = MatrixSymbol('F', k, 1)

    Y = BlockMatrix(Matrix([[E], [F]]))

    assert (X*Y).shape == (l + n, 1)
    assert block_collapse(X*Y).blocks[0, 0] == A*E + B*F
    assert block_collapse(X*Y).blocks[1, 0] == C*E + D*F
    assert (block_collapse(Transpose(block_collapse(Transpose(X*Y)))) ==
            block_collapse(X*Y))

    # block_collapse passes down into container objects, transposes, and inverse
    assert block_collapse(Tuple(X*Y, 2*X)) == (
        block_collapse(X*Y), block_collapse(2*X))
    assert (block_collapse(Transpose(X*Y)) ==
            block_collapse(Transpose(block_collapse(X*Y))))

    Ab = BlockMatrix([[A]])
    Z = MatrixSymbol('Z', *A.shape)

    # Make sure that MatrixSymbols will enter 1x1 BlockMatrix if it simplifies
    assert block_collapse(Ab + Z) == A + Z


def test_BlockMatrix_Trace():
    A, B, C, D = map(lambda s: MatrixSymbol(s, 3, 3), 'ABCD')
    X = BlockMatrix([[A, B], [C, D]])
    assert Trace(X) == Trace(A) + Trace(D)


def test_squareBlockMatrix():
    A = MatrixSymbol('A', n, n)
    B = MatrixSymbol('B', n, m)
    C = MatrixSymbol('C', m, n)
    D = MatrixSymbol('D', m, m)
    X = BlockMatrix([[A, B], [C, D]])
    Y = BlockMatrix([[A]])

    assert X.is_square

    assert block_collapse(X + Identity(m + n)).equals(
        BlockMatrix([[A + Identity(n), B], [C, D + Identity(m)]]))
    Q = X + Identity(m + n)

    assert block_collapse(Inverse(Q)) == Inverse(block_collapse(Q))

    assert (X + MatrixSymbol('Q', n + m, n + m)).is_MatAdd
    assert (X * MatrixSymbol('Q', n + m, n + m)).is_MatMul

    assert Y.I.blocks[0, 0] == A.I
    assert Inverse(X, expand=True) == BlockMatrix([
        [(-B*D.I*C + A).I, -A.I*B*(D + -C*A.I*B).I],
        [-(D - C*A.I*B).I*C*A.I, (D - C*A.I*B).I]])

    assert Inverse(X, expand=False).is_Inverse
    assert X.inverse().is_Inverse

    assert not X.is_Identity

    Z = BlockMatrix([[Identity(n), B], [C, D]])
    assert not Z.is_Identity


def test_BlockDiagMatrix():
    A = MatrixSymbol('A', n, n)
    B = MatrixSymbol('B', m, m)
    C = MatrixSymbol('C', l, l)
    M = MatrixSymbol('M', n + m + l, n + m + l)

    X = BlockDiagMatrix(A, B, C)
    Y = BlockDiagMatrix(A, 2*B, 3*C)

    assert X.blocks[1, 1] == B
    assert X.shape == (n + m + l, n + m + l)
    assert all(X.blocks[i, j].is_ZeroMatrix if i != j else X.blocks[i, j] in [A, B, C]
            for i in range(3) for j in range(3))

    assert block_collapse(X.I * X).is_Identity

    assert block_collapse(X*X).equals(BlockDiagMatrix(A*A, B*B, C*C))

    assert block_collapse(X + X).equals(BlockDiagMatrix(2*A, 2*B, 2*C))

    assert block_collapse(X*Y).equals(BlockDiagMatrix(A*A, 2*B*B, 3*C*C))

    assert block_collapse(X + Y).equals(BlockDiagMatrix(2*A, 3*B, 4*C))

    # Ensure that BlockDiagMatrices can still interact with normal MatrixExprs
    assert (X*(2*M)).is_MatMul
    assert (X + (2*M)).is_MatAdd

    assert (X._blockmul(M)).is_MatMul
    assert (X._blockadd(M)).is_MatAdd


def test_ZeroMatrix():
    A = MatrixSymbol('A', n, m)
    Z = ZeroMatrix(n, m)

    assert A + Z == A
    assert A*Z.T == ZeroMatrix(n, n)
    assert Z*A.T == ZeroMatrix(n, n)
    assert A - A == ZeroMatrix(*A.shape)

    assert Transpose(Z) == ZeroMatrix(m, n)
    assert Z.conjugate() == Z


def test_Identity():
    A = MatrixSymbol('A', n, m)
    In = Identity(n)
    Im = Identity(m)

    assert A*Im == A
    assert In*A == A

    assert Transpose(In) == In
    assert Inverse(In) == In
    assert In.conjugate() == In


def test_MatAdd():
    A = MatrixSymbol('A', n, m)
    B = MatrixSymbol('B', n, m)

    assert (A + B).shape == A.shape
    assert MatAdd(A, -A, 2*B).is_MatMul

    raises(ShapeError, lambda: A + B.T)
    raises(TypeError, lambda: A + 1)
    raises(TypeError, lambda: 5 + A)
    raises(TypeError, lambda: 5 - A)

    assert MatAdd(A, ZeroMatrix(n, m), -A) == ZeroMatrix(n, m)
    # raises(TypeError, lambda : MatAdd(ZeroMatrix(n,m), S(0)))


def test_MatMul():
    A = MatrixSymbol('A', n, m)
    B = MatrixSymbol('B', m, l)
    C = MatrixSymbol('C', n, n)

    assert (2*A*B).shape == (n, l)

    assert (A*0*B) == ZeroMatrix(n, l)

    raises(ShapeError, lambda: B*A)
    assert (2*A).shape == A.shape

    assert MatMul(A, ZeroMatrix(m, m), B) == ZeroMatrix(n, l)

    assert MatMul(C*Identity(n)*C.I) == Identity(n)

    assert B/2 == S.Half*B
    raises(NotImplementedError, lambda: 2/B)

    A = MatrixSymbol('A', n, n)
    B = MatrixSymbol('B', n, n)
    assert MatMul(Identity(n), (A + B)).is_MatAdd


def test_MatPow():
    A = MatrixSymbol('A', n, n)

    AA = MatPow(A, 2)
    assert AA.exp == 2
    assert AA.base == A
    assert (A**n).exp == n

    assert A**0 == Identity(n)
    assert A**1 == A
    assert A**-1 == Inverse(A)
    raises(ShapeError, lambda: MatrixSymbol('B', 3, 2)**2)


def test_MatrixSymbol():
    n, m, t = symbols('n,m,t')
    X = MatrixSymbol('X', n, m)
    assert X.shape == (n, m)
    raises(TypeError, lambda: MatrixSymbol('X', n, m)(t))  # issue 2756


def test_dense_conversion():
    X = MatrixSymbol('X', 2, 2)
    x00, x01, x10, x11 = symbols('X_00 X_01 X_10 X_11')
    assert ImmutableMatrix(X) == ImmutableMatrix([[x00, x01], [x10, x11]])
    assert Matrix(X) == Matrix([[x00, x01], [x10, x11]])


def test_free_symbols():
    assert (C*D).free_symbols == set((C, D))


def test_zero_matmul():
    assert isinstance(S.Zero * MatrixSymbol('X', 2, 2), MatrixExpr)


def test_matadd_simplify():
    A = MatrixSymbol('A', 1, 1)
    assert simplify(MatAdd(A, ImmutableMatrix([[sin(x)**2 + cos(x)**2]]))) == \
        MatAdd(A, ImmutableMatrix([[1]]))


def test_matmul_simplify():
    A = MatrixSymbol('A', 1, 1)
    assert simplify(MatMul(A, ImmutableMatrix([[sin(x)**2 + cos(x)**2]]))) == \
        MatMul(A, ImmutableMatrix([[1]]))
