#!/usr/bin/env python3
"""
Design-space search (Section 5.2): every combination of published LD blocks for
the chain 1 -> 2 -> 4 -> 8 -> 7 on K-163, costed unfused and fused.

Expected result: no combination costs fewer than 15 multiplications.
"""
import itertools
import dag
from dag import var, add, cost, SymField
import ecc_core

S_M, A_M = 0.356, 0.029     # Table 3, K-163
def meq(c): return c[0] + S_M*c[1] + A_M*c[3]

ONE = None
def DBL(name):
    F = SymField
    return {
        'dl': lambda X, Y, Z: ecc_core.dbl_2005_dl(F, dag.ONE, dag.ONE, X, Y, Z),
        'l7': lambda X, Y, Z: ecc_core.dbl_2005_l(F, dag.ONE, X, Y, Z),
        'a2': lambda X, Y, Z: ecc_core.dbl_fixed_a2(F, dag.ONE, X, Y, Z),
    }[name]
def MADD(name):
    F = SymField
    return {
        'AD':  lambda x, y, X, Y, Z: ecc_core.madd_2005_dl(F, dag.ONE, x, y, X, Y, Z),
        'LDm': lambda x, y, X, Y, Z: ecc_core.madd_lopezdahab(F, dag.ONE, X, Y, Z, x, y),
    }[name]

def standalone(kind, name):
    dag.reset()
    if kind == 'mdbl':
        o = (DBL(name)(var('X'), var('Y'), dag.ONE) if name != 'dl'
             else ecc_core.mdbl_2005_dl(SymField, dag.ONE, dag.ONE, var('X'), var('Y')))
    elif kind == 'dbl':
        o = DBL(name)(var('X'), var('Y'), var('Z'))
    else:
        o = MADD(name)(var('x'), var('y'), var('X'), var('Y'), var('Z'))
    return cost(list(o))

def chain(s1, s2, s3, fin):
    dag.reset()
    X1, Y1 = var('X1'), var('Y1')
    P2 = (ecc_core.mdbl_2005_dl(SymField, dag.ONE, dag.ONE, X1, Y1) if s1 == 'dl'
          else DBL(s1)(X1, Y1, dag.ONE))
    P4 = DBL(s2)(*P2)
    P8 = DBL(s3)(*P4)
    P7 = MADD(fin)(X1, add(X1, Y1), *P8)
    return cost(list(P7))

def main():
    print("Standalone block costs on K-163  (M, S, D, A)")
    for n in ('dl', 'l7', 'a2'):
        print(f"   mdbl {n}: {standalone('mdbl', n)}     dbl {n}: {standalone('dbl', n)}")
    for n in ('AD', 'LDm'):
        print(f"   madd {n}: {standalone('madd', n)}")
    print()
    rows = []
    for s1, s2, s3, fin in itertools.product(('dl','l7','a2'), ('dl','l7','a2'),
                                             ('dl','l7','a2'), ('AD','LDm')):
        unf = [0,0,0,0]
        for c in (standalone('mdbl', s1), standalone('dbl', s2),
                  standalone('dbl', s3), standalone('madd', fin)):
            unf = [a+b for a, b in zip(unf, c)]
        unf[3] += 1                                    # negation of P
        fus = chain(s1, s2, s3, fin)
        rows.append((meq(fus), (s1,s2,s3,fin), tuple(unf), fus))
    rows.sort()
    print(f"{'rank':>4}  {'steps':16s} {'unfused':>16s} {'fused':>16s}   M-eq")
    for i, (m, k, u, f) in enumerate(rows[:8], 1):
        print(f"{i:4d}  {'/'.join(k):16s} {u[0]:3d}M {u[1]:2d}S {u[3]:2d}A   "
              f"{f[0]:3d}M {f[1]:2d}S {f[3]:2d}A   {m:.3f}")
    print(f"   ... {len(rows)} combinations in total")
    print(f"   minimum multiplication count over all combinations: "
          f"{min(f[0] for _,_,_,f in rows)}")

if __name__ == "__main__":
    main()
