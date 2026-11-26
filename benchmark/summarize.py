#!/usr/bin/env python3
"""summarize.py -- turns run*.txt into the numbers for Tables 3, 11 and 12.
Usage: python3 summarize.py <results_dir>   (prints Markdown)"""
import sys, glob, re, statistics as st, csv, os

d = sys.argv[1]
runs = sorted(glob.glob(os.path.join(d, "run*.txt")))
pat = re.compile(r"RESULT (\w+) curve=(\S+) item=(\S+) mode=(\S+) median=([\d.]+)")
data = {}                                   # (kind,curve,item,mode) -> [median per run]
info = []
for f in runs:
    for line in open(f):
        m = pat.match(line)
        if m:
            k = m.group(1, 2, 3, 4); data.setdefault(k, []).append(float(m.group(5)))
        elif line.startswith("RESULT") and f == runs[0]:
            info.append(line.strip()[7:])
fails = [l for f in runs for l in open(f) if l.startswith("RESULT total_failures")]

def med(k):  v = data.get(k); return st.median(v) if v else float("nan")
def rng(k):  v = data.get(k, [float("nan")]); return min(v), max(v)
CURVES = ["K-163", "B-233", "B-283"]

def ratios(c, mode, run=None):
    def g(it):
        v = data.get(("field", c, it, mode)); return None if not v else (v if run is None else v[run])
    M, S, A, I = g("M"), g("S"), g("A"), g("I")
    return M, S, A, I

print(f"# Benchmark summary\n\nRuns: {len(runs)}  ({', '.join(os.path.basename(r) for r in runs)})\n")
print("Correctness: " + ", ".join(l.strip()[7:] for l in fails) + "\n")
print("Build and protocol (run 1):\n"); [print(f"- {i}") for i in info if not i.startswith(("check", "resets"))]

# ---------------- Table 3
print("\n## Table 3: field-operation ratios (latency; median of runs, range in parentheses)\n")
print("| | " + " | ".join(CURVES) + " |\n|---|" + "---|" * len(CURVES))
rat = {}
for name, num in [("S/M", "S"), ("A/M", "A"), ("I/M", "I")]:
    row = []
    for c in CURVES:
        per = []
        for r in range(len(runs)):
            try: per.append(data[("field", c, num, "latency")][r] / data[("field", c, "M", "latency")][r])
            except (KeyError, IndexError): pass
        if per:
            rat[(c, name)] = st.median(per)
            row.append(f"{st.median(per):.3f} ({min(per):.3f}-{max(per):.3f})")
        else: row.append("n/a")
    print(f"| {name} | " + " | ".join(row) + " |")
print("| M, TSC cycles | " + " | ".join(f"{med(('field', c, 'M', 'latency')):.1f}" for c in CURVES) + " |")
print("\nThroughput ratios (four independent streams):\n")
for c in CURVES:
    M, S, A = med(("field", c, "M", "throughput")), med(("field", c, "S", "throughput")), med(("field", c, "A", "throughput"))
    print(f"- {c}: S/M = {S/M:.3f}, A/M = {A/M:.3f}, M = {M:.1f} cycles")

# ---------------- cost tuples (Table 5; on B-curves a chargeable D is counted as 1M)
K = {"mdbl-2005-dl": (1, 3, 4), "fixed-a2": (3, 5, 3), "dbl-2005-dl": (3, 5, 4), "dbl-2005-l": (4, 4, 5),
     "madd-2005-dl": (8, 5, 9), "add-2005-dl": (13, 4, 9), "fixed-a2-Z1": (2, 3, 3)}
B = {"mdbl-2005-dl": (2, 3, 4), "fixed-a2": (4, 5, 3), "dbl-2005-dl": (4, 5, 4), "dbl-2005-l": (4, 4, 5),
     "madd-2005-dl": (8, 5, 9), "add-2005-dl": (13, 4, 9), "fixed-a2-Z1": (2, 3, 3)}
CH = {"K-163": {"Eq7-ours": (15, 18, 20), "Eq6-best": (20, 18, 25), "Eq6-blocks-of-1": (24, 18, 28)},
      "B-233": {"Eq7-ours": (18, 16, 24), "Eq6-best": (22, 17, 27), "Eq6-blocks-of-1": (24, 18, 28)}}
CH["B-283"] = CH["B-233"]
def meq(c, t): return t[0] + t[1] * rat[(c, "S/M")] + t[2] * rat[(c, "A/M")]

# ---------------- Table 11
print("\n## Table 11: block costs (cycles, median of runs), predicted M-equivalents at this field's measured ratios\n")
for c in CURVES:
    tup = K if c == "K-163" else B
    print(f"\n**{c}**\n\n| Block | (M,S,A) | Predicted M-eq | Cycles | Range | Cycles per M-eq |\n|---|---|---|---|---|---|")
    for b in ["mdbl-2005-dl", "fixed-a2-Z1", "fixed-a2", "dbl-2005-dl", "dbl-2005-l", "madd-2005-dl", "add-2005-dl"]:
        k = ("block", c, b, "latency"); cy = med(k); lo, hi = rng(k); p = meq(c, tup[b])
        print(f"| {b} | {tup[b]} | {p:.2f} | {cy:.0f} | {lo:.0f}-{hi:.0f} | {cy/p:.0f} |")

# ---------------- Table 12
print("\n## Table 12: cost of 7P (cycles per chain, median of runs)\n")
print("| Curve | Eq.(6) best blocks | Eq.(7) ours | Measured saving | Range over runs | Predicted saving | Eq.(6) blocks of [1] |")
print("|---|---|---|---|---|---|---|")
for c in CURVES:
    pub, our, prn = (data.get(("chain", c, n, "repeated"), []) for n in ("Eq6-best", "Eq7-ours", "Eq6-blocks-of-1"))
    if not pub or not our: continue
    sav = [(p - o) / p * 100 for p, o in zip(pub, our)]
    pp, po = meq(c, CH[c]["Eq6-best"]), meq(c, CH[c]["Eq7-ours"])
    print(f"| {c} | {st.median(pub):.0f} | {st.median(our):.0f} | {st.median(sav):.1f}% | {min(sav):.1f}-{max(sav):.1f}% | {(pp-po)/pp*100:.1f}% | {st.median(prn):.0f} |")
print("\nSaving = (Eq.6 - Eq.7) / Eq.6, i.e. the reduction in cycles (use this for the abstract's [X]%).")

# ---------------- (2^n - 1)P
ns = [med(("chain", "K-163", f"pow2m1-n{n}", "repeated")) for n in range(1, 7)]
print("\n## (2^n - 1)P on K-163 (cycles)\n")
print("| n | " + " | ".join(str(n) for n in range(1, 7)) + " |\n|---|" + "---|" * 6)
print("| cycles | " + " | ".join(f"{x:.0f}" for x in ns) + " |")
print("| increment | - | " + " | ".join(f"{ns[i]-ns[i-1]:.0f}" for i in range(1, 6)) + " |")
print(f"\nOne fixed-a2 doubling on K-163: {med(('block', 'K-163', 'fixed-a2', 'latency')):.0f} cycles.")

# ---------------- clock log
print("\n## Core clock during runs (from freq_run*.csv)\n")
for f in sorted(glob.glob(os.path.join(d, "freq_run*.csv"))):
    v = []
    for row in csv.DictReader(open(f)):
        try: v.append(float(row["core_kHz"]) / 1e6)
        except (ValueError, KeyError): pass
    if v: print(f"- {os.path.basename(f)}: {min(v):.2f}-{max(v):.2f} GHz (median {st.median(v):.2f}), {len(v)} samples")
