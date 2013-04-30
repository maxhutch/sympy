from sympy import Basic, Tuple
from sympy.computations.core import (Computation, CompositeComputation, OpComp)
from sympy.rules.tools import subs

def make_getname():
    """ Make a new tokenizer

    Tokenizers maintian state for which variables they have already seen.
    This function makes a new function with a new bound cache
    """

    cache = {}
    seen = set(['', None])

    def getname(key, requested=None):
        """ Get the name associated to a key """
        if key in cache:
            return cache[key]

        if requested:
            name = requested
        elif hasattr(key, 'name'):
            name = key.name
        else:
            name = ''
        if name in seen:
            id = 2
            while(name + '_%d'%id in seen):
                id += 1
            name = name + '_%d'%id

        assert name not in cache.values()
        assert name not in seen

        cache[key] = name
        seen.add(name)
        return name
    return getname


def inplace(x):
    """ Get a dict mapping storage location of each output

    {1: 2} means that the output of index 1 is stored in the input with index 2
    """
    try:
        return x.inplace
    except AttributeError:
        try:
            return x.op.inplace
        except AttributeError:
            pass
    return {}


class Copy(Computation):
    """ A Copy computation """
    pass

def copies_one(comp, getname):
    """ The necessary copies to make an impure computation pure """
    def new_comp(inp, out):
        requested = inp.token if inp.token[0]!='_' else None
        newtoken = getname((inp.expr, out.expr), requested)
        out = ExprToken(inp.expr, newtoken)
        return IOpComp(Copy, (inp,), (out,))

    return [new_comp(comp.inputs[v], comp.outputs[k])
                 for k, v in inplace(comp).items()]

def purify_one(comp, getname):
    """ A pure version of a single impure computation.

    Adds copies and returns a Composite

    See Also
        purify
    """
    copies = copies_one(comp, getname)
    d = dict((cp.inputs[0], cp.outputs[0]) for cp in copies)
    if not d:
        return comp

    inputs = tuple(d[i] if i in d else i for i in comp.inputs)

    newcomp = IOpComp(comp.op, inputs, comp.outputs, inplace(comp))  #.canonicalize() ??

    return CompositeComputation(newcomp, *copies)

def purify(comp, getname):
    """ Pure version of an impure computation

    Adds copies and returns a Composite

    See Also
        purify_one
    """
    if not isinstance(comp, CompositeComputation):
        return purify_one(comp, getname)
    return CompositeComputation(*[purify_one(c, getname)
                                    for c in comp.computations])

class ExprToken(Basic):
    """ A pair of mathematical Expr and computational Token

    The expr contains all necessary mathematical information.
    The token contains all variable information. It is a valid variable name.
    """
    expr = property(lambda self: self.args[0])
    token = property(lambda self: self.args[1])

    def __str__(self):
        return "%s @ %s" %(self.expr, self.token)


def tokenize_one(mathcomp, tokenizer):
    """ Transform mathematical computation into a computation of ExprTokens

    This is the switch from pure math to thinking about variables and memory

    Works on only a single computaion (not a composite)

    See Also
        tokenize
    """
    return IOpComp(type(mathcomp),
                   tuple(ExprToken(i, tokenizer(i)) for i in mathcomp.raw_inputs),
                   tuple(ExprToken(o, tokenizer(o)) for o in mathcomp.outputs),
                   inplace(mathcomp))

def tokenize(mathcomp, tokenizer):
    """ Transform mathematical computation into a computation of ExprTokens

    This is the switch from pure math to thinking about variables and memory

    Works on composites

    See Also
        tokenize_one
    """
    if not isinstance(mathcomp, CompositeComputation):
        return tokenize_one(mathcomp, tokenizer)
    return CompositeComputation(*[tokenize_one(c, tokenizer)
                                    for c in mathcomp.computations])

def inplace_tokenize(comp):
    """ Change tokens to be consistent with inplace dictionaries """
    computations = comp.toposort()
    for i in range(len(computations)):
        c = computations[i]
        d = dict((c.outputs[k], ExprToken(c.outputs[k].expr, c.inputs[v].token))
                for k, v in inplace(c).items())
        if d:
            computations[i:] = map(subs(d), computations[i:])
    return CompositeComputation(*computations)

def remove_single_copies(comp):
    """ Remove unnecessary copies

    The following changes
    In:  a -> Copy -> b -> A -> c
    Out: a -> A -> c

    The following does not change
    In:  a -> Copy -> b -> A -> C
           ->  B   -> c
    """
    users = {}
    computations = comp.toposort()
    for c in computations:
        for inp in c.inputs:
            s = users.get(inp, set())
            s.add(c)
            users[inp] = s

    single_copies = [cp for s in users.values() for cp in s
                        if len(s) == 1 and cp.op == Copy]

    subsrl = subs(dict((cp.outputs[0].token, cp.inputs[0].token)
                        for cp in single_copies))

    return CompositeComputation(*[subsrl(c) for c in computations
                                            if c not in single_copies])

def inplace_compile(comp):
    """ Compile a mathematical computation into a nice inplace one

    This is a master function that calls the following in order

    See Also
        tokenize
        purify
        remove_single_copies
        inplace_tokenize
    """
    tokenizer = make_getname()
    stage0 = comp
    stage1 = tokenize(stage0, tokenizer)
    stage2 = purify(stage1, tokenizer)
    stage3 = remove_single_copies(stage2)
    stage4 = inplace_tokenize(stage3)
    return stage4

class IOpComp(OpComp):
    """ Inplace version of OpComp """

    def __new__(cls, op, inputs, outputs, inpl=None):
        inpl = inpl or inplace(op) or {}
        return Basic.__new__(cls, op, Tuple(*inputs), Tuple(*outputs),
                Tuple(*sorted(inpl.items())))

    inplace = property(lambda self: dict(self.args[3]))
