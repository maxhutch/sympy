"""A module that handles matrices.

Includes functions for fast creating matrices like zero, one/eye, random
matrix, etc.
"""
from matrices import (DeferredVector, ShapeError, NonSquareMatrixError)

from dense import (
    GramSchmidt, Matrix, casoratian, diag, eye, hessian, jordan_cell,
    list2numpy, matrix2numpy, matrix_multiply_elementwise, ones,
    randMatrix, rot_axis1, rot_axis2, rot_axis3, symarray, wronskian,
    zeros)

MutableDenseMatrix = MutableMatrix = Matrix

from sparse import MutableSparseMatrix as SparseMatrix, Diag

from immutable import ImmutableMatrix, ImmutableSparseMatrix

MutableSparseMatrix = SparseMatrix
ImmutableDenseMatrix = ImmutableMatrix

from expressions import (
    BlockDiagMatrix, BlockMatrix, FunctionMatrix, Identity, Inverse,
    MatAdd, MatMul, MatPow, MatrixExpr, MatrixSymbol, Trace, Transpose,
    ZeroMatrix, block_collapse, linear_factors, matrix_symbols, matrixify)
