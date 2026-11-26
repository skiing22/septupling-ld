#!/usr/bin/env bash
# run_all.sh -- builds, records the platform, runs the benchmark RUNS times on
# one pinned core, summarises, and packs everything into one .tgz.
# Usage: ./run_all.sh            (full run, about 15-30 minutes)
#        QUICK=1 ./run_all.sh    (smoke test, about 1 minute)
set -euo pipefail
cd "$(dirname "$0")"
CORE="${CORE:-2}"; RUNS="${RUNS:-3}"
STAMP="$(hostname)_$(date +%Y%m%d_%H%M%S)"
if ! taskset -c "$CORE" true 2>/dev/null; then
  echo "ERROR: cannot pin to CPU $CORE on this machine. Choose a P-core, e.g. CORE=0 ./run_all.sh"; exit 1; fi
OUT="results/$STAMP"; mkdir -p "$OUT"
if [ "${QUICK:-0}" = 1 ]; then ARGS="4096 256 64 3 20"; else ARGS="1048576 65536 16384 15 200"; fi

echo "[1/5] recording platform -> $OUT/platform.txt"
CORE="$CORE" ./record_platform.sh > "$OUT/platform.txt" 2>&1

echo "[2/5] building"
INC=""; LIB=""
if [ -n "${CONDA_PREFIX:-}" ] && [ -f "$CONDA_PREFIX/include/NTL/GF2E.h" ]; then
  INC="-I$CONDA_PREFIX/include"; LIB="-L$CONDA_PREFIX/lib -Wl,-rpath,$CONDA_PREFIX/lib"; fi
CMD="g++ -O2 -march=native -std=c++17 $INC bench.cpp -o bench $LIB -lntl -lgf2x -lgmp -pthread"
echo "$CMD" > "$OUT/build.log"; $CMD >> "$OUT/build.log" 2>&1
ldd ./bench >> "$OUT/build.log" 2>&1 || true

echo "[3/5] running $RUNS independent runs on CPU $CORE (args: $ARGS)"
for r in $(seq 1 "$RUNS"); do
  ./freq_log.sh "$CORE" "$OUT/freq_run$r.csv" & FL=$!
  taskset -c "$CORE" ./bench $ARGS > "$OUT/run$r.txt" 2>&1 || true
  kill "$FL" 2>/dev/null || true
  tail -1 "$OUT/run$r.txt"
done

echo "[4/5] chain enumeration (Table 10) and small-curve order counts (Sec. 4.4)"
python3 tools/enumerate_chains.py 0.80 0.094 > "$OUT/table10_enumeration.txt"
python3 tools/small_curve_orders.py > "$OUT/small_curve_orders.txt"
echo "[4/5] summarising -> $OUT/summary.md"
python3 summarize.py "$OUT" > "$OUT/summary.md"

echo "[5/5] packing"
mkdir -p "$OUT/source" && cp -r bench.cpp ld_common.h run_all.sh record_platform.sh freq_log.sh summarize.py README.md tools "$OUT/source/"
tar czf "results_$STAMP.tgz" -C results "$STAMP"
echo "DONE. Keep this file: $(pwd)/results_$STAMP.tgz"
