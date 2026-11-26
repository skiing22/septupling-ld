"""
Core arithmetic for the septupling paper: binary fields, the affine group law,
and every point-arithmetic block used in the manuscript.

Pure Python 3, standard library only.  Nothing here is optimised; it exists to
be obviously correct, so that it can be used as ground truth for the counts and
chains printed in the paper.
"""

# ---------------------------------------------------------------- field ----
class GF:
    """GF(2^m) with elements as ints, bit i = coefficient of x^i."""
    def __init__(self, m, poly):
        self.m, self.poly = m, poly          # poly includes the x^m bit

    def add(self, a, b):
        return a ^ b

    def mul(self, a, b):
        r = 0
        while b:
            if b & 1:
                r ^= a
            b >>= 1
            a <<= 1
            if a >> self.m & 1:
                a ^= self.poly
        return r

    def sqr(self, a):
        return self.mul(a, a)

    def inv(self, a):
        assert a != 0, "inversion of zero"
        u, v, g1, g2 = a, self.poly, 1, 0
        while u != 1:
            if u == 0:
                raise ZeroDivisionError
            j = u.bit_length() - v.bit_length()
            if j < 0:
                u, v, g1, g2, j = v, u, g2, g1, -j
            u ^= v << j
            g1 ^= g2 << j
        return g1 if g1.bit_length() <= self.m else self._reduce(g1)

    def _reduce(self, a):
        while a.bit_length() > self.m:
            a ^= self.poly << (a.bit_length() - self.poly.bit_length())
        return a

    def div(self, a, b):
        return self.mul(a, self.inv(b))

    def sqrt(self, a):
        """In GF(2^m) squaring is a bijection; sqrt(a) = a^(2^(m-1))."""
        r = a
        for _ in range(self.m - 1):
            r = self.sqr(r)
        return r


# Irreducible polynomials for the small test fields.
FIELDS = {
    5:  0b100101,            # x^5 + x^2 + 1
    7:  0b10000011,          # x^7 + x + 1
    9:  0b1000010001,        # x^9 + x^4 + 1
    11: 0b100000000101,      # x^11 + x^2 + 1
}

# ------------------------------------------------------ affine group law ----
O = None          # the point at infinity

def on_curve(F, a2, a6, P):
    """y^2 + xy = x^3 + a2 x^2 + a6"""
    if P is O:
        return True
    x, y = P
    lhs = F.add(F.sqr(y), F.mul(x, y))
    rhs = F.add(F.add(F.mul(F.sqr(x), x), F.mul(a2, F.sqr(x))), a6)
    return lhs == rhs

def points(F, a2, a6):
    return [(x, y) for x in range(1 << F.m) for y in range(1 << F.m)
            if on_curve(F, a2, a6, (x, y))]

def neg(F, P):
    return O if P is O else (P[0], F.add(P[0], P[1]))

def aadd(F, a2, a6, P, Q):
    """Textbook affine addition; ground truth for every test."""
    if P is O:
        return Q
    if Q is O:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if P != Q:
            return O                      # Q = -P
        if x1 == 0:
            return O
        lam = F.add(x1, F.div(y1, x1))
        x3 = F.add(F.add(F.sqr(lam), lam), a2)
        y3 = F.add(F.sqr(x1), F.mul(F.add(lam, 1), x3))
        return (x3, y3)
    lam = F.div(F.add(y1, y2), F.add(x1, x2))
    x3 = F.add(F.add(F.add(F.add(F.sqr(lam), lam), x1), x2), a2)
    y3 = F.add(F.add(F.mul(lam, F.add(x1, x3)), x3), y1)
    return (x3, y3)

def amul(F, a2, a6, k, P):
    R = O
    for _ in range(k):
        R = aadd(F, a2, a6, R, P)
    return R

# ------------------------------------------- Lopez-Dahab coordinates -------
# (X : Y : Z)  represents  (X/Z, Y/Z^2)

def ld_to_affine(F, T):
    X, Y, Z = T
    if Z == 0:
        return O
    zi = F.inv(Z)
    return (F.mul(X, zi), F.mul(Y, F.sqr(zi)))

def ld_lift(F, P, mu):
    """A non-trivial LD representative of the affine point P."""
    return (F.mul(mu, P[0]), F.mul(F.sqr(mu), P[1]), mu)

def mdbl_2005_dl(F, a2, a6, X1, Y1):
    """Lopez-Dahab doubling specialised to Z1 = 1.  [LD98, Sec. 5.2]"""
    Z2 = F.sqr(X1)
    T  = a6
    X2 = F.add(F.sqr(F.sqr(X1)), T)
    Y2 = F.add(F.mul(T, Z2),
               F.mul(X2, F.add(F.add(F.mul(a2, Z2), F.sqr(Y1)), T)))
    return (X2, Y2, Z2)

def dbl_2005_dl(F, a2, a6, X1, Y1, Z1):
    """Lopez-Dahab projective doubling.  [LD98, Sec. 5.2]"""
    Z3 = F.mul(F.sqr(Z1), F.sqr(X1))
    T  = F.mul(a6, F.sqr(F.sqr(Z1)))
    X3 = F.add(F.sqr(F.sqr(X1)), T)
    Y3 = F.add(F.mul(T, Z3),
               F.mul(X3, F.add(F.add(F.mul(a2, Z3), F.sqr(Y1)), T)))
    return (X3, Y3, Z3)

