// bench.cpp -- correctness checks and timings for the septupling paper.
//   Part 0  platform and build information
//   Part 1  correctness of every block and chain against the affine group law
//   Part 2  field-operation costs (Table 3): latency and throughput
//   Part 3  block costs (Table 11) and chain costs (Table 12, (2^n-1)P)
// Usage:  ./bench [field_iters] [block_iters] [chain_iters] [reps] [tests]
// Lines that start with "RESULT" are machine-readable (see summarize.py).
#include "ld_common.h"
#include <NTL/version.h>
#include <algorithm>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <functional>

static inline uint64_t tsc(){
    unsigned lo, hi;
    __asm__ __volatile__("lfence\n\trdtsc\n\tlfence" : "=a"(lo), "=d"(hi) :: "memory");
    return ((uint64_t)hi << 32) | lo;
}
static const int WARM = 3;
static int REPS = 15;

struct Stat { double med, lo, hi; };
// Runs body() WARM + REPS times; each run performs `ops` operations.
static Stat timed(long ops, const std::function<void()> &body){
    std::vector<double> v;
    for (int r = 0; r < WARM + REPS; ++r){
        uint64_t t0 = tsc(); body(); uint64_t t1 = tsc();
        if (r >= WARM) v.push_back(double(t1 - t0) / double(ops));
    }
    std::sort(v.begin(), v.end());
    return {v[v.size()/2], v.front(), v.back()};
}
static void result(const char *kind, const std::string &curve, const char *what, const char *mode, const Stat &s){
    printf("RESULT %s curve=%s item=%s mode=%s median=%.2f min=%.2f max=%.2f\n",
           kind, curve.c_str(), what, mode, s.med, s.lo, s.hi);
}

static volatile long SINK = 0;
static void consume(const GF2E &x){ SINK += deg(rep(x)); }

// ------------------------------------------------------------- Part 1
static long FAILS = 0;
static void expect(bool ok, const std::string &curve, const char *what){
    if (!ok){ ++FAILS; printf("FAIL %s %s\n", curve.c_str(), what); }
}
static GF2E rand_nonzero(){ GF2E m; do random(m); while (IsZero(m)); return m; }

static void correctness(const Curve &c, int tests){
    Aff G; G.inf = false; G.x = c.gx; G.y = c.gy;
    expect(on_curve(c, G), c.name, "generator on curve");
    expect(amul(c, c.n, G).inf, c.name, "n*G = O");
    long checks = 0;
    for (int t = 0; t < tests; ++t){
        ZZ k = RandomBnd(c.n - 1) + 1, k2 = RandomBnd(c.n - 1) + 1;
        Aff P = amul(c, k, G), Q = amul(c, k2, G);
        Aff P2 = adbl(c, P), PQ = aadd(c, P, Q);
        LD p = from_aff(P, rand_nonzero()), q = from_aff(Q, rand_nonzero()), o;
        dbl_dl(c, o, p);    expect(aeq(to_aff(o), P2), c.name, "dbl-2005-dl");        ++checks;
        dbl_l(c, o, p);     expect(aeq(to_aff(o), P2), c.name, "dbl-2005-l");         ++checks;
        dbl_fixed(c, o, p); expect(aeq(to_aff(o), P2), c.name, "fixed-a2 doubling");  ++checks;
        mdbl_dl(c, o, P.x, P.y);    expect(aeq(to_aff(o), P2), c.name, "mdbl-2005-dl");          ++checks;
        mdbl_fixed(c, o, P.x, P.y); expect(aeq(to_aff(o), P2), c.name, "fixed-a2 at Z1=1");      ++checks;
        madd(c, o, q, P.x, P.y);    expect(aeq(to_aff(o), PQ), c.name, "madd-2005-dl");          ++checks;
        add_ht(o, p, q);            expect(aeq(to_aff(o), PQ), c.name, "add-2005-dl");           ++checks;
        LD np{p.X, p.X*p.Z + p.Y, p.Z};
        expect(aeq(to_aff(np), aneg(P)), c.name, "negation (Lemma 1)");                          ++checks;
        Aff P7 = amul(c, ZZ(7), P);
        chain_ours(c, o, P.x, P.y);        expect(aeq(to_aff(o), P7), c.name, "chain Eq.(7)");                 ++checks;
        chain_pub_best(c, o, P.x, P.y);    expect(aeq(to_aff(o), P7), c.name, "chain Eq.(6), best blocks");    ++checks;
        chain_pub_printed(c, o, P.x, P.y); expect(aeq(to_aff(o), P7), c.name, "chain Eq.(6), blocks of [1]"); ++checks;
        for (int n = 1; n <= 6; ++n){
            chain_pow2m1(c, n, o, P.x, P.y);
            expect(aeq(to_aff(o), amul(c, ZZ((1L << n) - 1), P)), c.name, "(2^n-1)P chain"); ++checks;
        }
    }
    printf("RESULT check curve=%s checks=%ld failures_so_far=%ld\n", c.name.c_str(), checks, FAILS);
}

