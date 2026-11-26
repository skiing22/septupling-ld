"""
Hash-consed expression DAG over GF(2), used to count operations mechanically.

Two structurally identical expressions become the SAME node, so building several
blocks back to back and then counting the distinct nodes reachable from the
outputs performs common-subexpression elimination across block boundaries.
That is what "fusing a chain" means in Section 5.2 of the paper.

Simplifications applied (all valid in characteristic 2):
    a + a = 0     a + 0 = a     a * 1 = a     a * 0 = 0
    sqr(0) = 0    sqr(1) = 1    + and * are commutative (operands sorted)
"""

NODES = {}
KIND = []
ZERO = ONE = None

def reset():
    global NODES, KIND, ZERO, ONE
    NODES, KIND = {}, []
    ZERO = _intern(('zero',))
    ONE = _intern(('one',))

def _intern(key):
    if key in NODES:
        return NODES[key]
    i = len(KIND)
    NODES[key] = i
    KIND.append(key)
    return i

def var(name):
    return _intern(('var', name))

def add(a, b):
    if a == ZERO: return b
    if b == ZERO: return a
    if a == b:    return ZERO            # characteristic 2
    if a > b:     a, b = b, a
    return _intern(('add', a, b))

def mul(a, b):
    if a == ZERO or b == ZERO: return ZERO
    if a == ONE:  return b
    if b == ONE:  return a
    if a > b:     a, b = b, a
    return _intern(('mul', a, b))

def sqr(a):
    if a in (ZERO, ONE):
        return a
    return _intern(('sqr', a))

def cost(roots, constants=()):
    """Distinct operation nodes reachable from roots, as (M, S, D, A).
       A multiplication with one operand in `constants` is counted as D."""
    constants = set(constants)
    seen, stack = set(), list(roots)
    M = S = D = A = 0
    while stack:
        n = stack.pop()
        if n in seen:
            continue
        seen.add(n)
        k = KIND[n]
        if k[0] == 'add':
            A += 1
            stack += [k[1], k[2]]
        elif k[0] == 'sqr':
            S += 1
            stack.append(k[1])
        elif k[0] == 'mul':
            if k[1] in constants or k[2] in constants:
                D += 1
            else:
                M += 1
            stack += [k[1], k[2]]
    return (M, S, D, A)

class SymField:
    """Drop-in replacement for GF, so the ecc_core blocks can be run symbolically."""
    add = staticmethod(add)
    mul = staticmethod(mul)
    sqr = staticmethod(sqr)

reset()
