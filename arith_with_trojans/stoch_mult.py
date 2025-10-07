# simple_trojan_test.py
"""
Simple single-case Trojan test:
 - injection mode: flip_input_a (trojan flips A's bit when active)
 - performs one stochastic multiplication (unipolar) using Sobol pairs
 - shows baseline vs trojan bitstreams for A, B, and product
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path

# make parent (repo root) visible so sibling packages import cleanly
sys.path.append(str(Path(__file__).resolve().parent.parent))

from hardware_trojans.sequential import TrojanCounter
from simple_operations.sobol_arith import sobol_pairs_base2, encode_unipolar_bitstream

BIT_LENGTH = 32     # small so we can read the printed bitstreams
K_TRIGGER  = 2      # triggers when counter hits all-ones (period 2^K)
SCRAMBLE   = True

def run_single_case(a: float, b: float, n_bits: int, k_trigger: int,
                    mode: str = "flip_input_a", scramble: bool = True):
    # Sobol samples and baseline encodes
    uv = sobol_pairs_base2(n_bits, scramble=scramble, seed=47823, skip=0)
    A = encode_unipolar_bitstream(a, uv[:, 0])
    B = encode_unipolar_bitstream(b, uv[:, 1])

    # Baseline product (no injection)
    prod_base = (A & B).astype(np.uint8)

    # Trojan-enabled run (we'll record injected A/B and product)
    trojan = TrojanCounter(k=k_trigger, trigger_kind="all_one")
    trojan.set_ER(0)
    trojan.set_Ena(1)

    A_troj   = np.zeros(n_bits, dtype=np.uint8)
    B_troj   = np.zeros(n_bits, dtype=np.uint8)
    prod_troj = np.zeros(n_bits, dtype=np.uint8)
    erstar_trace = np.zeros(n_bits, dtype=np.uint8)

    for i in range(n_bits):
        a_bit = int(A[i])
        b_bit = int(B[i])

        er_star = trojan.clock_tick()
        erstar_trace[i] = er_star

        a_t = a_bit
        b_t = b_bit

        if er_star and mode == "flip_input_a":
            a_t ^= 1
            # print(f"Cycle {i}: ER* active, flipping A bit")
        elif er_star and mode == "flip_input_b":
            b_t ^= 1
        # (you could add other modes here if needed)

        A_troj[i] = a_t
        B_troj[i] = b_t
        prod_troj[i] = a_t & b_t
    
    return {
        "A": A, "B": B, "Prod_base": prod_base,
        "A_troj": A_troj, "B_troj": B_troj, "Prod_troj": prod_troj,
        "erstar_trace": erstar_trace,
        "a": a, "b": b,
        "true": a * b,
        "est_base": float(prod_base.mean()),
        "est_troj": float(prod_troj.mean())
    }

def bits_to_str(bits: np.ndarray) -> str:
    """Turn a 0/1 array into a compact string, e.g., '101001...'."""
    return ''.join('1' if x else '0' for x in bits.tolist())

def main():
    rng = np.random.default_rng(12345)
    a = float(rng.random()); b = float(rng.random())

    res = run_single_case(a=a, b=b, n_bits=BIT_LENGTH, k_trigger=K_TRIGGER,
                          mode="flip_input_a", scramble=SCRAMBLE)

    print(f"BIT_LENGTH={BIT_LENGTH}, K_TRIGGER={K_TRIGGER}")
    print(f"a={res['a']:.6f}, b={res['b']:.6f}")
    print(f"true value={res['true']:.6f}, baseline est={res['est_base']:.6f}, trojan est={res['est_troj']:.6f}")
    print("\n--- Bitstreams (baseline) ---")
    print("A         :", bits_to_str(res["A"]))
    print("B         :", bits_to_str(res["B"]))
    print("Prod_base :", bits_to_str(res["Prod_base"]))
    print("\n--- Bitstreams (trojan-injected) ---")
    print("A_troj    :", bits_to_str(res["A_troj"]))
    print("B_troj    :", bits_to_str(res["B_troj"]))
    print("Prod_troj :", bits_to_str(res["Prod_troj"]))
    print("\nER* (1=trojan active):")
    print(bits_to_str(res["erstar_trace"]))

    # Visualization: stacked rows so flips are obvious
    # Order: ER*, A, A_troj, B, B_troj, Prod_base, Prod_troj
    viz = np.vstack([
        res["erstar_trace"],
        res["A"], res["A_troj"],
        res["B"], res["B_troj"],
        res["Prod_base"], res["Prod_troj"],
    ]).astype(float)

    plt.figure(figsize=(10, 3.5))
    plt.imshow(viz, aspect='auto', interpolation='nearest')
    plt.yticks(range(viz.shape[0]),
               ["ER*", "A", "A_troj", "B", "B_troj", "Prod_base", "Prod_troj"])
    plt.xticks(range(BIT_LENGTH), range(BIT_LENGTH))
    plt.title("Baseline vs Trojan Bitstreams (columns are cycles)")
    plt.xlabel("Cycle index")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
