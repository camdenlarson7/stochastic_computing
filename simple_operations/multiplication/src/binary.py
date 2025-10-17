#!/usr/bin/env python3
# ieee754_mul_sim.py : Gate-level style simulation of IEEE-754 single-precision multiplication
# Implements bitwise adders, shift-add multiplier, normalization, and round-to-nearest-even.

from typing import Tuple

BIAS = 127

def uadd(bits_a: int, bits_b: int, width: int) -> Tuple[int, int]:
    carry = 0
    result = 0
    for i in range(width):
        a_i = (bits_a >> i) & 1
        b_i = (bits_b >> i) & 1
        s_i = a_i ^ b_i ^ carry
        carry = (a_i & b_i) | (a_i & carry) | (b_i & carry)
        result |= (s_i << i)
    return result, carry

def shift_add_mul(a: int, b: int, width: int) -> int:
    prod = 0
    for i in range(width):
        if (b >> i) & 1:
            partial, _ = uadd(prod, a << i, width*2)
            prod = partial
    return prod

def float_to_ieee754_components(x: float):
    import struct
    bits = struct.unpack('>I', struct.pack('>f', x))[0]
    sign = (bits >> 31) & 0x1
    exp  = (bits >> 23) & 0xFF
    frac = bits & ((1<<23)-1)
    return sign, exp, frac

def ieee754_components_to_float(sign: int, exp: int, frac: int) -> float:
    import struct
    bits = (sign << 31) | (exp << 23) | (frac & ((1<<23)-1))
    return struct.unpack('>f', struct.pack('>I', bits))[0]

def normalize_and_round(prod48: int, exp_sum: int):
    msb47 = (prod48 >> 47) & 1
    if msb47 == 1:
        shifted = prod48 >> 1
        exp_sum += 1
    else:
        shifted = prod48
    frac_23 = (shifted >> 23) & ((1<<23)-1)
    guard = (shifted >> 22) & 1
    roundb = (shifted >> 21) & 1
    sticky = 1 if (shifted & ((1<<21)-1)) != 0 else 0
    increment = False
    if guard == 1:
        if (roundb | sticky) == 1:
            increment = True
        else:
            increment = (frac_23 & 1) == 1
    if increment:
        frac_23_inc, carry = uadd(frac_23, 1, 23)
        frac_23 = frac_23_inc & ((1<<23)-1)
        if carry == 1:
            frac_23 = 0
            exp_sum += 1
    return exp_sum, frac_23

def mul_ieee754_single(a: float, b: float):
    sign_a, exp_a, frac_a = float_to_ieee754_components(a)
    sign_b, exp_b, frac_b = float_to_ieee754_components(b)

    def is_nan(exp, frac): return exp == 0xFF and frac != 0
    def is_inf(exp, frac): return exp == 0xFF and frac == 0
    def is_zero(exp, frac): return exp == 0 and frac == 0

    if is_nan(exp_a, frac_a) or is_nan(exp_b, frac_b):
        return float('nan'), {}
    if (is_inf(exp_a, frac_a) and is_zero(exp_b, frac_b)) or (is_inf(exp_b, frac_b) and is_zero(exp_a, frac_a)):
        return float('nan'), {}
    if is_inf(exp_a, frac_a) or is_inf(exp_b, frac_b):
        s = sign_a ^ sign_b
        return ieee754_components_to_float(s, 0xFF, 0), {}
    if is_zero(exp_a, frac_a) or is_zero(exp_b, frac_b):
        s = sign_a ^ sign_b
        return ieee754_components_to_float(s, 0, 0), {}

    def significand(exp, frac):
        if exp == 0:
            sig = frac
            e_unbiased = 1 - BIAS
        else:
            sig = (1 << 23) | frac
            e_unbiased = exp - BIAS
        return sig, e_unbiased

    sig_a, e_a = significand(exp_a, frac_a)
    sig_b, e_b = significand(exp_b, frac_b)

    prod48 = shift_add_mul(sig_a, sig_b, 24)
    e_sum = e_a + e_b
    e_norm, frac_23 = normalize_and_round(prod48, e_sum)
    exp_final = e_norm + BIAS
    sign_final = sign_a ^ sign_b

    if exp_final >= 0xFF:
        return ieee754_components_to_float(sign_final, 0xFF, 0), {}
    if exp_final <= 0:
        return ieee754_components_to_float(sign_final, 0, 0), {}

    result = ieee754_components_to_float(sign_final, exp_final, frac_23)
    return result, {
        "a": (sign_a, exp_a, frac_a),
        "b": (sign_b, exp_b, frac_b),
        "sig_a": sig_a, "sig_b": sig_b,
        "prod48": prod48, "e_sum": e_sum, "e_norm": e_norm,
        "exp_final": exp_final, "frac_final": frac_23,
        "sign_final": sign_final
    }

def bits_to_str(sign: int, exp: int, frac: int) -> str:
    return f"{sign:1b} {exp:08b} {frac:023b}"

def pack_bits(s: int, e: int, f: int) -> int:
    return (s << 31) | (e << 23) | f

def main():
    a = 0.356012
    b = 0.652977
    prod, dbg = mul_ieee754_single(a, b)

    sa, ea, fa = float_to_ieee754_components(a)
    sb, eb, fb = float_to_ieee754_components(b)
    sp, ep, fp = float_to_ieee754_components(prod)

    print("=== IEEE-754 Single-Precision Gate-Level Multiply ===")
    print(f"a = {a}")
    print(f"b = {b}")
    print(f"true product (Python double): {a*b:.10f}")
    print(f"simulated single-precision product: {prod:.10f}\n")

    print("A (sign | exponent | fraction):")
    print(bits_to_str(sa, ea, fa))
    print(f"hex: 0x{pack_bits(sa,ea,fa):08X}\n")

    print("B (sign | exponent | fraction):")
    print(bits_to_str(sb, eb, fb))
    print(f"hex: 0x{pack_bits(sb,eb,fb):08X}\n")

    print("Product (sign | exponent | fraction):")
    print(bits_to_str(sp, ep, fp))
    print(f"hex: 0x{pack_bits(sp,ep,fp):08X}\n")

    print("=== Internal Debug ===")
    for k, v in dbg.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    main()
