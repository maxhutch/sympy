from matexpr import MatrixExpr, ShapeError, Identity
from sympy import Pow, S, Basic
from sympy.core.sympify import _sympify


class MatPow(MatrixExpr):

    def __new__(cls, b, e):
        assert b.is_Matrix
        e = _sympify(e)
        if e is S.One or b.is_ZeroMatrix:
            return b
        elif not b.is_square:
            raise ShapeError("Power of non-square matrix %s" % b)
        elif e is S.Zero:
            return Identity(b.rows)
        else:
            return MatrixExpr.__new__(cls, b, e)

    @property
    def base(self):
        return self.args[0]

    @property
    def exp(self):
        return self.args[1]

    @property
    def shape(self):
        return self.base.shape

    def _entry(self, i, j):
        if self.exp.is_Integer:
            # Make an explicity MatMul out of the MatPow
            return Basic.__new__(MatMul,
                    *[self.base for k in range(self.exp)])._entry(i, j)
        else:
            raise NotImplementedError("Indexing not supported on MatPows")

from matmul import MatMul