// ------------------------------------------------------------- Part 2
static void field_costs(const Curve &c, long iters){
    GF2E a = rand_nonzero(), b = rand_nonzero();
    const long I_iters = std::max(1L, iters / 64);   // inversion is slow
    Stat M = timed(iters, [&]{ GF2E x = a; for (long i = 0; i < iters; ++i) mul(x, x, b); consume(x); });
    Stat S = timed(iters, [&]{ GF2E x = a; for (long i = 0; i < iters; ++i) sqr(x, x); consume(x); });
    Stat A = timed(iters, [&]{ GF2E x = a; for (long i = 0; i < iters; ++i) add(x, x, b); consume(x); });
    Stat I = timed(I_iters, [&]{ GF2E x = a, t; for (long i = 0; i < I_iters; ++i){ add(t, x, b); if (IsZero(t)) t = 1; inv(x, t); } consume(x); });
    result("field", c.name, "M", "latency", M); result("field", c.name, "S", "latency", S);
    result("field", c.name, "A", "latency", A); result("field", c.name, "I", "latency", I);
    // Throughput: four independent streams, cost per operation.
    Stat Mt = timed(4*iters, [&]{ GF2E x0=a,x1=b,x2=a+b,x3=a*b; for (long i=0;i<iters;++i){ mul(x0,x0,b); mul(x1,x1,a); mul(x2,x2,b); mul(x3,x3,a);} consume(x0+x1+x2+x3); });
    Stat St = timed(4*iters, [&]{ GF2E x0=a,x1=b,x2=a+b,x3=a*b; for (long i=0;i<iters;++i){ sqr(x0,x0); sqr(x1,x1); sqr(x2,x2); sqr(x3,x3);} consume(x0+x1+x2+x3); });
    Stat At = timed(4*iters, [&]{ GF2E x0=a,x1=b,x2=a+b,x3=a*b; for (long i=0;i<iters;++i){ add(x0,x0,b); add(x1,x1,a); add(x2,x2,b); add(x3,x3,a);} consume(x0+x1+x2+x3); });
    result("field", c.name, "M", "throughput", Mt); result("field", c.name, "S", "throughput", St);
    result("field", c.name, "A", "throughput", At);
}