def dbl_2005_l(F, a2, X1, Y1, Z1):
    """Lange's doubling.  [Lange06, Eq. (7)]"""
    S  = F.sqr(X1)
    U  = F.add(S, Y1)
    T  = F.mul(X1, Z1)
    Z3 = F.sqr(T)
    R  = F.mul(U, T)
    X3 = F.add(F.add(F.sqr(U), R), F.mul(a2, Z3))
    Y3 = F.add(F.mul(F.add(Z3, R), X3), F.mul(F.sqr(S), Z3))
    return (X3, Y3, Z3)

def dbl_fixed_a2(F, sqrt_a6, X1, Y1, Z1):
    """Fixed-a2 doubling, a2 = 1, sqrt(a6) precomputed.
       [Lange06, Eq. (4)], attributed there to Lopez; EFD dbl-2005-dl-a2-1.
       This is the general doubling c_dbl on K-163."""
    S  = F.sqr(X1)
    T  = F.mul(sqrt_a6, F.sqr(Z1))
    U  = F.mul(X1, Z1)
    Z3 = F.sqr(U)
    ST = F.add(S, T)                       # formed once, reused in Y3
    X3 = F.sqr(ST)
    Y3 = F.sqr(F.add(F.mul(U, S), F.mul(F.add(Y1, T), ST)))
    return (X3, Y3, Z3)

def madd_2005_dl(F, a2, x1, y1, X2, Y2, Z2):
    """Mixed addition: affine (x1,y1) + projective (X2:Y2:Z2).
       [Al-Daoud et al. 2002, Thm. 1]"""
    U  = F.add(F.mul(F.sqr(Z2), y1), Y2)
    S  = F.add(F.mul(Z2, x1), X2)
    T  = F.mul(Z2, S)
    Z3 = F.sqr(T)
    V  = F.mul(Z3, x1)
    C  = F.add(x1, y1)
    X3 = F.add(F.sqr(U), F.mul(T, F.add(F.add(U, F.sqr(S)), F.mul(a2, T))))
    Y3 = F.add(F.mul(F.add(V, X3), F.add(F.mul(T, U), Z3)), F.mul(F.sqr(Z3), C))
    return (X3, Y3, Z3)

def madd_lopezdahab(F, a2, X0, Y0, Z0, x1, y1):
    """Lopez-Dahab's own Z=1 addition, 9M+4S.  [LD98, Sec. 5.2]  Not used; a comparator."""
    Z0s = F.sqr(Z0)
    A = F.add(F.mul(y1, Z0s), Y0)
    B = F.add(F.mul(x1, Z0), X0)
    C = F.mul(Z0, B)
    D = F.mul(F.sqr(B), F.add(C, F.mul(a2, Z0s)))
    Z2 = F.sqr(C)
    E = F.mul(A, C)
    X2 = F.add(F.add(F.sqr(A), D), E)
    Fv = F.add(X2, F.mul(x1, Z2))
    G  = F.add(X2, F.mul(y1, Z2))
    Y2 = F.add(F.mul(E, Fv), F.mul(Z2, G))
    return (X2, Y2, Z2)

def add_2005_dl(F, X1, Y1, Z1, X2, Y2, Z2):
    """General addition, both operands projective.  13M + 4S + 9A.
       [Higuchi-Takagi 2000]; operation count as in [Lange06]; EFD add-2005-dl.
       Written from Appendix A.6 of the paper."""
    A1 = F.mul(X1, Z2)
    A2 = F.mul(X2, Z1)
    C  = F.add(A1, A2)
    B1 = F.sqr(A1)
    B2 = F.sqr(A2)
    D  = F.add(B1, B2)
    E1 = F.mul(Y1, F.sqr(Z2))
    E2 = F.mul(Y2, F.sqr(Z1))
    Fv = F.add(E1, E2)
    G  = F.mul(C, Fv)
    Z3 = F.mul(F.mul(Z1, Z2), D)
    X3 = F.add(F.mul(A1, F.add(E2, B2)), F.mul(A2, F.add(E1, B1)))
    Y3 = F.add(F.mul(F.add(F.mul(A1, G), F.mul(E1, D)), D), F.mul(F.add(G, Z3), X3))
    return (X3, Y3, Z3)

def tripling_yasin_muda(F, a2, X1, Y1):
    """Fused tripling for affine input.  [Yasin-Muda 2015, Eq. (5)]"""
    Z2 = F.sqr(X1)
    U  = F.add(Z2, Y1)
    E  = F.mul(U, X1)
    X2 = F.add(F.add(F.sqr(U), E), F.mul(a2, Z2))
    A  = F.add(F.mul(F.add(Z2, E), X2), F.mul(F.sqr(Z2), U))
    B  = F.add(X2, F.mul(X1, Z2))
    C  = F.mul(B, Z2)
    Z3 = F.sqr(C)
    D  = F.mul(X1, Z3)
    X3 = F.add(F.add(F.sqr(A), F.mul(C, F.add(A, F.sqr(B)))), F.mul(a2, Z3))
    Y3 = F.add(F.mul(F.add(D, X3), F.add(F.mul(A, C), Z3)),
               F.mul(F.add(Y1, X1), F.sqr(Z3)))
    return (X3, Y3, Z3)
