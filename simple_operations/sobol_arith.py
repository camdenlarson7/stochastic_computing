from scipy.stats.qmc import Sobol
import numpy as np

BIT_LENGTH = 2048   # use powers of two for Sobol
SCRAMBLE = True   

def gen_sobol_pairs(n_bits: int, scramble: bool = True) -> np.ndarray:
    """
    Generate n_bits pairs (u_i, v_i) from a 2-D Sobol sequence.
    Shape: (n_bits, 2), values in [0, 1).
    """
    sobol = Sobol(d=2, scramble=scramble)
    return sobol.random(n_bits)  # (n_bits, 2)

def encode_unipolar_bitstream(value: float, uni_stream: np.ndarray) -> np.ndarray:
    """
    Unipolar encoding: bit_i = 1 if u_i < value else 0.
    value should be in [0, 1].
    """
    if not (0.0 <= value <= 1.0):
        raise ValueError("Unipolar value must be in [0, 1].")
    return (uni_stream < value).astype(np.uint8)

def sc_multiply_unipolar(a: float, b: float, n_bits: int = BIT_LENGTH, scramble: bool = SCRAMBLE):
    """
    Stochastic multiply (unipolar) via bitwise AND of two encoded streams.
    Returns (estimate, a_mean, b_mean, a_count, b_count).
    """
    uv = gen_sobol_pairs(n_bits, scramble=scramble)  # (n_bits, 2)
    u = uv[:, 0]
    v = uv[:, 1]

    A = encode_unipolar_bitstream(a, u)  # 0/1
    B = encode_unipolar_bitstream(b, v)  # 0/1

    prod_bits = (A & B)

    est = prod_bits.mean()
    a_count = A.sum()
    b_count = B.sum()
    a_est = a_count / n_bits
    b_est = b_count / n_bits

    return est, a_est, b_est, a_count, b_count

# -------------------------------
# Stubs for future ops
# -------------------------------
def sc_add_unipolar(a: float, b: float, n_bits: int = BIT_LENGTH, p_mux: float = 0.5, scramble: bool = SCRAMBLE):
    """
    Stochastic addition (unipolar) typically uses a random multiplexer to avoid overflow:
    z = MUX(p=p_mux, A, B) approximates p*A + (1-p)*B. 
    If you want (A+B)/2, set p_mux = 0.5.
    Returns estimate.
    """
    uv = gen_sobol_pairs(n_bits, scramble=scramble)  # (n_bits, 2)
    u = uv[:, 0]
    v = uv[:, 1]

    A = encode_unipolar_bitstream(a, u)
    B = encode_unipolar_bitstream(b, v)

    # Third stream for mux select
    sel = Sobol(d=1, scramble=scramble).random(n_bits).flatten()
    S = (sel < p_mux).astype(np.uint8)

    # If S=1 take A else take B
    Z = (S & A) | ((1 - S) & B)
    return Z.mean()

def sc_subtract_bipolar(a_bip: float, b_bip: float, n_bits: int = BIT_LENGTH, scramble: bool = SCRAMBLE):
    """
    Subtraction is easier in bipolar encoding where x in [-1,1] maps to Bernoulli with p=(x+1)/2.
    Then subtraction can be implemented by X + (-Y).
    This stub is here for later; you’ll encode to bipolar streams and combine with X XOR Y or
    other gates depending on the exact design.
    """
    raise NotImplementedError("Bipolar subtraction to be implemented based on your chosen gate model.")

# -------------------------------
# Demo in main()
# -------------------------------
def main():
    # Random a, b in [0,1]
    # a = np.random.rand()
    # b = np.random.rand()
    a = .459400
    b = .723400
    true_product = a * b

    for bits in range(4, 13):  # from 2^4 = 16 up to 2^12 = 4096
        bit_len = 2**bits
        sc_prod, sc_a, sc_b, a_count, b_count = sc_multiply_unipolar(
            a, b, n_bits=bit_len, scramble=SCRAMBLE
        )

        print("\n--------------------------------------")
        print(f"bit-length           : {bit_len}")
        print(f"a, b                 : {a:.6f}, {b:.6f}")
        print(f"true a*b             : {true_product:.6f}")
        print(f"stochastic a (mean)  : {sc_a:.6f} ({a_count} ones)")
        print(f"stochastic b (mean)  : {sc_b:.6f} ({b_count} ones)")
        print(f"stochastic a*b (AND) : {sc_prod:.6f}")
        print(f"absolute error       : {abs(true_product - sc_prod):.6f}")
        print("percent error        : {:.2f}%".format(
            100 * abs(true_product - sc_prod) / true_product if true_product != 0 else 0.0
        ))

# -------------------------------
# Entry point
# -------------------------------
if __name__ == "__main__":
    main()
