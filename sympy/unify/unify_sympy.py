from sympy import Basic, Wild, Expr
from unify import Compound, Variable, _unify
from unify import *

def sympy_associative(op):
    from sympy import MatAdd, MatMul, Union, Intersection
    from sympy.core.operations import AssocOp
    assoc_ops = (AssocOp, MatAdd, MatMul, Union, Intersection)
    return any(issubclass(op, aop) for aop in assoc_ops)

def sympy_commutative(op):
    from sympy import Add, MatAdd, Union
    comm_ops = (Add, MatAdd, Union)
    return any(issubclass(op, cop) for cop in comm_ops)

def is_associative(x):
    return isinstance(x, Compound) and sympy_associative(x.op)

def is_commutative(x):
    # return isinstance(x, Compound) and construct(x).is_commutative
    if not isinstance(x, Compound):
        return False
    if sympy_commutative(x.op):
        return True
    if isinstance(x.op, Expr):
        return _build(x).is_commutative

def wildify(s):
    return ("WILD!", s)
def iswild(s):
    return isinstance(s, tuple) and s[0] == "WILD!"
def wildtoken(s):
    return s[1]

def patternify(expr, *wilds):
    from sympy.rules.tools import subs
    repldict = {w: wildify(w) for w in wilds}
    return subs(repldict)(expr)

def destruct(s):
    """ Turn a SymPy object into a Compound Tuple """
    if isinstance(s, Wild):
        return Variable(s)
    if iswild(s):
        return Variable(wildtoken(s))
    if not isinstance(s, Basic) or s.is_Atom:
        return s
    return Compound(s.__class__, tuple(map(destruct, s.args)))

def rebuild(s):
    """ Rebuild a SymPy expression using auto-evaluation """
    return _build(destruct(s))

def _build(t):
    # This function is the same as construct but builds the op in an
    # autoevaluated way. We do this only to get is_commutative. This function
    # should not be used otherwise.
    if isinstance(t, Variable):
        return t.arg
    if not isinstance(t, Compound):
        return t
    # This does auto-evaluation. Watch out!
    return t.op(*map(_build, t.args))

def construct(t):
    """ Turn a Compound Tuple into a SymPy object """
    if isinstance(t, Variable):
        return t.arg
    if not isinstance(t, Compound):
        return t
    return Basic.__new__(t.op, *map(construct, t.args))

def unify(x, y, s, **kwargs):
    """ Structural unification of two expressions possibly containing Wilds

    >>> from unify_sympy import unify
    >>> from sympy import Wild
    >>> from sympy.abc import x, y, z
    >>> expr = 2*x + y + z
    >>> pattern = 2*Wild('p') + Wild('q')
    >>> list(unify(expr, pattern, {}))
    [{p_: x, q_: y + z}]

    >>> expr = x + y + z
    >>> pattern = Wild('p') + Wild('q')
    >>> list(unify(expr, pattern, {}))
    [{p_: z, q_: x + y}, {p_: y + z, q_: x}]
    """

    ds = _unify(destruct(x), destruct(y), {}, is_associative=is_associative,
                                              is_commutative=is_commutative,
                                              **kwargs)
    for d in ds:
        yield {construct(k): construct(v) for k, v in d.items()}