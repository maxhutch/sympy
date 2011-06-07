from sympy import (
    Symbol, Set, Union, Interval, oo, S,
    Inequality, Max, Min, And, Or, Eq, Le, Lt, Float, FiniteSet
)
from sympy.mpmath import mpi

from sympy.utilities.pytest import raises

def test_interval_arguments():
    assert Interval(0, oo) == Interval(0, oo, False, True)
    assert Interval(0, oo).right_open == True
    assert Interval(-oo, 0) == Interval(-oo, 0, True, False)
    assert Interval(-oo, 0).left_open == True

    assert isinstance(Interval(1, 1), FiniteSet)

    assert Interval(1, 0) == S.EmptySet
    assert Interval(1, 1).measure == 0

    assert Interval(1, 1, False, True) == S.EmptySet
    assert Interval(1, 1, True, False) == S.EmptySet
    assert Interval(1, 1, True, True) == S.EmptySet

    raises(ValueError, "Interval(0, S.ImaginaryUnit)")
    raises(ValueError, "Interval(0, Symbol('z'))")

    assert isinstance(Interval(1, Symbol('a', real=True)), Interval)

def test_interval_symbolic_end_points():
    a = Symbol('a', real=True)

    assert Union(Interval(0, a), Interval(0, 3)).sup == Max(a, 3)
    assert Union(Interval(a, 0), Interval(-3, 0)).inf == Min(-3, a)

    assert Interval(0, a).contains(1) == Inequality(1, a)

def test_union():
    assert Union(Interval(1, 2), Interval(2, 3)) == Interval(1, 3)
    assert Union(Interval(1, 2), Interval(2, 3, True)) == Interval(1, 3)
    assert Union(Interval(1, 3), Interval(2, 4)) == Interval(1, 4)
    assert Union(Interval(1, 2), Interval(1, 3)) == Interval(1, 3)
    assert Union(Interval(1, 3), Interval(1, 2)) == Interval(1, 3)
    assert Union(Interval(1, 3, False, True), Interval(1, 2)) == \
           Interval(1, 3, False, True)
    assert Union(Interval(1, 3), Interval(1, 2, False, True)) == Interval(1, 3)
    assert Union(Interval(1, 2, True), Interval(1, 3)) == Interval(1, 3)
    assert Union(Interval(1, 2, True), Interval(1, 3, True)) == Interval(1, 3, True)
    assert Union(Interval(1, 2, True), Interval(1, 3, True, True)) == \
           Interval(1, 3, True, True)
    assert Union(Interval(1, 2, True, True), Interval(1, 3, True)) == \
           Interval(1, 3, True)
    assert Union(Interval(1, 3), Interval(2, 3)) == Interval(1, 3)
    assert Union(Interval(1, 3, False, True), Interval(2, 3)) == \
           Interval(1, 3)
    assert Union(Interval(1, 2, False, True), Interval(2, 3, True)) != \
           Interval(1, 3)
    assert Union(Interval(1, 2), S.EmptySet) == Interval(1, 2)
    assert Union(S.EmptySet) == S.EmptySet

    assert Interval(1, 2).union(Interval(2, 3)) == \
           Interval(1, 2) + Interval(2, 3)

    assert Interval(1, 2).union(Interval(2, 3)) == Interval(1, 3)

    assert Union(Set()) == Set()

    # Test that Intervals and FiniteSets play nicely
    assert Interval(1,3) + FiniteSet(2) == Interval(1,3)
    assert Interval(1,3, True,True) + FiniteSet(3) == Interval(1,3, True,False)
    X = Interval(1,3)+FiniteSet(5)
    Y = Interval(1,2)+FiniteSet(3)
    XandY = X.intersect(Y)
    assert 2 in X and 3 in X and 3 in XandY
    assert X.subset(XandY) and Y.subset(XandY)


    raises(ValueError, "Union(1, 2, 3)")

def test_difference():
    assert Interval(1, 3) - Interval(1, 2) == Interval(2, 3, True)
    assert Interval(1, 3) - Interval(2, 3) == Interval(1, 2, False, True)
    assert Interval(1, 3, True) - Interval(2, 3) == Interval(1, 2, True, True)
    assert Interval(1, 3, True) - Interval(2, 3, True) == \
           Interval(1, 2, True, False)

