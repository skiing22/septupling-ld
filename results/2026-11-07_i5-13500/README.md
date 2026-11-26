# Benchmark run of 7 November 2026 (Intel Core i5-13500)

Every measured number in the paper comes from this run.

| File | Contents |
|---|---|
| `platform.txt` | CPU, OS, kernel, governor, turbo, libraries (output of `record_platform.sh`) |
| `build.log` | Exact compile command and linked libraries |
| `run1.txt`, `run2.txt`, `run3.txt` | Raw output of the three pinned runs; each ends with `ALL CORRECTNESS CHECKS PASSED` |
| `freq_run1.csv` … `freq_run3.csv` | Core clock of the pinned CPU every 0.2 s during each run |
| `summary.md` | Output of `summarize.py`: medians and ranges used in Tables 3, 11 and 12 |
| `table10_enumeration.txt` | Chain enumeration (weights 0.80 / 0.094; see note below) |
| `small_curve_orders.txt` | Points of exact order 5 and 6 on the small test curves |
| `raw_archive.tgz` | The untouched archive produced by `run_all.sh`, including the exact sources |

Platform in brief: Intel Core i5-13500, logical CPU 2 (performance core) pinned,
Ubuntu 22.04.5 LTS, kernel 6.8, gcc 16.2.0 (conda-forge), NTL 11.6.0, gf2x 1.3.0,
GMP 6.3.0, TSC 2.496 GHz, turbo on, core clock 4.48–4.80 GHz.

## Notes on reading the files

- **Measured saving in Table 12.** The paper computes the saving from the median
  cycle counts, e.g. (7049 − 5918) / 7049 = 16.0% on K-163. `summary.md` instead
  reports the median of the three per-run savings (16.3%, range 16.0–16.7%). Both
  come from the same data; the paper uses the first.
- **`table10_enumeration.txt`** was produced with the weights 0.80 / 0.094 passed
  by `run_all.sh`. The (M, S, A) tuples and the unique minimisers are the ones in
  Table 10; only the M-equivalent column differs. Table 10 uses the measured
  ratios 0.356 / 0.029 (`python3 benchmark/tools/enumerate_chains.py 0.356 0.029`).
