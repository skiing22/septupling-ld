# septupling-ld

Code, data and logs for the paper

> S. Ramola, A. Pinapati, B. Das, *On the Minimality of Chain-Based Septupling using
> López-Dahab Coordinates over Binary Field* (submitted).

Section, table and equation numbers below refer to the submitted manuscript.

## Layout

| Folder | What it contains | Language |
|---|---|---|
| [`verification/`](verification/) | Exhaustive correctness checks, operation counts, chain enumeration, fusion analysis and block search | Python 3, standard library only |
| [`benchmark/`](benchmark/) | Timing program for Tables 3, 11 and 12 and the (2^n−1)P timings; repeats the correctness checks on K-163, B-233 and B-283 before timing | C++17 with NTL and gf2x |
| [`results/2026-11-07_i5-13500/`](results/2026-11-07_i5-13500/) | The single benchmark run that every measured number in the paper comes from | Raw logs |

## Quick start

```bash
# Correctness, counts and minimality (about 3-10 minutes, no dependencies)
cd verification && ./run_all.sh

# Timings (needs g++, NTL, gf2x, GMP; see benchmark/README.md)
cd benchmark && CORE=2 ./run_all.sh
```

## Key numbers (K-163)

| Quantity | Value | Paper |
|---|---|---|
| Chain of Eq. (7), `1→2→4→8→7` | 15M + 18S + 20A | Table 7 |
| Chain of Eq. (6), `1→2→3→6→7`, best blocks | 20M + 18S + 25A | Table 7 |
| Saving | 5M + 0S + 5A | Table 7 |
| Unique cheapest chain for 7P | `1→2→4→8→7` | Table 10 |
| Fusion saving | 1S + 1A, no M | Section 5.2 |
| Minimum M over the 54 block combinations | 15 | Section 5.2 |
| Measured cycles, Eq. (6) vs Eq. (7) | 7049 vs 5918 (16.0% fewer) | Table 12 |

## License

MIT, see [`LICENSE`](LICENSE).