def test_complement():
    assert Interval(0, 1).complement == \
           Union(Interval(-oo, 0, True, True), Interval(1, oo, True, True))
    assert Interval(0, 1, True, False).complement == \
           Union(Interval(-oo, 0, True, False), Interval(1, oo, True, True))
    assert Interval(0, 1, False, True).complement == \
           Union(Interval(-oo, 0, True, True), Interval(1, oo, False, True))
    assert Interval(0, 1, True, True).complement == \
           Union(Interval(-oo, 0, True, False), Interval(1, oo, False, True))

    assert -S.EmptySet == S.EmptySet.complement
    assert ~S.EmptySet == S.EmptySet.complement

    assert S.EmptySet.complement == Interval(-oo, oo)

    assert Union(Interval(0, 1), Interval(2, 3)).complement == \
           Union(Interval(-oo, 0, True, True), Interval(1, 2, True, True),
                 Interval(3, oo, True, True))

    assert FiniteSet(0).complement == Union(Interval(-oo,0, True,True) ,
            Interval(0,oo, True, True))
    X = Interval(1,3)+FiniteSet(5)
    assert X.intersect(X.complement) == S.EmptySet


def test_intersect():
    x = Symbol('x')
    assert Interval(0, 2).intersect(Interval(1, 2)) == Interval(1, 2)
    assert Interval(0, 2).intersect(Interval(1, 2, True)) == \
           Interval(1, 2, True)
    assert Interval(0, 2, True).intersect(Interval(1, 2)) == \
           Interval(1, 2, False, False)
    assert Interval(0, 2, True, True).intersect(Interval(1, 2)) == \
           Interval(1, 2, False, True)
    assert Interval(0, 2).intersect(Union(Interval(0, 1), Interval(2, 3))) == \
           Union(Interval(0, 1), Interval(2, 2))

    assert FiniteSet(1,2,x).intersect(FiniteSet(x)) == FiniteSet(x)
    assert Interval(0,5).intersect(FiniteSet(1,3)) == FiniteSet(1,3)
    assert Interval(0,1, True, True).intersect(FiniteSet(1)) == S.EmptySet

    assert Union(Interval(0, 1), Interval(2, 3)).intersect(Interval(1, 2)) == \
           Union(Interval(1, 1), Interval(2, 2))
    assert Union(Interval(0, 1), Interval(2, 3)).intersect(Interval(0, 2)) == \
           Union(Interval(0, 1), Interval(2, 2))
    assert Union(Interval(0, 1), Interval(2, 3)).intersect(Interval(1, 2, True, True)) == \
           S.EmptySet
    assert Union(Interval(0, 1), Interval(2, 3)).intersect(S.EmptySet) == \
           S.EmptySet

def test_interval_subs():
    a = Symbol('a', real=True)

    assert Interval(0, a).subs(a, 2) == Interval(0, 2)
    assert Interval(a, 0).subs(a, 2) == S.EmptySet

def test_interval_evalf():
    assert Interval(0, 1).evalf() == mpi(0, 1)
    assert Interval(0, 1, True, False).evalf() == mpi(0, 1)

def test_measure():
    a = Symbol('a', real=True)

    assert Interval(1, 3).measure == 2
    assert Interval(0, a).measure == a
    assert Interval(1, a).measure == a - 1

    assert Union(Interval(1, 2), Interval(3, 4)).measure == 2

    assert FiniteSet(1,2,oo,a,-oo,-5).measure == 0

    assert S.EmptySet.measure == 0

def test_subset():
    assert Interval(0, 2).subset(Interval(0, 1)) == True
    assert Interval(0, 2).subset(Interval(0, 3)) == False

    assert FiniteSet(1,2,3,4).subset(FiniteSet(1,2))
    assert Interval(0,2).subset(FiniteSet(1))
    assert (Interval(0,2,False,True)+FiniteSet(2,3)).subset(
            Interval(1,2)+FiniteSet(3))

    assert Union(Interval(0, 1), Interval(2, 5)).subset(Interval(3, 4)) == True
    assert Union(Interval(0, 1), Interval(2, 5)).subset(Interval(3, 6)) == False

    assert S.EmptySet.subset(Interval(0, 1)) == False
    assert S.EmptySet.subset(S.EmptySet) == True

    raises(ValueError, "S.EmptySet.subset(1)")

