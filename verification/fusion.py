#!/usr/bin/env python3
"""
Fusion analysis (Section 5.2, Proposition on fusion).

Builds the chain 1 -> 2 -> 4 -> 8 -> 7 in a single hash-consed DAG, so common
subexpressions are eliminated across block boundaries.  Expected result: the
fused program saves one squaring and no multiplication; a further addition is
saved by hand, because C = X1 + (X1+Y1) = Y1 in characteristic 2.
"""
import dag
from dag import var, add, cost, SymField
import ecc_core

def build(k163=True):
    dag.reset()
    X1, Y1 = var('X1'), var('Y1')
    if k163:
        a2 = a6 = s6 = dag.ONE
        consts = set()
    else:
        a2, a6, s6 = dag.ONE, var('a6'), var('s6')      # a2 = 1 required by fixed-a2
        consts = {a6, s6}
    F = SymField
    P2 = ecc_core.mdbl_2005_dl(F, a2, a6, X1, Y1)
    P4 = ecc_core.dbl_fixed_a2(F, s6, *P2)
    P8 = ecc_core.dbl_fixed_a2(F, s6, *P4)
    negY = add(X1, Y1)
    P7 = ecc_core.madd_2005_dl(F, a2, X1, negY, *P8)
    return (P2, P4, P8, P7), consts

def main():
    for label, k163 in (("K-163 (a2 = a6 = 1)", True), ("a2 = 1, a6 symbolic", False)):
        (P2, P4, P8, P7), consts = build(k163)
        print(label)
        for name, pt in (("2P", P2), ("4P", P4), ("8P", P8), ("7P", P7)):
            print(f"   cumulative after {name}: {cost(list(pt), consts)}")
        fused = cost(list(P7), consts)
        unf = (15, 18, 0, 20) if k163 else (15, 18, 3, 20)
        print(f"   unfused chain            : {unf}")
        print(f"   fused (structural CSE)   : {fused}")
        print(f"   plus C = X1+(X1+Y1) = Y1 : one further addition, by inspection")
        print(f"   saving                   : "
              f"{tuple(a-b for a,b in zip(unf, fused))} and 1 more A")
        print()

if __name__ == "__main__":
    main()
