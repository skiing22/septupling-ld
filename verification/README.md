# Verification suite

Pure Python 3 (3.8 or newer), standard library only. No packages, no network access.

```bash
chmod +x run_all.sh
./run_all.sh                  # runs every script below
./run_all.sh 2>&1 | tee verification-$(date +%F).log
```

Each script can also be run on its own, e.g. `python3 count_blocks.py`.
`expected_output.txt` is a complete reference log.

## Files

| File | What it does | Paper |
|---|---|---|
| `ecc_core.py` | GF(2^m), the affine group law, and every LD block, written from the printed formula in its primary source | Table 2, Appendix A |
| `dag.py` | Hash-consed expression DAG for mechanical operation counting | Section 5.2 |
| `check_correctness.py` | Exhaustive correctness checks A–C on small curves | Section 4.4 |
| `count_blocks.py` | Operation counts of every block, both 7P chains, closed form | Appendix A, Table 7, Eq. (8) |
| `enumerate_chains.py` | Exhaustive addition–subtraction chain search | Section 5.1, Table 10 |
| `fusion.py` | Common-subexpression elimination across block boundaries | Section 5.2 |
| `search_chains.py` | All 54 block combinations for `1→2→4→8→7` | Section 5.2 |

## What `check_correctness.py` tests

Test curves: y² + xy = x³ + a₂x² + a₆ with a₂ ∈ {0, 1}, a₆ ∈ {1, 3, 5}, over
GF(2⁵), GF(2⁷), GF(2⁹) and GF(2¹¹). Every affine point of every curve is used
(points of order 2 excepted), not a random sample. Projective inputs are given as
(μX : μ²Y : μ) with μ ∈ {1, 2, 3}.

- **A** – each block against the affine group law: `mdbl-2005-dl`, `dbl-2005-dl`,
  `dbl-2005-l`, the fixed-a₂ doubling (curves with a₂ = 1), `madd-2005-dl`,
  `add-2005-dl`, plus two comparators (López–Dahab mixed addition, tripling of
  Yasin et al.).
- **B** – the chain of Eq. (7) on every input with 7P, 8P, 9P ≠ O.
- **C** – the chain of Eq. (6) on every input with 2P, 3P, 5P, 6P, 7P ≠ O.

The script must end with `TOTAL FAILURES: 0`. It also prints how many inputs fall
outside each chain's conditions; these are the exceptional cases of Section 4.1.

## Cost weights

`M`-equivalents use the measured K-163 ratios of Table 3, S/M = 0.356 and
A/M = 0.029, set at the top of `count_blocks.py`, `enumerate_chains.py` and
`search_chains.py`. The saving of Eq. (7) over Eq. (6) is non-negative in every
operation class, so it does not depend on these values.

## Search space of `search_chains.py`

Each of the three doublings uses one of three formulas (`dbl-2005-dl`,
`dbl-2005-l`, fixed-a₂), each in its affine-input form at the first step, and the
final addition uses one of two mixed additions (`madd-2005-dl` or the López–Dahab
mixed addition, 9M + 4S): 3 × 3 × 3 × 2 = 54 programs.
