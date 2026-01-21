#!/usr/bin/env python3
import random
from datetime import datetime
from typing import Tuple, Dict
from scipy.stats.qmc import Sobol

def generate_sobol_bitstream(value: float, num_bits: int, seed: int):
    """
    Generate a Sobol bitstream for a given value in [0,1] and bitstream length.
    Returns (bits, count_of_ones).
    """
    sobol = Sobol(d=1, scramble=True, seed=seed)
    nums = sobol.random(num_bits).flatten()
    bits = [1 if u < value else 0 for u in nums]
    return bits, sum(bits)

def stochastic_multiply(
    a: float,
    b: float,
    bit_length: int,
    x_seed: int = 123,
    y_seed: int = 567,
    round_decimals: int = 8,
) -> Tuple[float, float, Dict[str, float]]:
    """
    Perform stochastic multiplication of a and b in [0,1] using AND on Sobol bitstreams.

    Returns:
      stochastic_result (float),
      expected_result (float),
      info (dict) with aux stats.
    """
    x_bits, _ = generate_sobol_bitstream(a, bit_length, seed=x_seed)
    y_bits, _ = generate_sobol_bitstream(b, bit_length, seed=y_seed)

    ones = 0
    for i in range(bit_length):
        ones += (x_bits[i] & y_bits[i])  # AND gate

    stochastic_result = round(ones / bit_length, round_decimals)
    expected_result   = round(a * b, round_decimals)

    abs_err = abs(stochastic_result - expected_result)
    pct_err = (abs_err / abs(expected_result) * 100.0) if expected_result != 0 else 0.0

    info = {
        "ones": ones,
        "bit_length": bit_length,
        "abs_error": round(abs_err, round_decimals),
        "percent_error": pct_err,
        "x_seed": x_seed,
        "y_seed": y_seed,
    }
    return stochastic_result, expected_result, info

if __name__ == "__main__":
    # Single example run — tweak bit_length as needed
    bit_length = 2**28
    a = round(random.random(), 6)
    b = round(random.random(), 6)

    print(f"[{datetime.now().isoformat()}]")
    print(f"bit_length = {bit_length}")
    print(f"a = {a}, b = {b}")

    stoch, expect, info = stochastic_multiply(a, b, bit_length)
    print(f"stochastic_result = {stoch}")
    print(f"expected_result   = {expect}")
    print(f"absolute_error    = {info['abs_error']:.8f}")
    print(f"percent_error     = {info['percent_error']:.6f}%")
