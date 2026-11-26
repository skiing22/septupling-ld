#!/usr/bin/env python3
"""small_curve_orders.py -- counts points of exact order 5 and 6 on the 24 small test curves
(Sec. 4.4): y^2+xy=x^3+a2x^2+a6, a2 in {0,1}, a6 in {1,3,5}, over F_2^5, F_2^7, F_2^9, F_2^11."""
def mul(a,b,m,poly):
    r=0
    while b:
        if b&1: r^=a
        b>>=1; a<<=1
        if a>>m&1: a^=poly
    return r
def inv(a,m,poly):
    # a^(2^m-2)
    r=1; e=(1<<m)-2; base=a
    while e:
        if e&1: r=mul(r,base,m,poly)
        base=mul(base,base,m,poly); e>>=1
    return r
def tr(a,m,poly):
    t=a; s=a
    for _ in range(m-1):
        t=mul(t,t,m,poly); s^=t
    return s
polys={5:(1<<5)|(1<<2)|1,7:(1<<7)|2|1,9:(1<<9)|(1<<4)|1,11:(1<<11)|(1<<2)|1}
tot5=tot6=tot6any=0
for m,poly in polys.items():
    for a2 in (0,1):
        for a6 in (1,3,5):
            cnt=0
            for x in range(1,1<<m):
                xi=inv(x,m,poly); rhs=x^a2^mul(a6,mul(xi,xi,m,poly),m,poly)
                if tr(rhs,m,poly)==0: cnt+=1
            N=2+2*cnt
            e5=4 if N%5==0 else 0
            e6=2 if N%3==0 else 0
            any6 = (1 + (2 if N%3==0 else 0) + e6)  # orders 2,3,6
            tot5+=e5; tot6+=e6; tot6any+=any6
            print(m,a2,a6,N, "5|N" if e5 else "", "3|N" if e6 else "")
print("exact order 5:",tot5," exact order 6:",tot6," any nonzero P with 6P=O:",tot6any)
