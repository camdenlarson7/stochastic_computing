# stoch_mult_sweep.py
"""
Sweep stochastic multiply across several bit-lengths.
Reuses run_single_case() from stoch_mult.py to produce:
    - True analytical product
    - Stochastic baseline estimate
    - Stochastic-with-Trojan estimate
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# ensure arith_with_trojans is visible
sys.path.append(str(Path(__file__).resolve().parent))

from stoch_mult import run_single_case

# ----------------------------
# Config
# ----------------------------
BIT_POWERS = [4, 5, 6, 7, 8, 9, 10, 11, 12]  # test 16–1024 bits
K_TRIGGER = 3
SCRAMBLE = True
MODE = "flip_input_a"
SEED = 12345

def sweep_and_plot(powers, k_trigger=K_TRIGGER, mode=MODE, scramble=SCRAMBLE, seed=SEED):
    a = .5254181
    b = .3987602
    true_val = a * b

    bit_lengths = [2 ** p for p in powers]
    baseline_vals = []
    trojan_vals = []

    print(f"Running stochastic multiply sweep:")
    print(f"  a = {a:.6f}, b = {b:.6f}, true product = {true_val:.6f}\n")

    for n_bits in bit_lengths:
        res = run_single_case(a=a, b=b, n_bits=n_bits, k_trigger=k_trigger, mode=mode, scramble=scramble)
        baseline_vals.append(res["est_base"])
        trojan_vals.append(res["est_troj"])
        abs_err_troj = abs(true_val - res["est_troj"])
        print(f"Bits={n_bits:<5d}  Base={res['est_base']:.6f}  Trojan={res['est_troj']:.6f}  AbsErr={abs_err_troj:.6e}")

    # ----------------------------
    # Plot true vs baseline vs trojan
    # ----------------------------
    plt.figure(figsize=(8, 5))
    plt.plot(bit_lengths, [true_val]*len(bit_lengths),
             label="True product (a*b)", color="black", linestyle="--", linewidth=1.5)
    plt.plot(bit_lengths, baseline_vals,
             label="Stochastic (baseline)", color="tab:blue", marker="o", linewidth=1.5)
    plt.plot(bit_lengths, trojan_vals,
             label="Stochastic (with Trojan)", color="tab:red", marker="s", linewidth=1.5)

    plt.xscale('log', base=2)
    plt.xlabel("Bit length (log2 scale)")
    plt.ylabel("Computed value")
    plt.title(f"Stochastic Multiply vs Bit Length\n(a={a:.3f}, b={b:.3f}, mode={mode})")
    plt.legend()
    plt.grid(True, which="both", linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.show()

def main():
    sweep_and_plot(BIT_POWERS)

if __name__ == "__main__":
    main()

