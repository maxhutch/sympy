"""Module for Sympy containers

    (Sympy objects that store other Sympy objects)

    The containers implemented in this module are subclassed to Basic.
    They are supposed to work seamlessly within the Sympy framework.
"""

from basic import Basic
from sympify import sympify

class Tuple(Basic):
    """
    Wrapper around the builtin tuple object

    The Tuple is a subclass of Basic, so that it works well in the
    Sympy framework.  The wrapped tuple is available as self.args, but
    you can also access elements or slices with [:] syntax.

    >>> from sympy import symbols
    >>> from sympy.core.containers import Tuple
    >>> a, b, c, d = symbols('a b c d')
    >>> Tuple(a, b, c)[1:]
    (b, c)
    >>> Tuple(a, b, c).subs(a, d)
    (d, b, c)

    """

    def __new__(cls, *args, **assumptions):
        args = [ sympify(arg) for arg in args ]
        obj = Basic.__new__(cls, *args, **assumptions)
        return obj

    def __getitem__(self,i):
        if isinstance(i,slice):
            indices = i.indices(len(self))
            return Tuple(*[self.args[i] for i in range(*indices)])
        return self.args[i]

    def __len__(self):
        return len(self.args)

    def __contains__(self, item):
        return item in self.args

    def __iter__(self):
        return iter(self.args)

    def __add__(self, other):
        if isinstance(other, Tuple):
            return Tuple(*(self.args + other.args))
        elif isinstance(other, tuple):
            return Tuple(*(self.args + other))
        else:
            return NotImplemented

    def __radd__(self, other):
        if isinstance(other, Tuple):
            return Tuple(*(other.args + self.args))
        elif isinstance(other, tuple):
            return Tuple(*(other + self.args))
        else:
            return NotImplemented

    def __eq__(self, other):
        if isinstance(other, Basic):
            return super(Tuple, self).__eq__(other)
        return self.args == other

    def __ne__(self, other):
        if isinstance(other, Basic):
            return super(Tuple, self).__ne__(other)
        return self.args != other

    def __hash__(self):
        return hash(self.args)

    def _to_mpmath(self, prec):
        return tuple([a._to_mpmath(prec) for a in self.args])


def tuple_wrapper(method):
    """
    Decorator that converts any tuple in the function arguments into a Tuple.

    The motivation for this is to provide simple user interfaces.  The user can
    call a function with regular tuples in the argument, and the wrapper will
    convert them to Tuples before handing them to the function.

    >>> from sympy.core.containers import tuple_wrapper, Tuple
    >>> def f(*args):
    ...    return args
    >>> g = tuple_wrapper(f)

    The decorated function g sees only the Tuple argument:

    >>> g(0, (1, 2), 3)
    (0, (1, 2), 3)

    """
    def wrap_tuples(*args, **kw_args):
        newargs=[]
        for arg in args:
            if type(arg) is tuple:
                newargs.append(Tuple(*arg))
            else:
                newargs.append(arg)
        return method(*newargs, **kw_args)
    return wrap_tuples

class Dict(Basic):
    """
    Wrapper around the builtin dict object

    The Dict is a subclass of Basic, so that it works well in the
    Sympy framework.  The wrapped dict is accessible through the normal
    dict accessor methods.

    >>> from sympy.core.containers import Dict

    >>> D = Dict({1:'one', 2:'two'})
    >>> D[1]
    one
    >>> for k, v in D: print k, v
    1 one
    2 two

    """

    def __new__(cls, d):
        items = [Tuple(k,v) for k, v in d.items()]
        obj = Basic.__new__(cls, *items)
        obj._dict = dict(items) # In case Tuple decides it wants to Sympify
        return obj

    def __getitem__(self, key):
        """x.__getitem__(y) <==> x[y]"""
        return self._dict[key]

    def __setitem__(self, key, value):
        raise NotImplementedError("SymPy Dicts are Immutable")

    def items(self):
        '''D.items() -> list of D's (key, value) pairs, as 2-tuples'''
        return self.args

    def iteritems(self):
        '''D.iteritems() -> an iterator over the (key, value) items of D'''
        return self.args.__iter__()

    def iterkeys(self):
        '''D.iterkeys() -> an iterator over the keys of D'''
        return (k for k,v in self.iteritems())

    def keys(self):
        '''D.keys() -> list of D's keys'''
        return list(self.iterkeys())

    def itervalues(self):
        '''D.itervalues() -> an iterator over the values of D'''
        return (v for k,v in self.iteritems())

    def values(self):
        '''D.values() -> list of D's values'''
        return list(self.itervalues())

    def __iter__(self):
        '''x.__iter__() <==> iter(x)'''
        return self.iteritems()

    def __len__(self):
        '''x.__len__() <==> len(x)'''
        return self._dict.__len__()

    def __repr__(self):
        return self._dict.__repr__()

    def get(self, key, default):
        '''D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None.'''
        return self._dict.get(key, default)

    def has_key(self, key):
        '''D.has_key(k) -> True if D has a key k, else False'''
        return self._dict.has_key(key)

    def __contains__(self, key):
        '''D.__contains__(k) -> True if D has a key k, else False'''
        return self.has_key(key)

