#!/usr/bin/env bash
# Runs every verification script and reports pass/fail.
# Usage:  ./run_all.sh
set -u
cd "$(dirname "$0")"

PY=${PYTHON:-python3}
fail=0
line() { printf '=%.0s' {1..72}; echo; }

run() {
    line; echo "  $1"; line
    if $PY "$2"; then echo; else echo "*** $2 FAILED ***"; fail=1; fi
    echo
}

echo "Verification suite for: On the Minimality of Chain-Based Septupling"
echo "Python: $($PY --version 2>&1)"
echo

run "1. Correctness: Checks A-C, exhaustive (Section 4.4; slowest, ~5-10 min)" check_correctness.py
run "2. Operation counts: every block and both chains (Appendix A, Table 7, Eq. 8)"          count_blocks.py
run "3. Minimality: exhaustive chain enumeration (Section 5.1, Table 10)"                 enumerate_chains.py
run "4. Fusion analysis (Section 5.2)"                             fusion.py
run "5. Design-space search over published blocks (Section 5.2)"             search_chains.py

line
if [ $fail -eq 0 ]; then
    echo "  ALL SCRIPTS COMPLETED"
else
    echo "  SOME SCRIPTS FAILED - see above"
fi
line
exit $fail