def test_contains():
    assert Interval(0, 2).contains(1) == True
    assert Interval(0, 2).contains(3) == False
    assert Interval(0, 2, True, False).contains(0) == False
    assert Interval(0, 2, True, False).contains(2) == True
    assert Interval(0, 2, False, True).contains(0) == True
    assert Interval(0, 2, False, True).contains(2) == False
    assert Interval(0, 2, True, True).contains(0) == False
    assert Interval(0, 2, True, True).contains(2) == False

    assert FiniteSet(1,2,3).contains(2)
    assert FiniteSet(1,2,Symbol('x')).contains(Symbol('x'))

    assert Union(Interval(0, 1), Interval(2, 5)).contains(3) == True
    assert Union(Interval(0, 1), Interval(2, 5)).contains(6) == False

    assert S.EmptySet.contains(1) == False

def test_interval_symbolic():
    x = Symbol('x')
    e = Interval(0, 1)
    assert e.contains(x) == And(0<=x, x<=1)
    raises(TypeError, "x in e")
    e = Interval(0, 1, True, True)
    assert e.contains(x) == And(0<x, x<1)

def test_union_contains():
    x = Symbol('x')
    i1 = Interval(0, 1)
    i2 = Interval(2, 3)
    i3 = Union(i1, i2)
    raises(TypeError, "x in i3")
    e = i3.contains(x)
    assert e == Or(And(0 <= x, x <= 1), And(2 <= x, x <= 3))
    assert e.subs(x, -0.5) is False
    assert e.subs(x, 0.5) is True
    assert e.subs(x, 1.5) is False
    assert e.subs(x, 2.5) is True
    assert e.subs(x, 3.5) is False

    U = Interval(0,2, True,True) + Interval(10,oo) + FiniteSet(-1,2,5,6)
    assert not any(el in U for el in [0,4,-oo])
    assert all(el in U for el in [2,5,10])

def test_is_number():
    assert Interval(0, 1).is_number is False
    assert Set().is_number is False

def test_Interval_is_left_unbounded():
    assert Interval(3, 4).is_left_unbounded == False
    assert Interval(-oo, 3).is_left_unbounded == True
    assert Interval(Float("-inf"), 3).is_left_unbounded == True

def test_Interval_is_right_unbounded():
    assert Interval(3, 4).is_right_unbounded == False
    assert Interval(3, oo).is_right_unbounded == True
    assert Interval(3, Float("+inf")).is_right_unbounded == True

def test_Interval_as_relational():
    x = Symbol('x')

    assert Interval(-1, 2, False, False).as_relational(x) == And(Le(-1, x), Le(x, 2))
    assert Interval(-1, 2, True, False).as_relational(x) == And(Lt(-1, x), Le(x, 2))
    assert Interval(-1, 2, False, True).as_relational(x) == And(Le(-1, x), Lt(x, 2))
    assert Interval(-1, 2, True, True).as_relational(x) == And(Lt(-1, x), Lt(x, 2))

    assert Interval(-oo, 2, right_open=False).as_relational(x) == Le(x, 2)
    assert Interval(-oo, 2, right_open=True).as_relational(x) == Lt(x, 2)

    assert Interval(-2, oo, left_open=False).as_relational(x) == Le(-2, x)
    assert Interval(-2, oo, left_open=True).as_relational(x) == Lt(-2, x)

    assert Interval(-oo, oo).as_relational(x) == True

def test_finite_basic():
    x = Symbol('x')
    A = FiniteSet(1,2,3)
    B = FiniteSet(3,4,5)
    AorB = Union(A,B)
    AandB = A.intersect(B)
    assert AorB.subset(A) and AorB.subset(B)
    assert A.subset(AandB)
    assert AandB == FiniteSet(3)


