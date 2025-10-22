#!/usr/bin/env python3
"""
stochastic_mul_with_sequential_trojan.py

Runs Sobol-based stochastic multiplication both CLEAN and with a SEQUENTIAL TROJAN
using the user's existing TrojanCounter class, which lives in a sibling folder:

<project_root>/
  hardware_trojans/             <-- contains trojan_counter.py (defines TrojanCounter)
  simple_operations/
    multiplication/
      src/
        stochastic_mul_with_sequential_trojan.py   <-- this script

Import path setup below adds the project root to sys.path so we can do:
    from hardware_trojans.trojan_counter import TrojanCounter

Outputs a CSV comparing clean vs. trojan results across bit-lengths.
"""

import os
import sys
from pathlib import Path
import uuid
from datetime import datetime
import random
import pandas as pd

# -----------------------------
# Import user's TrojanCounter from sibling folder
# -----------------------------
THIS_FILE = Path(__file__).resolve()
# .../simple_operations/multiplication/src
PROJECT_ROOT = THIS_FILE.parents[2]     # .../simple_operations
TOP_LEVEL   = PROJECT_ROOT.parent       # common parent containing hardware_trojans/
if str(TOP_LEVEL) not in sys.path:
    sys.path.insert(0, str(TOP_LEVEL))


from hardware_trojans.sequential import TrojanCounter

    

# -----------------------------
# Sobol bitstream generation
# -----------------------------
from scipy.stats.qmc import Sobol

def generate_sobol_bitstream(value: float, num_bits: int, seed: int):
    """
    Generate a Sobol bitstream for a given value in [0,1] with the given length and seed.
    Returns (bitstream_list, count_of_ones).
    """
    sobol = Sobol(d=1, scramble=True, seed=seed)
    numbers = sobol.random(num_bits).flatten()
    bitstream = [(1 if num < value else 0) for num in numbers]
    return bitstream, sum(bitstream)

# -----------------------------
# Clean stochastic multiply (reference)
# -----------------------------
def stochastic_multiply_clean(num_bits: int, a: float, b: float,
                              x_seed: int = 123, y_seed: int = 567):
    x, _ = generate_sobol_bitstream(a, num_bits, x_seed)
    y, _ = generate_sobol_bitstream(b, num_bits, y_seed)
    total = 0
    for t in range(num_bits):
        total += 1 if (x[t] & y[t]) == 1 else 0
    return round(total / num_bits, 8)

# -----------------------------
# Trojanized stochastic multiply using user's TrojanCounter
# -----------------------------
def stochastic_multiply_with_trojan_counter(num_bits: int,
                                            a: float,
                                            b: float,
                                            k_counter_bits: int = 8,
                                            x_seed: int = 123,
                                            y_seed: int = 567):
    """
    For each cycle t: compute raw_bit = x[t] & y[t]. Feed that as ER into TrojanCounter.
    The TrojanCounter increments internally and flips ER to ER* when its trigger condition is met.
    Accumulate ER* as the trojanized output bit.

    Returns (trojan_result, flips_applied, flip_rate, trigger_period)
    """
    x, _ = generate_sobol_bitstream(a, num_bits, x_seed)
    y, _ = generate_sobol_bitstream(b, num_bits, y_seed)

    trojan = TrojanCounter(k=k_counter_bits, trigger_kind="all_one")
    trojan.set_Ena(1)

    total = 0
    flips_applied = 0

    for t in range(num_bits):
        raw_bit = 1 if (x[t] & y[t]) == 1 else 0
        # Present ER for this "cycle"
        trojan.set_ER(raw_bit)
        # One synchronous "clock" tick
        er_star = trojan.clock_tick()
        total += er_star
        if er_star != raw_bit:
            flips_applied += 1

    trojan_result = round(total / num_bits, 8)
    flip_rate = flips_applied / num_bits
    trigger_period = 1 << k_counter_bits  # flips once per 2^k cycles
    return trojan_result, flips_applied, flip_rate, trigger_period

# -----------------------------
# Experiment runner
# -----------------------------
def main():
    # Powers of two up to 2^17 (like your baseline)
    bit_sizes = [2**i for i in range(1, 18)]

    # Fix a and b for all bit-lengths
    a = round(random.random(), 6)
    b = round(random.random(), 6)

    run_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    print(f"Fixed a: {a}, Fixed b: {b}, Run ID: {run_id}, Timestamp: {timestamp}")

    # Configure trojan counter width (trigger once per 2^k cycles)
    k_counter_bits = 8  # e.g., trigger every 256 cycles

    rows = []
    for bits in bit_sizes:
        print(f"Testing {bits} bits ...")
        clean = stochastic_multiply_clean(bits, a, b, x_seed=123, y_seed=567)
        troj, flips, flip_rate, trig_period = stochastic_multiply_with_trojan_counter(
            bits, a, b, k_counter_bits=k_counter_bits, x_seed=123, y_seed=567
        )
        expected = round(a * b, 8)

        if expected != 0:
            err_clean = abs(clean - expected) / abs(expected) * 100.0
            err_troj  = abs(troj  - expected) / abs(expected) * 100.0
        else:
            err_clean = 0.0
            err_troj  = 0.0

        rows.append({
            "Run ID": run_id,
            "Timestamp": timestamp,
            "a": a,
            "b": b,
            "Number of Bits": bits,
            "Expected Result": expected,
            "Stochastic Result (Clean)": clean,
            "Stochastic Result (Trojan)": troj,
            "Delta (Trojan - Clean)": round(troj - clean, 8),
            "Percent Error Clean (%)": round(err_clean, 6),
            "Percent Error Trojan (%)": round(err_troj, 6),
            "Trojan k (counter bits)": k_counter_bits,
            "Trojan Trigger Period (cycles)": trig_period,
            "Trojan Flips Applied": flips,
            "Trojan Flip Rate": round(flip_rate, 8),
        })

    df = pd.DataFrame(rows)
    out_file = "sobol_multiplication_results_seqtrojan.csv"
    df.to_csv(out_file, index=False)
    print(df)

    # Append to master file
    master_file = "all_sobol_results_seqtrojan.csv"
    append_header = not os.path.isfile(master_file)
    df.to_csv(master_file, mode='a', header=append_header, index=False)

    print(f"\nSaved: {out_file}")
    print(f"Appended to: {master_file}")
    print("\nNOTE: If import failed, ensure your file is at hardware_trojans/trojan_counter.py with class TrojanCounter.")

if __name__ == "__main__":
    main()
