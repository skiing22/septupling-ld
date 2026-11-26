// ld_common.h -- field setup, curves, affine group law and LD blocks.
// Every LD block follows the line-by-line listing of Appendix A of the paper.
#pragma once
#include <NTL/GF2X.h>
#include <NTL/GF2E.h>
#include <NTL/ZZ.h>
#include <string>
#include <vector>
#include <cstdint>
using namespace NTL;

// ---------------------------------------------------------------- curves
// Parameters copied from OpenSSL crypto/ec/ec_curve.c (NIST sect163k1,
// sect233r1, sect283r1); the program re-checks G on the curve and n*G = O.
struct CurveSpec {
    const char *name;
    int m;
    std::vector<long> poly;     // exponents of the reduction polynomial
    const char *a2, *a6, *gx, *gy, *n;   // hex strings
};
static const CurveSpec CURVES[3] = {
  {"K-163", 163, {163,7,6,3,0}, "1", "1",
   "2fe13c0537bbc11acaa07d793de4e6d5e5c94eee8",
   "289070fb05d38ff58321f2e800536d538ccdaa3d9",
   "4000000000000000000020108a2e0cc0d99f8a5ef"},
  {"B-233", 233, {233,74,0}, "1",
   "66647ede6c332c7f8c0923bb58213b333b20e9ce4281fe115f7d8f90ad",
   "fac9dfcbac8313bb2139f1bb755fef65bc391f8b36f8f8eb7371fd558b",
   "1006a08a41903350678e58528bebf8a0beff867a7ca36716f7e01f81052",
   "1000000000000000000000000000013e974e72f8a6922031d2603cfe0d7"},
  {"B-283", 283, {283,12,7,5,0}, "1",
   "27b680ac8b8596da5a4af8a19a0303fca97fd7645309fa2a581485af6263e313b79a2f5",
   "5f939258db7dd90e1934f8c70b0dfec2eed25b8557eac9c80e2e198f8cdbecd86b12053",
   "3676854fe24141cb98fe6d4b20d02b4516ff702350eddb0826779c813f0df45be8112f4",
   "3ffffffffffffffffffffffffffffffffffef90399660fc938a90165b042a7cefadb307"},
};

inline int hexval(char c){ return (c<='9')? c-'0' : (c|32)-'a'+10; }
inline GF2E hex_to_gf2e(const char *h){
    GF2X p; long L = (long)std::string(h).size();
    for (long i = 0; i < L; ++i){
        int v = hexval(h[L-1-i]);
        for (int b = 0; b < 4; ++b) if (v>>b & 1) SetCoeff(p, 4*i+b);
    }
    return conv<GF2E>(p);
}
inline ZZ hex_to_zz(const char *h){
    ZZ z(0); for (const char *c = h; *c; ++c) z = z*16 + hexval(*c); return z;
}

// Curve state for the field currently installed with GF2E::init.
struct Curve {
    std::string name; int m;
    GF2E a2, a6, sqrt_a6, gx, gy; ZZ n;
    bool a2_one, a6_one;        // multiplication by 1 is free (Table 4)
};
inline Curve install(const CurveSpec &s){
    GF2X f; for (long e : s.poly) SetCoeff(f, e);
    GF2E::init(f);
    Curve c; c.name = s.name; c.m = s.m;
    c.a2 = hex_to_gf2e(s.a2); c.a6 = hex_to_gf2e(s.a6);
    c.gx = hex_to_gf2e(s.gx); c.gy = hex_to_gf2e(s.gy); c.n = hex_to_zz(s.n);
    c.sqrt_a6 = c.a6; for (int i = 0; i < s.m-1; ++i) sqr(c.sqrt_a6, c.sqrt_a6);
    c.a2_one = IsOne(c.a2); c.a6_one = IsOne(c.a6);
    return c;
}
// Multiplication by a curve constant: free when the constant is 1 (Table 4).
inline void mulc(GF2E &r, const GF2E &x, const GF2E &k, bool one){
    if (one) r = x; else mul(r, x, k);
}

