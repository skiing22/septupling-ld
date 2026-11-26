# Benchmark summary

Runs: 3  (run1.txt, run2.txt, run3.txt)

Correctness: total_failures=0, total_failures=0, total_failures=0

Build and protocol (run 1):

- build compiler=gcc-16.2.0
- build ntl=11.6.0
- build gf2x=yes
- build pclmul=yes avx2=yes
- protocol field_iters=1048576 block_iters=65536 chain_iters=16384 warmups=3 reps=15 tests=200
- build tsc_ghz=2.496
- total_failures=0

## Table 3: field-operation ratios (latency; median of runs, range in parentheses)

| | K-163 | B-233 | B-283 |
|---|---|---|---|
| S/M | 0.356 (0.355-0.356) | 0.330 (0.330-0.330) | 0.244 (0.243-0.244) |
| A/M | 0.029 (0.029-0.030) | 0.026 (0.026-0.026) | 0.016 (0.016-0.016) |
| I/M | 20.755 (20.751-20.763) | 25.690 (25.686-25.733) | 19.128 (19.078-19.390) |
| M, TSC cycles | 231.9 | 280.7 | 481.3 |

Throughput ratios (four independent streams):

- K-163: S/M = 0.354, A/M = 0.048, M = 231.7 cycles
- B-233: S/M = 0.327, A/M = 0.032, M = 281.2 cycles
- B-283: S/M = 0.242, A/M = 0.019, M = 481.1 cycles

## Table 11: block costs (cycles, median of runs), predicted M-equivalents at this field's measured ratios


**K-163**

| Block | (M,S,A) | Predicted M-eq | Cycles | Range | Cycles per M-eq |
|---|---|---|---|---|---|
| mdbl-2005-dl | (1, 3, 4) | 2.19 | 606 | 606-610 | 277 |
| fixed-a2-Z1 | (2, 3, 3) | 3.16 | 808 | 804-809 | 256 |
| fixed-a2 | (3, 5, 3) | 4.87 | 1338 | 1334-1369 | 275 |
| dbl-2005-dl | (3, 5, 4) | 4.90 | 1370 | 1365-1409 | 280 |
| dbl-2005-l | (4, 4, 5) | 5.57 | 1466 | 1461-1472 | 263 |
| madd-2005-dl | (8, 5, 9) | 10.04 | 2577 | 2576-2623 | 257 |
| add-2005-dl | (13, 4, 9) | 14.69 | 3707 | 3703-3746 | 252 |

**B-233**

| Block | (M,S,A) | Predicted M-eq | Cycles | Range | Cycles per M-eq |
|---|---|---|---|---|---|
| mdbl-2005-dl | (2, 3, 4) | 3.09 | 943 | 943-947 | 305 |
| fixed-a2-Z1 | (2, 3, 3) | 3.07 | 943 | 943-948 | 307 |
| fixed-a2 | (4, 5, 3) | 5.73 | 1796 | 1796-1807 | 314 |
| dbl-2005-dl | (4, 5, 4) | 5.75 | 1799 | 1797-1813 | 313 |
| dbl-2005-l | (4, 4, 5) | 5.45 | 1658 | 1658-1659 | 304 |
| madd-2005-dl | (8, 5, 9) | 9.88 | 2998 | 2994-3029 | 303 |
| add-2005-dl | (13, 4, 9) | 14.55 | 4345 | 4345-4372 | 299 |

**B-283**

| Block | (M,S,A) | Predicted M-eq | Cycles | Range | Cycles per M-eq |
|---|---|---|---|---|---|
| mdbl-2005-dl | (2, 3, 4) | 2.80 | 1405 | 1403-1406 | 503 |
| fixed-a2-Z1 | (2, 3, 3) | 2.78 | 1395 | 1394-1396 | 502 |
| fixed-a2 | (4, 5, 3) | 5.27 | 2698 | 2693-2705 | 512 |
| dbl-2005-dl | (4, 5, 4) | 5.28 | 2709 | 2705-2717 | 513 |
| dbl-2005-l | (4, 4, 5) | 5.06 | 2540 | 2540-2541 | 502 |
| madd-2005-dl | (8, 5, 9) | 9.37 | 4677 | 4674-4688 | 499 |
| add-2005-dl | (13, 4, 9) | 14.12 | 7030 | 7018-7036 | 498 |

## Table 12: cost of 7P (cycles per chain, median of runs)

| Curve | Eq.(6) best blocks | Eq.(7) ours | Measured saving | Range over runs | Predicted saving | Eq.(6) blocks of [1] |
|---|---|---|---|---|---|---|
| K-163 | 7049 | 5918 | 16.3% | 16.0-16.7% | 19.0% | 7954 |
| B-233 | 8629 | 7371 | 14.5% | 14.5-14.6% | 15.6% | 9227 |
| B-283 | 13342 | 11262 | 15.5% | 15.4-15.6% | 16.1% | 14196 |

Saving = (Eq.6 - Eq.7) / Eq.6, i.e. the reduction in cycles (use this for the abstract's [X]%).

## (2^n - 1)P on K-163 (cycles)

| n | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| cycles | 3007 | 4567 | 5958 | 7235 | 8627 | 9951 |
| increment | - | 1560 | 1391 | 1277 | 1392 | 1324 |

One fixed-a2 doubling on K-163: 1338 cycles.

## Core clock during runs (from freq_run*.csv)

- freq_run1.csv: 4.48-4.80 GHz (median 4.80), 455 samples
- freq_run2.csv: 4.68-4.80 GHz (median 4.80), 454 samples
- freq_run3.csv: 4.64-4.80 GHz (median 4.80), 455 samples
