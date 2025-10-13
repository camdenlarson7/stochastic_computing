import struct

def binary_multiply(bin_a: str, bin_b: str) -> float:
    """
    Minimal gate-level IEEE 754 single-precision multiplication.
    Args:
        bin_a (str): 32-bit binary string representing a float (IEEE 754 single precision).
        bin_b (str): 32-bit binary string representing a float (IEEE 754 single precision).
    Returns:
        float: Product of the two floats.
    """
    # Parse IEEE 754 fields
    def parse_ieee754(bin_str):
        sign = int(bin_str[0], 2)
        exponent = int(bin_str[1:9], 2)
        mantissa = int(bin_str[9:], 2)
        return sign, exponent, mantissa

    # Get fields
    sign_a, exp_a, mant_a = parse_ieee754(bin_a)
    sign_b, exp_b, mant_b = parse_ieee754(bin_b)

    # Add implicit leading 1 for normalized numbers
    mant_a |= (1 << 23) if exp_a != 0 else 0
    mant_b |= (1 << 23) if exp_b != 0 else 0

    # Gate-level mantissa multiplication (bitwise)
    product_mant = 0
    for i in range(24):
        if (mant_b >> i) & 1:
            product_mant += mant_a << i
    # Normalize mantissa (shift right by 23)
    product_mant >>= 23

    # Exponent calculation
    product_exp = exp_a + exp_b - 127

    # Sign calculation
    product_sign = sign_a ^ sign_b

    # Assemble result (minimal, no rounding/overflow/denormals)
    result_bits = (product_sign << 31) | ((product_exp & 0xFF) << 23) | (product_mant & 0x7FFFFF)
    # Convert to float
    result_bytes = result_bits.to_bytes(4, byteorder='big')
    result_float = struct.unpack('>f', result_bytes)[0]
    return result_float

def binary_mult_gatelevel_with_sequential_trojan(bin_a: str, bin_b: str, k_trigger: int = 8, show_final_a: bool = False):
    """
    Gate-level binary multiplication for IEEE 754 single-precision floats with a sequential trojan:
    For every k_trigger-th AND gate, flip the bit of mantissa a for that gate only (do not persist the flip).
    If show_final_a is True, returns the final binary representation of a (unchanged, since flips are not persistent).
    """
    def parse_ieee754(bin_str):
        sign = int(bin_str[0], 2)
        exponent = int(bin_str[1:9], 2)
        mantissa = int(bin_str[9:], 2)
        return sign, exponent, mantissa

    sign_a, exp_a, mant_a = parse_ieee754(bin_a)
    sign_b, exp_b, mant_b = parse_ieee754(bin_b)
    mant_a |= (1 << 23) if exp_a != 0 else 0
    mant_b |= (1 << 23) if exp_b != 0 else 0

    a_bits = [(mant_a >> i) & 1 for i in range(24)]
    b_bits = [(mant_b >> i) & 1 for i in range(24)]
    result_bits = [0] * (48)
    and_count = 0
    for i in range(24):
        for j in range(24):
            a_bit = a_bits[j]
            b_bit = b_bits[i]
            and_count += 1
            # Flip the bit of a for this AND gate only if it's the k_trigger-th operation
            if and_count % k_trigger == 0:
                a_bit ^= 1
            pp = a_bit & b_bit
            k = i + j
            carry = pp
            while carry:
                sum_bit = result_bits[k] ^ carry
                carry = result_bits[k] & carry
                result_bits[k] = sum_bit
                k += 1
    product_mant = 0
    for idx in range(23, 47):
        product_mant |= (result_bits[idx] << (idx - 23))
    product_exp = exp_a + exp_b - 127
    product_sign = sign_a ^ sign_b
    result_bits_final = (product_sign << 31) | ((product_exp & 0xFF) << 23) | (product_mant & 0x7FFFFF)
    result_bytes = result_bits_final.to_bytes(4, byteorder='big')
    result_float = struct.unpack('>f', result_bytes)[0]
    if show_final_a:
        final_mant_a = sum([bit << idx for idx, bit in enumerate(a_bits)])
        final_a_bin = f"{sign_a:1b}{exp_a:08b}{final_mant_a:023b}"
        final_b_bin = f"{sign_b:1b}{exp_b:08b}{mant_b:023b}"
        return result_float, final_a_bin, final_b_bin
    return result_float

if __name__ == "__main__":
    # Example usage: 0.47015 * 0.83152
    import struct
    a_val = 0.47015
    b_val = 0.83152
    bin_a = ''.join(f'{b:08b}' for b in struct.pack('>f', a_val))
    bin_b = ''.join(f'{b:08b}' for b in struct.pack('>f', b_val))
    product = binary_multiply(bin_a, bin_b)
    print(f"{bin_a} * {bin_b} = {product}")

    # Example usage with gate-level sequential trojan
    gate_seq_trojan_product, final_a_bin, final_b_bin = binary_mult_gatelevel_with_sequential_trojan(
        bin_a, bin_b, k_trigger=8, show_final_a=True)
    print(f"  Final a: {final_a_bin} Final b: {final_b_bin} Final Product {gate_seq_trojan_product}")
