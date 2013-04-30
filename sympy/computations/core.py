import itertools
from sympy import Basic

def unique(seq):
    seen = set()
    for item in seq:
        if item not in seen:
            seen.add(item)
            yield item

def intersect(a, b):
    return not not set(a).intersection(set(b))

class Computation(Basic):
    """ An interface for a Computation

    Computations have inputs and outputs
    """

    inputs  = None
    outputs = None

    def edges(self):
        inedges  = ((i, self) for i in self.inputs)
        outedges = ((self, o) for o in self.outputs)
        return itertools.chain(inedges, outedges)

    @property
    def variables(self):
        return itertools.chain(self.inputs, self.outputs)

    def __add__(self, other):
        return CompositeComputation(self, other)

    def __str__(self):
        ins  = "["+', '.join(map(str, self.inputs)) +"]"
        outs = "["+', '.join(map(str, self.outputs))+"]"
        return "%s -> %s -> %s"%(ins, str(self.__class__.__name__), outs)

    def toposort(self):
        return [self]


class CompositeComputation(Computation):
    """ A computation composed of other computations """


    def __new__(cls, *args):
        obj = Basic.__new__(cls, *args)
        obj = obj.canonicalize()
        return obj

    computations = property(lambda self: self.args)

    def _input_outputs(self):
        """ Find the inputs and outputs of the complete computation """
        allin = tuple(unique(itertools.chain(
                        *[c.inputs  for c in self.computations])))
        allout = tuple(unique(itertools.chain(
                        *[c.outputs for c in self.computations])))
        inputs  = [i for i in allin  if i not in allout]
        outputs = [o for o in allout if o not in allin]
        return tuple(inputs), tuple(outputs)

    @property
    def inputs(self):
        return self._input_outputs()[0]

    @property
    def outputs(self):
        return self._input_outputs()[1]

    @property
    def variables(self):
        return unique(itertools.chain(
                        *[c.variables for c in self.computations]))

    def __str__(self):
        return "[[" + ", ".join(map(str, self.computations)) + "]]"

    def edges(self):
        return itertools.chain(*[c.edges() for c in self.computations])

    def dag_io(self):
        """ Return a dag of computations from inputs to outputs

        returns {A: {Bs}} such that A must occur before each of the Bs
        """
        return {A: set([B for B in self.computations
                          if intersect(A.outputs, B.inputs)])
                    for A in self.computations}

    def dag_oi(self):
        """ Return a dag of computations from outputs to inputs

        returns {A: {Bs}} such that A requires each of the Bs before it runs
        """
        return {A: set([B for B in self.computations
                          if intersect(A.inputs, B.outputs)])
                    for A in self.computations}

    def toposort(self):
        """ Order computations in an executable order """
        from sympy.utilities.iterables import _toposort
        return _toposort(self.dag_io())

    def canonicalize(self):
        from sympy.rules import exhaust, do_one, flatten, unpack, typed, sort
        return exhaust(typed({CompositeComputation:
                       do_one(rm_identity, flatten, unpack, sort(str))}))(self)

def rm_identity(comp):
    """ Remove or reduce unnecessary identities """
    for c in comp.computations:
        if isinstance(c, Identity):
            others = [x for x in comp.computations if x != c]
            other_outputs = set([o for other in others for o in other.outputs])
            outputs = [o for o in c.outputs if o not in other_outputs]
            if not outputs:
                return type(comp)(*others)
            if tuple(outputs) != c.outputs:
                newident = Identity(*outputs)
                return type(comp)(newident, *others)
    return comp

class Identity(Computation):
    inputs = property(lambda self: self.args)
    outputs = inputs
