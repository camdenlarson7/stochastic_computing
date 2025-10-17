# simple_trojan_test.py
"""
Single-case stochastic multiply with a sequential Trojan (clean, function-based).

Pipeline per cycle:
 1) A_bit = [u < a], B_bit = [v < b]
 2) ER* = trojan.clock_tick()
 3) If ER*==1: A_bit ^= 1
 4) Prod_bit = A_bit & B_bit

This script prints baseline vs trojan estimates and basic counts.
"""

from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
from scipy.stats.qmc import Sobol
import random

# Make parent (repo root) visible so sibling packages import cleanly
sys.path.append(str(Path(__file__).resolve().parent.parent))

from hardware_trojans.sequential import TrojanCounter
from simple_operations.sobol_mult import generate_sobol_bitstream

# ----------------------------
# Config
# ----------------------------
BIT_LENGTH = 131072
K_TRIGGER  = 3
SCRAMBLE   = True
SOBOL_SEED = 47823
ROW_SHIFT  = 0      # optional circular shift of Sobol rows (0 = none)
MODE       = "flip_input_a"  # keep it simple: flip A when ER* is active

# ----------------------------
# Helpers
# ----------------------------
def generate_independent_streams(a, b, n_bits, seed_a, seed_b):
    # Use the same strategy as sobol_mult.py for independent Sobol bitstreams
    # Import the function directly for consistency
    A, _ = generate_sobol_bitstream(a, n_bits, seed=seed_a)
    B, _ = generate_sobol_bitstream(b, n_bits, seed=seed_b)
    A = np.array(A, dtype=np.uint8)
    B = np.array(B, dtype=np.uint8)
    return A, B


def baseline_product(A: np.ndarray, B: np.ndarray) -> tuple[np.ndarray, float, int, int]:
    """Compute baseline product bits and stats by ANDing each bit individually."""
    prod = np.empty_like(A, dtype=np.uint8)
    for i in range(len(A)):
        prod[i] = A[i] & B[i]
    est = float(prod.mean())
    return prod, est, int(A.sum()), int(B.sum())

def run_trojan_on_A(A: np.ndarray,
                    B: np.ndarray,
                    k_trigger: int,
                    mode: str = "flip_input_a") -> tuple[np.ndarray, np.ndarray, np.ndarray, float, int, int]:
    """
    Per-cycle: tick trojan -> if ER*==1 and mode=='flip_input_a', flip A bit, then AND.
    Returns (A_troj, B_troj, Prod_troj, est_troj, A1s, B1s).
    """
    n = len(A)
    trojan = TrojanCounter(k=k_trigger, trigger_kind="all_one")
    trojan.set_ER(0)
    trojan.set_Ena(1)

    A_t = np.empty(n, dtype=np.uint8)
    B_t = np.empty(n, dtype=np.uint8)
    P_t = np.empty(n, dtype=np.uint8)

    for i in range(n):
        a_bit = int(A[i])
        b_bit = int(B[i])
        er_star = trojan.clock_tick()

        if er_star and mode == "flip_input_a":
            a_bit ^= 1
        elif er_star and mode == "flip_input_b":
            b_bit ^= 1
        # (keep minimal; other modes can be added later)

        A_t[i] = a_bit
        B_t[i] = b_bit
        P_t[i] = a_bit & b_bit

    est_troj = float(P_t.mean())
    return A_t, B_t, P_t, est_troj, int(A_t.sum()), int(B_t.sum())

# ----------------------------
# Main: single simple case
# ----------------------------
def main():
    a = random.random()
    b = random.random()

    print(f"a={a:.6f}, b={b:.6f}, true a*b={a*b:.6f}")


    A, B = generate_independent_streams(a, b, BIT_LENGTH, seed_a=123, seed_b=567)
    print("A :", A)
    print("B :", B)

    # Baseline
    prod_base, est_base, a_ones, b_ones = baseline_product(A, B)
    print(f"Baseline: est={est_base:.6f} | A ones={a_ones}/{BIT_LENGTH} ({a_ones/BIT_LENGTH:.6f})"
          f" | B ones={b_ones}/{BIT_LENGTH} ({b_ones/BIT_LENGTH:.6f})")

    # Trojan (flip A on ER*)
    A_t, B_t, prod_t, est_troj, a1_t, b1_t = run_trojan_on_A(A, B, k_trigger=K_TRIGGER, mode=MODE)
    print(f"Trojan  : est={est_troj:.6f} | A' ones={a1_t}/{BIT_LENGTH} ({a1_t/BIT_LENGTH:.6f})"
          f" | B' ones={b1_t}/{BIT_LENGTH} ({b1_t/BIT_LENGTH:.6f})")

if __name__ == "__main__":
    main()
