from scipy.stats.qmc import Sobol
import numpy as np
import math

def sobol_triplets(n_bits: int, scramble=True, seed=None):
    """Generate 3D Sobol sequences (u, v, s) for one full bitstream."""
    sob = Sobol(d=3, scramble=scramble, seed=seed)
    m = int(math.log2(n_bits))
    return sob.random_base2(m)  # shape: (n_bits, 3)

def encode_unipolar(value: float, uni_stream: np.ndarray):
    """Convert a Sobol sequence to a stochastic bitstream."""
    return (uni_stream < value).astype(np.uint8)

def sobol_encode_matrix(values_2d: np.ndarray, bit_length=128, scramble=True, base_seed=42):
    """Convert 2D array of decimals → 3D Sobol stochastic bitstreams."""
    num_streams, num_inputs = values_2d.shape
    bitstreams = np.zeros((num_streams, num_inputs, bit_length), dtype=np.uint8)

    for i in range(num_streams):
        for j in range(num_inputs):
            val = values_2d[i, j]
            sob_seq = sobol_triplets(bit_length, scramble=scramble, seed=(i * num_inputs + j + base_seed))
            bitstreams[i, j, :] = encode_unipolar(val, sob_seq[:, 0])

    return bitstreams

if __name__ == "__main__":
    # Load your decimal matrix
    values = np.loadtxt("imageMatrixDec.txt", delimiter=",")
    if values.ndim == 1:
        values = values.reshape(1, -1)

    bit_length = 128
    bitstreams = sobol_encode_matrix(values, bit_length=bit_length, scramble=True)

    # Save in grouped format (each pixel’s bitstream separated by commas)
    with open("imageMatrixBits.txt", "w") as f:
        for i, row in enumerate(bitstreams):
            groups = []
            for j, bits in enumerate(row):
                bit_str = "".join(map(str, bits))  # convert bits to string
                groups.append(bit_str)
            f.write(",".join(groups) + "\n")

    print("Read:", values.shape)
    print("Generated bitstreams:", bitstreams.shape)
    print("Saved grouped output to: imageMatrixBits.txt")
