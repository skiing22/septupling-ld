#!/usr/bin/env python3
"""
Correctness checks of Section 4.4 (Python check).

Every test is EXHAUSTIVE over the affine points of small curves
y^2 + xy = x^3 + a2 x^2 + a6,  a2 in {0,1},  a6 in {1,3,5},
over GF(2^5), GF(2^7), GF(2^9) and GF(2^11); not sampled.

  A  every block of Table 2 (and the comparators) against the affine group law,
     with projective inputs given as (mu X : mu^2 Y : mu), mu in {1, 2, 3}
  B  the chain of Eq. (7), 1 -> 2 -> 4 -> 8 -> 7, on every input with
     7P, 8P, 9P != O (the hypotheses of the validity theorem, Section 4.1)
  C  the chain of Eq. (6), 1 -> 2 -> 3 -> 6 -> 7, on every input with
     2P, 3P, 5P, 6P, 7P != O (its valid inputs)

Expected result: TOTAL FAILURES: 0.
"""
from ecc_core import *

RESULTS = {}
EXCLUDED = {"B": 0, "C": 0}

def record(name, ok):
    a, b = RESULTS.get(name, (0, 0))
    RESULTS[name] = (a + 1, b + (0 if ok else 1))

def run():
    for m, poly in FIELDS.items():
        F = GF(m, poly)
        for a2 in (0, 1):
            for a6 in (1, 3, 5):
                s6 = F.sqrt(a6)
                for P in points(F, a2, a6):
                    x1, y1 = P
                    if x1 == 0:          # point of order 2
                        continue
                    k = {n: amul(F, a2, a6, n, P) for n in range(2, 10)}

                    # ---- Check A: each block against the affine group law ----
                    record("A  mdbl-2005-dl",
                           ld_to_affine(F, mdbl_2005_dl(F, a2, a6, x1, y1)) == k[2])
                    for mu in (1, 2, 3):
                        R = ld_lift(F, P, mu)
                        record("A  dbl-2005-dl",
                               ld_to_affine(F, dbl_2005_dl(F, a2, a6, *R)) == k[2])
                        record("A  dbl-2005-l",
                               ld_to_affine(F, dbl_2005_l(F, a2, *R)) == k[2])
                        if a2 == 1:
                            record("A  fixed-a2 doubling",
                                   ld_to_affine(F, dbl_fixed_a2(F, s6, *R)) == k[2])
                    if k[2] is not O and k[2][0] and k[3] is not O:
                        Q2 = ld_lift(F, k[2], 3)
                        record("A  madd-2005-dl",
                               ld_to_affine(F, madd_2005_dl(F, a2, x1, y1, *Q2)) == k[3])
                        for mu in (1, 2, 3):
                            record("A  add-2005-dl",
                                   ld_to_affine(F, add_2005_dl(F, *ld_lift(F, P, mu), *Q2)) == k[3])
                        record("A  madd Lopez-Dahab (comparator)",
                               ld_to_affine(F, madd_lopezdahab(F, a2, *Q2, x1, y1)) == k[3])
                        record("A  tripling of Yasin et al. (comparator)",
                               ld_to_affine(F, tripling_yasin_muda(F, a2, x1, y1)) == k[3])

                    # ---- Check B: chain of Eq. (7), 1 -> 2 -> 4 -> 8 -> 7 ----
                    if any(k[n] is O for n in (7, 8, 9)):
                        EXCLUDED["B"] += 1
                    else:
                        nP = neg(F, P)
                        T2 = mdbl_2005_dl(F, a2, a6, x1, y1)
                        if a2 == 1:
                            T4 = dbl_fixed_a2(F, s6, *T2)
                            T8 = dbl_fixed_a2(F, s6, *T4)
                        else:
                            T4 = dbl_2005_dl(F, a2, a6, *T2)
                            T8 = dbl_2005_dl(F, a2, a6, *T4)
                        got = ld_to_affine(F, madd_2005_dl(F, a2, nP[0], nP[1], *T8))
                        record("B  chain of Eq. (7) = 7P", got == k[7])

                    # ---- Check C: chain of Eq. (6), 1 -> 2 -> 3 -> 6 -> 7 ----
                    if any(k[n] is O for n in (2, 3, 5, 6, 7)):
                        EXCLUDED["C"] += 1
                    else:
                        T2 = mdbl_2005_dl(F, a2, a6, x1, y1)
                        T3 = madd_2005_dl(F, a2, x1, y1, *T2)
                        T6 = dbl_2005_dl(F, a2, a6, *T3)
                        got = ld_to_affine(F, madd_2005_dl(F, a2, x1, y1, *T6))
                        record("C  chain of Eq. (6) = 7P", got == k[7])

    width = max(len(n) for n in RESULTS)
    total = 0
    for name in sorted(RESULTS):
        n, f = RESULTS[name]
        total += f
        print(f"  {name:<{width}} : {n:7d} cases, {f} failures")
    print()
    print(f"  inputs outside the hypotheses of B (7P, 8P or 9P = O)        : {EXCLUDED['B']}")
    print(f"  inputs outside the valid set of C (2P, 3P, 5P, 6P or 7P = O) : {EXCLUDED['C']}")
    print()
    print("TOTAL FAILURES:", total)
    return total

if __name__ == "__main__":
    import sys
    print("Correctness checks (exhaustive over small curves)")
    print()
    sys.exit(1 if run() else 0)
