#!/usr/bin/env python3
# Sobol SC multiply: error vs bit-length plots

import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats.qmc import Sobol


# -------------------------------
# SC helpers
# -------------------------------
def gen_sobol_pairs(n_bits: int, scramble: bool = True) -> np.ndarray:
    """Generate n_bits pairs (u_i, v_i) from a 2-D Sobol sequence."""
    sobol = Sobol(d=2, scramble=scramble)
    return sobol.random(n_bits)  # (n_bits, 2)

def encode_unipolar_bitstream(value: float, uni_stream: np.ndarray) -> np.ndarray:
    """Unipolar encoding: bit_i = 1 if u_i < value else 0."""
    if not (0.0 <= value <= 1.0):
        raise ValueError("Unipolar value must be in [0, 1].")
    return (uni_stream < value).astype(np.uint8)

def sc_multiply_unipolar_sobol(a: float, b: float, n_bits: int, scramble: bool = True) -> float:
    """Stochastic multiply (unipolar) using 2-D Sobol (AND)."""
    uv = gen_sobol_pairs(n_bits, scramble=scramble)
    A = encode_unipolar_bitstream(a, uv[:, 0])
    B = encode_unipolar_bitstream(b, uv[:, 1])
    return (A & B).mean()

def sc_multiply_unipolar_prng(a: float, b: float, n_bits: int, rng: np.random.Generator) -> float:
    """Stochastic multiply (unipolar) using pseudo-random generator baseline."""
    u = rng.random(n_bits)
    v = rng.random(n_bits)
    A = (u < a).astype(np.uint8)
    B = (v < b).astype(np.uint8)
    return (A & B).mean()


# -------------------------------
# Experiment runner
# -------------------------------
def run_experiment(
    powers=range(4, 13),       # 2^4 .. 2^12
    n_trials=5,                # average over multiple (a,b)
    sobol_scramble=True,
    include_prng=True,
    seed=42
):
    rng = np.random.default_rng(seed)

    bit_lengths = [2**p for p in powers]

    # arrays for Sobol
    sobol_abs = np.zeros(len(bit_lengths))
    sobol_pct = np.zeros(len(bit_lengths))

    # optional PRNG baseline
    prng_abs = np.zeros(len(bit_lengths)) if include_prng else None
    prng_pct = np.zeros(len(bit_lengths)) if include_prng else None

    for i, n_bits in enumerate(bit_lengths):
        abs_acc_sobol = 0.0
        pct_acc_sobol = 0.0

        abs_acc_prng = 0.0
        pct_acc_prng = 0.0

        for _ in range(n_trials):
            a = rng.random()
            b = rng.random()
            true_prod = a * b

            # Sobol estimate
            sc_prod_s = sc_multiply_unipolar_sobol(a, b, n_bits, scramble=sobol_scramble)
            abs_err_s = abs(true_prod - sc_prod_s)
            pct_err_s = (abs_err_s / true_prod * 100.0) if true_prod != 0 else 0.0
            abs_acc_sobol += abs_err_s
            pct_acc_sobol += pct_err_s

            if include_prng:
                sc_prod_p = sc_multiply_unipolar_prng(a, b, n_bits, rng)
                abs_err_p = abs(true_prod - sc_prod_p)
                pct_err_p = (abs_err_p / true_prod * 100.0) if true_prod != 0 else 0.0
                abs_acc_prng += abs_err_p
                pct_acc_prng += pct_err_p

        sobol_abs[i] = abs_acc_sobol / n_trials
        sobol_pct[i] = pct_acc_sobol / n_trials
        if include_prng:
            prng_abs[i] = abs_acc_prng / n_trials
            prng_pct[i] = pct_acc_prng / n_trials

    return bit_lengths, sobol_abs, sobol_pct, prng_abs, prng_pct


# -------------------------------
# Plot helpers
# -------------------------------
def plot_absolute(bit_lengths, sobol_abs, prng_abs=None, save_path=None):
    plt.figure()
    plt.plot(bit_lengths, sobol_abs, marker='o', label='Sobol (2D)')
    if prng_abs is not None:
        plt.plot(bit_lengths, prng_abs, marker='o', linestyle='--', label='Pseudo-random baseline')
    plt.xscale('log', base=2)
    plt.xlabel('Bit-Length (log2 scale)')
    plt.ylabel('Absolute Error')
    plt.title('Stochastic Multiply (Unipolar): Absolute Error vs Bit-Length')
    plt.grid(True, which='both')
    plt.legend()
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=160)
    plt.show()

def plot_percent(bit_lengths, sobol_pct, prng_pct=None, save_path=None):
    plt.figure()
    plt.plot(bit_lengths, sobol_pct, marker='o', label='Sobol (2D)')
    if prng_pct is not None:
        plt.plot(bit_lengths, prng_pct, marker='o', linestyle='--', label='Pseudo-random baseline')
    plt.xscale('log', base=2)
    plt.xlabel('Bit-Length (log2 scale)')
    plt.ylabel('Percent Error (%)')
    plt.title('Stochastic Multiply (Unipolar): Percent Error vs Bit-Length')
    plt.grid(True, which='both')
    plt.legend()
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=160)
    plt.show()


# -------------------------------
# CLI + main
# -------------------------------
def main():
    parser = argparse.ArgumentParser(description="Sobol SC error plots (absolute & percent).")
    parser.add_argument("--min_pow", type=int, default=4, help="min log2(bit-length), default 4 (16)")
    parser.add_argument("--max_pow", type=int, default=12, help="max log2(bit-length), default 12 (4096)")
    parser.add_argument("--trials", type=int, default=5, help="number of random (a,b) trials to average")
    parser.add_argument("--noscramble", action="store_true", help="disable Sobol scrambling")
    parser.add_argument("--no-prng", action="store_true", help="disable pseudo-random baseline curve")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed for (a,b)")
    parser.add_argument("--save", action="store_true", help="save PNGs instead of only showing")
    args = parser.parse_args()

    powers = range(args.min_pow, args.max_pow + 1)
    bit_lengths, sobol_abs, sobol_pct, prng_abs, prng_pct = run_experiment(
        powers=powers,
        n_trials=args.trials,
        sobol_scramble=not args.noscramble,
        include_prng=not args.no_prng,
        seed=args.seed,
    )

    save_abs = "sobol_sc_abs_error.png" if args.save else None
    save_pct = "sobol_sc_pct_error.png" if args.save else None

    plot_absolute(bit_lengths, sobol_abs, prng_abs, save_abs)
    plot_percent(bit_lengths, sobol_pct, prng_pct, save_pct)


if __name__ == "__main__":
    main()
