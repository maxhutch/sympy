from matexpr import MatrixExpr, ZeroMatrix, Identity
from matmul import MatMul
from matadd import MatAdd
from matpow import MatPow
from transpose import Transpose
from inverse import Inverse
from matrices import Matrix, eye
from sympy import Tuple, Basic, sympify, FiniteSet
from sympy.utilities.iterables import iterable

class BlockMatrix(MatrixExpr):
    is_BlockMatrix = True
    def __new__(cls, mat):
        if not isinstance(mat, Matrix):
            mat = Matrix(mat)
        data = Tuple(*mat.mat)
        shape = Tuple(*sympify(mat.shape))
        obj = Basic.__new__(cls, data, shape)
        obj.mat = mat
        return obj

    @property
    def shape(self):
        numrows = numcols = 0
        M = self.mat
        for i in range(M.shape[0]):
            numrows += M[i,0].shape[0]
        for i in range(M.shape[1]):
            numcols += M[0,i].shape[1]
        return (numrows, numcols)

    @property
    def blockshape(self):
        return self.mat.shape

    @property
    def rowblocksizes(self):
        return [self.mat[i,0].n for i in range(self.blockshape[0])]

    @property
    def colblocksizes(self):
        return [self.mat[0,i].m for i in range(self.blockshape[1])]

    def _blockmul(self, other):

        if  (other.is_Matrix and other.is_BlockMatrix and
                self.blockshape[1] == other.blockshape[0] and
                self.colblocksizes == other.rowblocksizes):
            return BlockMatrix(self.mat*other.mat)

        return MatrixExpr.__mul__(self, other)

    def _blockadd(self, other):

        if  (other.is_Matrix and other.is_BlockMatrix and
                self.blockshape == other.blockshape and
                self.rowblocksizes == other.rowblocksizes and
                self.colblocksizes == other.colblocksizes):
            return BlockMatrix(self.mat + other.mat)

        return MatrixExpr.__add__(self, other)

    def eval_transpose(self):
        # Flip all the individual matrices
        matrices = [Transpose(matrix) for matrix in self.mat.mat]
        # Make a copy
        mat = Matrix(self.blockshape[0], self.blockshape[1], matrices)
        # Transpose the block structure
        mat = mat.transpose()
        return BlockMatrix(mat)

    def transpose(self):
        return self.eval_transpose()

    def eval_inverse(self):
        # Inverse of size one block matrix is easy
        if len(self.mat.mat)==1:
            mat = Matrix(1, 1, (Inverse(self.mat[0]), ))
            return BlockMatrix(mat)
        else:
            raise NotImplementedError()

    def inverse(self):
        return Inverse(self)

    def __getitem__(self, *args):
        return self.mat.__getitem__(*args)

    @property
    def is_Identity(self):
        if self.blockshape[0] != self.blockshape[1]:
            return False
        for i in range(self.blockshape[0]):
            for j in range(self.blockshape[1]):
                if i==j and not self.mat[i,j].is_Identity:
                    return False
                if i!=j and not self.mat[i,j].is_ZeroMatrix:
                    return False
        return True
    @property
    def is_structurally_symmetric(self):
        return self.rowblocksizes == self.colblocksizes

def BlockDiagMatrix(mats):
    data_matrix = eye(len(mats))
    for i, mat in enumerate(mats):
        data_matrix[i,i] = mat

    for r in range(len(mats)):
        for c in range(len(mats)):
            if r == c:
                continue
            n = mats[r].n
            m = mats[c].m
            data_matrix[r, c] = ZeroMatrix(n, m)

    return BlockMatrix(data_matrix)

def block_collapse(expr):

    if expr.__class__ in [tuple, list, set, frozenset]:
        return expr.__class__([block_collapse(arg) for arg in expr])
    if expr.__class__ in [Tuple, FiniteSet]:
        return expr.__class__(*[block_collapse(arg) for arg in expr])

    if not expr.is_Matrix or (not expr.is_Add and not expr.is_Mul
            and not expr.is_Transpose and not expr.is_Pow
            and not expr.is_Inverse):
        return expr

    if expr.is_Transpose:
        return Transpose(block_collapse(expr.arg))

    if expr.is_Inverse:
        return Inverse(block_collapse(expr.arg))

    # Recurse on the subargs
    args = list(expr.args)
    for i in range(len(args)):
        arg = args[i]
        newarg = block_collapse(arg)
        while(newarg != arg): # Repeat until no new changes
            arg = newarg
            newarg = block_collapse(arg)
        args[i] = newarg

    if tuple(args) != expr.args:
        expr = expr.__class__(*args)

    # Turn  -[X, Y] into [-X, -Y]
    if (expr.is_Mul and len(expr.args)==2 and not expr.args[0].is_Matrix
            and expr.args[1].is_BlockMatrix):
        return BlockMatrix(expr.args[0]*expr.args[1].mat)

    if expr.is_Add:
        nonblocks = [arg for arg in expr.args if not arg.is_BlockMatrix]
        blocks = [arg for arg in expr.args if arg.is_BlockMatrix]
        if not blocks:
            return MatAdd(*nonblocks)
        block = reduce(lambda a,b: a._blockadd(b), blocks[1:], blocks[0])
        if block.blockshape == (1,1):
            # Bring all the non-blocks into the block_matrix
            mat = Matrix(1, 1, (block[0,0] + MatAdd(*nonblocks), ))
            return BlockMatrix(mat)
        # Add identities to the blocks as block identities
        for i, mat in enumerate(nonblocks):
            c, M = mat.as_coeff_Mul()
            if M.is_Identity and block.is_structurally_symmetric:
                block_id = BlockDiagMatrix(
                        [c*Identity(k) for k in block.rowblocksizes])
                nonblocks.pop(i)
                block = block._blockadd(block_id)


        return MatAdd(*(nonblocks+[block]))

    if expr.is_Mul:
        nonmatrices = [arg for arg in expr.args if not arg.is_Matrix]
        matrices = [arg for arg in expr.args if arg.is_Matrix]
        newmatrices = []
        i = 0
        while (i+1<len(matrices)):
            A, B = matrices[i:i+2]
            if A.is_BlockMatrix and B.is_BlockMatrix:
                matrices[i] = A._blockmul(B)
                matrices.pop(i+1)
            else:
                i+=1
        return MatMul(*(nonmatrices+matrices))

    if expr.is_Pow:
        rv = expr.base
        for i in range(1, expr.exp):
            rv = rv._blockmul(expr.base)
        return rv