// ------------------------------------------------------------- Part 3
// Blocks are timed on their own output (latency).  An affine-input block takes
// the X, Y of its last output as the next input; the arithmetic is the same
// whether or not that pair is on the curve.  A zero Z resets the state.
static void block_costs(const Curve &c, long iters){
    Aff G; G.inf = false; G.x = c.gx; G.y = c.gy;
    Aff P = adbl(c, G), Q = amul(c, ZZ(5), G);
    LD start = from_aff(P, rand_nonzero()), q = from_aff(Q, rand_nonzero());
    long resets = 0;
    auto guard = [&](LD &R){ if (IsZero(R.Z)){ R = q; ++resets; } };   // R = (5+2k)G or similar; never +-P for small k
    auto run_proj = [&](const char *name, void (*f)(const Curve&, LD&, const LD&)){
        Stat s = timed(iters, [&]{ LD R = start, T; for (long i = 0; i < iters; ++i){ f(c, T, R); R = T; guard(R);} consume(R.X); });
        result("block", c.name, name, "latency", s);
    };
    auto run_aff = [&](const char *name, void (*f)(const Curve&, LD&, const GF2E&, const GF2E&)){
        Stat s = timed(iters, [&]{ GF2E x = P.x, y = P.y; LD T; for (long i = 0; i < iters; ++i){ f(c, T, x, y); x = T.X; y = T.Y; if (IsZero(x)){ x = P.x; y = P.y; ++resets; } } consume(x); });
        result("block", c.name, name, "latency", s);
    };
    run_aff ("mdbl-2005-dl", mdbl_dl);
    run_aff ("fixed-a2-Z1", mdbl_fixed);
    run_proj("fixed-a2", dbl_fixed);
    run_proj("dbl-2005-dl", dbl_dl);
    run_proj("dbl-2005-l", dbl_l);
    { Stat s = timed(iters, [&]{ LD R = q, T; for (long i = 0; i < iters; ++i){ madd(c, T, R, P.x, P.y); R = T; guard(R);} consume(R.X); });
      result("block", c.name, "madd-2005-dl", "latency", s); }
    { Stat s = timed(iters, [&]{ LD R = start, T; for (long i = 0; i < iters; ++i){ add_ht(T, R, q); R = T; guard(R);} consume(R.X); });
      result("block", c.name, "add-2005-dl", "latency", s); }
    printf("RESULT resets curve=%s count=%ld\n", c.name.c_str(), resets);
}
static void chain_costs(const Curve &c, long iters){
    Aff G; G.inf = false; G.x = c.gx; G.y = c.gy;
    Aff P = amul(c, ZZ(3), G);
    auto run = [&](const char *name, const std::function<void(LD&)> &ch){
        Stat s = timed(iters, [&]{ LD R; for (long i = 0; i < iters; ++i){ ch(R); consume(R.Z); } });
        result("chain", c.name, name, "repeated", s);
    };
    run("Eq7-ours",        [&](LD &R){ chain_ours(c, R, P.x, P.y); });
    run("Eq6-best",        [&](LD &R){ chain_pub_best(c, R, P.x, P.y); });
    run("Eq6-blocks-of-1", [&](LD &R){ chain_pub_printed(c, R, P.x, P.y); });
    if (c.a6_one) for (int n = 1; n <= 6; ++n){
        char nm[32]; snprintf(nm, sizeof nm, "pow2m1-n%d", n);
        run(nm, [&](LD &R){ chain_pow2m1(c, n, R, P.x, P.y); });
    }
}

int main(int argc, char **argv){
    long field_iters = argc > 1 ? atol(argv[1]) : (1L << 20);
    long block_iters = argc > 2 ? atol(argv[2]) : (1L << 16);
    long chain_iters = argc > 3 ? atol(argv[3]) : (1L << 14);
    REPS             = argc > 4 ? atoi(argv[4]) : 15;
    int  tests       = argc > 5 ? atoi(argv[5]) : 200;
    SetSeed(ZZ(20261107));

    printf("== Part 0: build ==\n");
#if defined(__GNUC__)
    printf("RESULT build compiler=gcc-%d.%d.%d\n", __GNUC__, __GNUC_MINOR__, __GNUC_PATCHLEVEL__);
#endif
    printf("RESULT build ntl=%s\n", NTL_VERSION);
#ifdef NTL_GF2X_LIB
    printf("RESULT build gf2x=yes\n");
#else
    printf("RESULT build gf2x=no\n");
#endif
    printf("RESULT build pclmul=%s avx2=%s\n", __builtin_cpu_supports("pclmul") ? "yes" : "no",
           __builtin_cpu_supports("avx2") ? "yes" : "no");
    printf("RESULT protocol field_iters=%ld block_iters=%ld chain_iters=%ld warmups=%d reps=%d tests=%d\n",
           field_iters, block_iters, chain_iters, WARM, REPS, tests);
    { auto w0 = std::chrono::steady_clock::now(); uint64_t t0 = tsc();
      while (std::chrono::steady_clock::now() - w0 < std::chrono::milliseconds(500)) {}
      uint64_t t1 = tsc(); double s = std::chrono::duration<double>(std::chrono::steady_clock::now() - w0).count();
      printf("RESULT build tsc_ghz=%.3f\n", (t1 - t0) / s / 1e9); }

    for (const CurveSpec &spec : CURVES){
        Curve c = install(spec);
        printf("\n== %s ==\n", c.name.c_str());
        correctness(c, tests);
        field_costs(c, field_iters);
        block_costs(c, block_iters);
        chain_costs(c, chain_iters);
        fflush(stdout);
    }
    printf("\nRESULT total_failures=%ld\n", FAILS);
    printf(FAILS ? "CORRECTNESS FAILED\n" : "ALL CORRECTNESS CHECKS PASSED\n");
    return FAILS ? 1 : 0;
}
