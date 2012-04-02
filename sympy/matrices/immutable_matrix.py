from matrices import MatrixBase, MutableMatrix
from expressions import MatrixExpr, Transpose
from sympy import Basic, Tuple, sympify

class ImmutableMatrix(MatrixExpr, MatrixBase):

    _class_priority = 8
    is_MatrixBase = True

    @classmethod
    def _new(cls, *args, **kwargs):
        if len(args)==1 and isinstance(args[0], ImmutableMatrix):
            return args[0]
        rows, cols, mat = MatrixBase._handle_creation_inputs(*args, **kwargs)
        rows, cols = sympify(rows), sympify(cols)
        mat = Tuple(*mat)
        return Basic.__new__(cls, rows, cols, mat)
    def __new__(cls, *args, **kwargs):
        return cls._new(*args, **kwargs)

    @property
    def shape(self):
        return self.args[0:2]

    @property
    def mat(self):
        return self.args[2]

    def _entry(self, i, j):
        return MatrixBase.__getitem__(self, (i,j))

    def __setitem__(self, *args):
        raise TypeError("Can not set values in Immutable Matrix")

    __getitem__ = MatrixBase.__getitem__

    as_mutable = MatrixBase.as_mutable

    equals = MatrixBase.equals
    is_Identity = MatrixBase.is_Identity