// ------------------------------------------------------- affine law (ground truth)
struct Aff { bool inf = true; GF2E x, y; };
inline bool on_curve(const Curve &c, const Aff &P){
    if (P.inf) return true;
    return sqr(P.y) + P.x*P.y == P.x*sqr(P.x) + c.a2*sqr(P.x) + c.a6;
}
inline Aff aneg(const Aff &P){ Aff R = P; if (!P.inf) R.y = P.x + P.y; return R; }
inline Aff adbl(const Curve &c, const Aff &P){
    Aff R; if (P.inf || IsZero(P.x)) return R;
    GF2E l = P.x + P.y/P.x; R.inf = false;
    R.x = sqr(l) + l + c.a2; R.y = sqr(P.x) + (l+1)*R.x; return R;
}
inline Aff aadd(const Curve &c, const Aff &P, const Aff &Q){
    if (P.inf) return Q; if (Q.inf) return P;
    if (P.x == Q.x) return (P.y == Q.y) ? adbl(c, P) : Aff();
    GF2E l = (P.y+Q.y)/(P.x+Q.x); Aff R; R.inf = false;
    R.x = sqr(l) + l + P.x + Q.x + c.a2; R.y = l*(P.x + R.x) + R.x + P.y; return R;
}
inline Aff amul(const Curve &c, const ZZ &k, const Aff &P){
    Aff R; for (long i = NumBits(k)-1; i >= 0; --i){ R = adbl(c, R); if (bit(k, i)) R = aadd(c, R, P); }
    return R;
}
inline bool aeq(const Aff &P, const Aff &Q){
    if (P.inf || Q.inf) return P.inf == Q.inf; return P.x == Q.x && P.y == Q.y;
}

// ------------------------------------------------------------ LD points
struct LD { GF2E X, Y, Z; };
inline Aff to_aff(const LD &R){
    Aff A; if (IsZero(R.Z)) return A;
    GF2E zi = inv(R.Z); A.inf = false; A.x = R.X*zi; A.y = R.Y*sqr(zi); return A;
}
inline LD from_aff(const Aff &P, const GF2E &mu){   // (mu x : mu^2 y : mu)
    LD R; R.X = mu*P.x; R.Y = sqr(mu)*P.y; R.Z = mu; return R;
}

// A.1 dbl-2005-dl, general input.  3M + 5S + 2D + 4A
inline void dbl_dl(const Curve &c, LD &o, const LD &p){
    GF2E z1s, x1s, x1q, bz, t;
    sqr(z1s, p.Z); sqr(x1s, p.X); GF2E Z3; mul(Z3, z1s, x1s);
    sqr(x1q, x1s); sqr(t, z1s); mulc(bz, t, c.a6, c.a6_one);
    GF2E X3; add(X3, x1q, bz);
    GF2E u, v; mulc(u, Z3, c.a2, c.a2_one); sqr(v, p.Y); add(u, u, v); add(u, u, bz);
    mul(u, X3, u); mul(v, bz, Z3); add(o.Y, v, u); o.X = X3; o.Z = Z3;
}
// A.2 mdbl-2005-dl, input Z1 = 1.  1M + 3S + 2D + 4A
inline void mdbl_dl(const Curve &c, LD &o, const GF2E &x1, const GF2E &y1){
    GF2E Z3, X3, u, v;
    sqr(Z3, x1); sqr(X3, Z3); add(X3, X3, c.a6);
    mulc(u, Z3, c.a2, c.a2_one); sqr(v, y1); add(u, u, v); add(u, u, c.a6);
    mul(u, X3, u); mulc(v, Z3, c.a6, c.a6_one); add(o.Y, v, u); o.X = X3; o.Z = Z3;
}
// A.3 dbl-2005-l (Lange).  4M + 4S + 1D + 5A
inline void dbl_l(const Curve &c, LD &o, const LD &p){
    GF2E S, U, T, Z3, X3, t;
    sqr(S, p.X); add(U, S, p.Y); mul(T, p.X, p.Z); sqr(Z3, T); mul(T, U, T);
    sqr(X3, U); add(X3, X3, T); mulc(t, Z3, c.a2, c.a2_one); add(X3, X3, t);
    GF2E Y3; add(t, Z3, T); mul(Y3, t, X3); sqr(t, S); mul(t, t, Z3); add(Y3, Y3, t);
    o.X = X3; o.Y = Y3; o.Z = Z3;
}
// A.4 fixed-a2 doubling (a2 = 1).  3M + 5S + 1D + 3A
inline void dbl_fixed(const Curve &c, LD &o, const LD &p){
    GF2E S, T, U, Z3, ST, X3, t, w;
    sqr(S, p.X); sqr(t, p.Z); mulc(T, t, c.sqrt_a6, c.a6_one);
    mul(U, p.X, p.Z); sqr(Z3, U); add(ST, S, T); sqr(X3, ST);
    mul(t, U, S); add(w, p.Y, T); mul(w, w, ST); add(t, t, w); sqr(o.Y, t);
    o.X = X3; o.Z = Z3;
}
// Fixed-a2 doubling at Z1 = 1 (Sec. 2.5, B-curves).  2M + 3S + 3A, sqrt(a6) precomputed
inline void mdbl_fixed(const Curve &c, LD &o, const GF2E &x1, const GF2E &y1){
    GF2E S, ST, t, w;
    sqr(S, x1); add(ST, S, c.sqrt_a6); sqr(o.X, ST);
    mul(t, x1, S); add(w, y1, c.sqrt_a6); mul(w, w, ST); add(t, t, w); sqr(o.Y, t);
    o.Z = S;
}
// A.5 madd-2005-dl: projective p + affine (x1, y1).  8M + 5S + 1D + 9A
inline void madd(const Curve &c, LD &o, const LD &p, const GF2E &x1, const GF2E &y1){
    GF2E U, S, T, Z3, V, C, t, w;
    sqr(t, p.Z); mul(U, t, y1); add(U, U, p.Y);
    mul(S, p.Z, x1); add(S, S, p.X);
    mul(T, p.Z, S); sqr(Z3, T); mul(V, Z3, x1); add(C, x1, y1);
    GF2E X3; sqr(X3, U); sqr(t, S); add(t, t, U); mulc(w, T, c.a2, c.a2_one); add(t, t, w);
    mul(t, T, t); add(X3, X3, t);
    GF2E Y3; add(t, V, X3); mul(w, T, U); add(w, w, Z3); mul(Y3, t, w);
    sqr(t, Z3); mul(t, t, C); add(o.Y, Y3, t); o.X = X3; o.Z = Z3;
}
// A.6 add-2005-dl (Higuchi-Takagi), both operands projective.  13M + 4S + 9A
inline void add_ht(LD &o, const LD &p, const LD &q){
    GF2E A1, A2, C, B1, B2, D, E1, E2, F, G, Z3, X3, t, w;
    mul(A1, p.X, q.Z); mul(A2, q.X, p.Z); add(C, A1, A2);
    sqr(B1, A1); sqr(B2, A2); add(D, B1, B2);
    sqr(t, q.Z); mul(E1, p.Y, t); sqr(t, p.Z); mul(E2, q.Y, t); add(F, E1, E2);
    mul(G, C, F); mul(Z3, p.Z, q.Z); mul(Z3, Z3, D);
    add(t, E2, B2); mul(t, A1, t); add(w, E1, B1); mul(w, A2, w); add(X3, t, w);
    mul(t, A1, G); mul(w, E1, D); add(t, t, w); mul(t, t, D);
    add(w, G, Z3); mul(w, w, X3); add(o.Y, t, w); o.X = X3; o.Z = Z3;
}

