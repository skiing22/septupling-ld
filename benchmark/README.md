# Benchmark

Produces every measured number in the paper: Table 3 (field-operation ratios),
Table 11 (block cycles), Table 12 (cycles of 7P) and the (2^n−1)P timings of
Section 5.1. Before timing, it checks every LD block and both 7P chains against
the affine group law on K-163, B-233 and B-283 with 200 random points per curve
(NIST parameters; the program also verifies that G is on the curve and n·G = O),
and it records the machine.

The files here are byte-identical to the sources packed inside the results
archive of the run reported in the paper (`results/2026-11-07_i5-13500/`).

| File | Purpose |
|---|---|
| `ld_common.h` | Field and curve setup, affine group law, the LD blocks of Appendix A, the chains of Eqs. (6) and (7) |
| `bench.cpp` | Part 1 correctness, Part 2 field costs (Table 3), Part 3 block and chain costs (Tables 11, 12) |
| `run_all.sh` | Records the platform, builds, runs 3 pinned runs, summarises, packs one `.tgz` |
| `record_platform.sh` | CPU, OS, kernel, clocks, turbo, governor, libraries, virtualisation |
| `freq_log.sh` | Logs the pinned core's clock every 0.2 s during each run |
| `summarize.py` | Medians across runs, ratios, predicted vs measured savings |
| `tools/enumerate_chains.py` | Chain enumeration of Table 10 (same result as `verification/enumerate_chains.py`) |
| `tools/small_curve_orders.py` | Number of points of exact order 5 and 6 on the small test curves (Section 4.4) |

## Running

```bash
sudo apt install g++ libntl-dev libgf2x-dev libgmp-dev python3
CORE=2 QUICK=1 ./run_all.sh     # smoke test, about 1 minute; must print ALL CORRECTNESS CHECKS PASSED
CORE=2 ./run_all.sh             # full run; keep the results_*.tgz it prints
```

Without sudo: `conda install -c conda-forge ntl gf2x gmp`, then run inside the
activated environment; `run_all.sh` uses `$CONDA_PREFIX` automatically.

On hybrid Intel CPUs, choose a performance core for `CORE`
(`cat /sys/devices/cpu_core/cpus`).

## Protocol

`rdtsc` with `lfence` before and after; 3 warm-ups and 15 timed repetitions,
median; field operations 2^20 per repetition (inversion 2^14), blocks 2^16 on
their own output, chains 2^14 repeated evaluations; three independent process
runs on one pinned core. Build: `g++ -O2 -march=native -std=c++17`.

## Note on `tools/enumerate_chains.py`

`run_all.sh` calls it with the weights `0.80 0.094`. The weights only rank the
(M, S, A) tuples; the tuples and the unique minimiser do not change. The paper's
Table 10 reports M-equivalents at the measured ratios:

```bash
python3 tools/enumerate_chains.py 0.356 0.029
```
