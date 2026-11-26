#!/usr/bin/env python3
"""Mechanical operation counts for every block (Appendix A), both 7P chains
(Table 7) and the closed form of Eq. (8).  Ratios: Table 3, K-163."""
import dag
from dag import var, cost, SymField
import ecc_core

S_M, A_M = 0.356, 0.029
def meq(c): return c[0] + S_M * c[1] + A_M * c[3]
def total(*cs): return tuple(map(sum, zip(*cs)))

def count(fn, nvars, consts=()):
    dag.reset()
    names = ['X1', 'Y1', 'Z1', 'X2', 'Y2', 'Z2'][:nvars]
    vs = [var(n) for n in names]
    cv = {c: var(c) for c in consts}
    out = fn(SymField, vs, cv)
    return cost(list(out), set(cv.values()))

def main():
    print("Block costs, generic curve  (M, S, D, A)")
    rows = [
      ("mdbl-2005-dl", lambda F,v,c: ecc_core.mdbl_2005_dl(F, c['a2'], c['a6'], v[0], v[1]), 2, ('a2','a6')),
      ("dbl-2005-dl",  lambda F,v,c: ecc_core.dbl_2005_dl(F, c['a2'], c['a6'], *v[:3]), 3, ('a2','a6')),
      ("dbl-2005-l",   lambda F,v,c: ecc_core.dbl_2005_l(F, c['a2'], *v[:3]), 3, ('a2',)),
      ("dbl fixed-a2", lambda F,v,c: ecc_core.dbl_fixed_a2(F, c['s6'], *v[:3]), 3, ('s6',)),
      ("madd-2005-dl", lambda F,v,c: ecc_core.madd_2005_dl(F, c['a2'], v[4], v[5], *v[:3]), 6, ('a2',)),
      ("add-2005-dl",  lambda F,v,c: ecc_core.add_2005_dl(F, *v[:3], v[3], v[4], v[5]), 6, ()),
      ("madd LD 9M+4S",lambda F,v,c: ecc_core.madd_lopezdahab(F, c['a2'], *v[:3], v[4], v[5]), 6, ('a2',)),
      ("Yasin-Muda 3P",lambda F,v,c: ecc_core.tripling_yasin_muda(F, c['a2'], v[0], v[1]), 2, ('a2',)),
    ]
    for name, fn, n, consts in rows:
        print(f"  {name:18s} {count(fn, n, consts)}")

    print()
    print("Frozen K-163 blocks (D = 0) and chain totals")
    mdbl, dbl, mix, ng = (1,3,0,4), (3,5,0,3), (8,5,0,9), (0,0,0,1)
    ours = total(mdbl, dbl, dbl, ng, mix)
    his  = total(mdbl, mix, dbl, mix)
    print(f"  1-2-4-8-7 : {ours}  = {meq(ours):.2f} M")
    print(f"  1-2-3-6-7 : {his}  = {meq(his):.2f} M")
    print(f"  margin    : {tuple(a-b for a,b in zip(his,ours))}  = {meq(his)-meq(ours):.2f} M")

    print()
    print("Closed form (3n+6)M + (5n+3)S + (3n+10+eps)A, K-163")
    for n in range(1, 7):
        for eps in (1, 0):
            c = total(mdbl, *([dbl]*(n-1)), mix, tuple(eps*x for x in ng))
            assert c == (3*n+6, 5*n+3, 0, 3*n+10+eps), (n, eps, c)
    print("  verified for n = 1..6, both signs")

if __name__ == "__main__":
    main()