// ----------------------------------------------------------------- chains
// cdbl per Table 5: fixed-a2 doubling on K-163, dbl-2005-l on the B-curves.
inline void cdbl(const Curve &c, LD &o, const LD &p){ if (c.a6_one) dbl_fixed(c, o, p); else dbl_l(c, o, p); }

// Eq. (7), this paper: 7P = 2(2(2P)) - P.   cmdbl + 2 cdbl + neg + cmix
inline void chain_ours(const Curve &c, LD &R, const GF2E &x, const GF2E &y){
    LD T; mdbl_dl(c, R, x, y); cdbl(c, T, R); cdbl(c, R, T);
    GF2E ny; add(ny, x, y);                  // -P = (x, x + y), Lemma 1: 1A
    madd(c, T, R, x, ny); R = T;
}
// Eq. (6) with the cheapest blocks: 7P = 2(2P + P) + P.   cmdbl + cmix + cdbl + cmix
inline void chain_pub_best(const Curve &c, LD &R, const GF2E &x, const GF2E &y){
    LD T; mdbl_dl(c, R, x, y); madd(c, T, R, x, y); cdbl(c, R, T); madd(c, T, R, x, y); R = T;
}
// Eq. (6) with the block choice of [1]: dbl-2005-l at every doubling (also on the affine input).
inline void chain_pub_printed(const Curve &c, LD &R, const GF2E &x, const GF2E &y){
    LD P1{x, y, GF2E(1)}, T; dbl_l(c, R, P1); madd(c, T, R, x, y); dbl_l(c, R, T); madd(c, T, R, x, y); R = T;
}
// (2^n - 1)P = 2^n P - P, Theorem 15.
inline void chain_pow2m1(const Curve &c, int n, LD &R, const GF2E &x, const GF2E &y){
    LD T; mdbl_dl(c, R, x, y);
    for (int i = 1; i < n; ++i){ cdbl(c, T, R); R = T; }
    GF2E ny; add(ny, x, y); madd(c, T, R, x, ny); R = T;
}
