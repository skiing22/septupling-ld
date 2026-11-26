#!/usr/bin/env python3
"""enumerate_chains.py -- Table 10: every addition-subtraction chain of length at most n+2
reaching N (values in (0, 4N], each chain stopped at its first arrival at N), costed with
Definition 7 and the K-163 blocks of Table 5.  Pure Python, no dependencies.
Usage: python3 enumerate_chains.py [S/M] [A/M]   (weights only rank the tuples)"""
import sys
SM = float(sys.argv[1]) if len(sys.argv) > 1 else 0.80
AM = float(sys.argv[2]) if len(sys.argv) > 2 else 0.094
CMDBL, CDBL, CMIX, CADD = (1, 3, 4), (3, 5, 3), (8, 5, 9), (13, 4, 9)
NEG_P, NEG_R = (0, 0, 1), (1, 0, 1)
def plus(*ts): return tuple(map(sum, zip(*ts)))
def w(t): return t[0] + SM * t[1] + AM * t[2]

def run(N, n):
    L, found = n + 2, []
    def rec(seq, steps):
        if len(seq) > 1 and seq[-1] == N:
            found.append((list(seq), list(steps))); return
        if len(seq) - 1 >= L: return
        for j in range(len(seq)):
            for k in range(len(seq)):
                for sgn in (1, -1):
                    v = seq[j] + sgn * seq[k]
                    if 0 < v <= 4 * N and (sgn == 1 or j != k):
                        if sgn == 1 and k < j: continue          # a+b = b+a
                        rec(seq + [v], steps + [(j, k, sgn)])
    rec([1], [])
    best = {}
    for seq, steps in found:
        cost, vals = (0, 0, 0), seq
        for i, (j, k, sgn) in enumerate(steps):
            same = (vals[j] == vals[k]) if sgn == 1 else (vals[j] == -vals[k])
            if same:   blk = CMDBL if j == 0 else CDBL
            elif j == 0 or k == 0: blk = CMIX
            else:      blk = CADD
            cost = plus(cost, blk)
            if sgn == -1: cost = plus(cost, NEG_P if k == 0 else NEG_R)
        key = tuple(seq)
        if key not in best or w(cost) < w(best[key]): best[key] = cost
    ranked = sorted(best.items(), key=lambda kv: w(kv[1]))
    top = w(ranked[0][1]); minimisers = [r for r in ranked if abs(w(r[1]) - top) < 1e-9]
    return len(best), min(len(s) - 1 for s, _ in found), minimisers   # chains = distinct value sequences

rows = [(7, 3, "2^3-1"), (3, 2, "2^2-1"), (15, 4, "2^4-1"), (31, 5, "2^5-1"),
        (3, 1, "2^1+1"), (5, 2, "2^2+1"), (9, 3, "2^3+1"), (17, 4, "2^4+1"), (33, 5, "2^5+1")]
print(f"weights: S/M = {SM}, A/M = {AM}")
print("N      form    chains  min.len  minimisers  chain                    (M,S,A)       M-equiv")
for N, n, form in rows:
    cnt, ml, mins = run(N, n)
    seq, c = mins[0]
    print(f"{N:<6} {form:<7} {cnt:>6}  {ml:>7}  {len(mins):>10}  {' '.join(map(str, seq)):<24} {str(c):<13} {w(c):.2f}")
