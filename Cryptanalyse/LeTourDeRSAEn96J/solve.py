from output import pairs_of_moduli_and_ciphers
from Crypto.Util.number import long_to_bytes
from math import gcd, lcm


e = 96 # gcd(e, phi) != 1, trouble incoming

def find_eth_root_mod_n(max_number_of_roots, p, q):
    n = p * q
    phi = lcm(p - 1, q - 1)

    k = 1
    while gcd(phi // k, e) != 1:
        k *= gcd(phi // k, e)
    
    R = []
    for a in range(max_number_of_roots):
        r = pow(a, phi // k, n)
        R.append(r)

    return R

def find_g_and_recover_all_possible_plaintexts(e, p, q, R: list, c):
    n = p * q
    phi = lcm(p - 1, q - 1)

    k = 1
    while gcd(phi // k, e) != 1:
        k *= gcd(phi // k, e)
    
    d = pow(e, -1, phi // k)
    g = pow(c, d, n)

    P = []
    for l in R:
        pt =  (l * g) % n
        P.append(pt)
    
    return P

for n1, n2, c1, c2 in pairs_of_moduli_and_ciphers:
    p = gcd(n1, n2)
    q1 = n1 // p
    q2 = n2 // p

    # Trying the first one
    R = find_eth_root_mod_n(10, p, q1)
    P = find_g_and_recover_all_possible_plaintexts(e, p, q1, R, c1)
    for pt in P:
        try:
            print(long_to_bytes(pt).decode("utf-8"))
        except ValueError:
            pass
    
    # Trying the second one
    R = find_eth_root_mod_n(10, p, q2)
    P = find_g_and_recover_all_possible_plaintexts(e, p, q2, R, c2)
    for pt in P:
        try:
            print(long_to_bytes(pt).decode("utf-8"))
        except ValueError:
            pass
