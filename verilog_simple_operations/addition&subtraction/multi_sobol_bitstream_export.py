from scipy.stats.qmc import Sobol
import numpy as np
import math
import random

BIT_LENGTH = 128          # number of bits per stream
SCRAMBLE = True
NUM_STREAMS = 500        
p_mux = 0.5              # 0.5 = balanced selection

a_vals = [random.random() for _ in range(NUM_STREAMS)]
b_vals = [random.random() for _ in range(NUM_STREAMS)]
with open("a_vals.txt", "w") as fa:
    for val in a_vals:
        fa.write(f"{val:.6f}\n")

with open("b_vals.txt", "w") as fb:
    for val in b_vals:
        fb.write(f"{val:.6f}\n")

def sobol_triplets(n_bits: int, scramble=True, seed=None):
    """Generate 3D Sobol sequences (u, v, s) for one full bitstream."""
    sob = Sobol(d=3, scramble=scramble, seed=seed)
    m = int(math.log2(n_bits))
    return sob.random_base2(m)  # shape: (n_bits, 3)

def encode_unipolar(value: float, uni_stream: np.ndarray):
    """Convert a Sobol sequence to a stochastic bitstream."""
    return (uni_stream < value).astype(np.uint8)

# Each row in these matrices will be one independent bitstream
A_matrix = []
B_matrix = []
Sel_matrix = []

for i, (a_val, b_val) in enumerate(zip(a_vals, b_vals)):
    # Generate new Sobol triplets for each stream
    uvs = sobol_triplets(BIT_LENGTH, scramble=SCRAMBLE, seed=i + 42)
    u, v, s = uvs[:, 0], uvs[:, 1], uvs[:, 2]

    A_bits = encode_unipolar(a_val, u)
    B_bits = encode_unipolar(b_val, v)
    Sel_bits = (s < p_mux).astype(np.uint8)

    A_matrix.append(A_bits)
    B_matrix.append(B_bits)
    Sel_matrix.append(Sel_bits)

# Stack all rows together (num_streams × BIT_LENGTH)
A_matrix = np.vstack(A_matrix)
B_matrix = np.vstack(B_matrix)
Sel_matrix = np.vstack(Sel_matrix)


np.savetxt("a_bits.txt", A_matrix, fmt="%d")
np.savetxt("b_bits.txt", B_matrix, fmt="%d")
np.savetxt("sel_bits.txt", Sel_matrix, fmt="%d")

print(f"Generated {len(a_vals)} bitstreams × {BIT_LENGTH} bits each")
print("Files saved: a_bits.txt, b_bits.txt, sel_bits.txt")
