#!/usr/bin/env python3
"""
Exhaustive enumeration of addition-subtraction chains (Section 5.1, Table 10).

Confirms that 1 -> 2 -> 4 -> 8 -> 7 is the UNIQUE cost minimiser for 7P, and
that the reference chain is the unique minimiser for every 2^n +- 1 tested.
Also reproduces the exception at n = 2 in the minus case (Section 4.2).
"""
S_M, A_M = 0.356, 0.029     # Table 3, K-163

PLAIN_K163 = dict(MDBL=(1,3,4), DBL=(3,5,3), MIX=(8,5,9), ADD=(13,4,9), NEG=(0,0,1))

def vadd(*cs): return tuple(map(sum, zip(*cs)))
def meq(c): return c[0] + S_M*c[1] + A_M*c[2]

def step_cost(B, i, j, k, sign):
    if j == k:                                   # doubling
        return B['MDBL'] if i == 1 else B['DBL']
    base = B['MIX'] if (j == 0 or k == 0) else B['ADD']
    if sign < 0:                                 # subtraction: negate subtrahend
        base = vadd(base, B['NEG'] if (j == 0 or k == 0) else (1, 0, 1))
    return base

def enumerate_chains(B, target, max_len):
    out = []
    def rec(vals, cost, depth):
        if vals[-1] == target:
            out.append((tuple(vals), cost)); return
        if depth == max_len:
            return
        i, seen = len(vals), set()
        for j in range(i):
            for k in range(j + 1):
                for sign in (1, -1):
                    nxt = vals[j] + sign * vals[k]
                    if nxt <= 0 or nxt > 4 * target or nxt in seen:
                        continue
                    seen.add(nxt)
                    rec(vals + [nxt], vadd(cost, step_cost(B, i, j, k, sign)), depth + 1)
    rec([1], (0, 0, 0), 0)
    return out

def report(B, N, max_len):
    res = enumerate_chains(B, N, max_len)
    best = min(meq(c) for _, c in res)
    win = [(ch, c) for ch, c in res if abs(meq(c) - best) < 1e-12]
    minlen = min(len(ch) - 1 for ch, _ in res)
    print(f"  N={N:3d}  chains<=len{max_len}: {len(res):5d}  min length: {minlen}  "
          f"minimisers: {len(win)}")
    for ch, c in win:
        print(f"         {' -> '.join(map(str, ch))}   "
              f"{c[0]}M + {c[1]}S + {c[2]}A   = {meq(c):.3f} M")

def main():
    for label, B in (("LD coordinates, K-163 (Table 5)", PLAIN_K163),):
        print(label)
        print("  --- septupling, exhaustive to length 5 ---")
        report(B, 7, 5)
        print("  --- 2^n - 1 ---")
        for n in range(2, 6):
            report(B, 2**n - 1, n + 2)
        print("  --- 2^n + 1 ---")
        for n in range(1, 6):
            report(B, 2**n + 1, n + 2)
        print()

if __name__ == "__main__":
    main()
