# make_sobol_bitstreams.py
# Generates 100 lines of: "<decimal_to_3dp>,<4096-bit stochastic bitstream>"
# Bitstreams use a scrambled Sobol(1D) sequence of length 2^12.

import numpy as np
from scipy.stats.qmc import Sobol

NUM_STREAMS = 100
M = 14                     # 2^14 = 16384 bits per stream
BIT_LEN = 1 << M           # 16384
OUTFILE = "sobol_bitstreams.txt"

# Optional: reproducibility (set to None for fresh randomness each run)
MASTER_SEED = 12345
rng = np.random.default_rng(MASTER_SEED)

with open(OUTFILE, "w", newline="\n") as f:
    for _ in range(NUM_STREAMS):
        # Random probability in [0,1) rounded to 3 decimals (max 0.999)
        p = float(np.round(rng.random(), 3))

        # New scrambled Sobol generator per stream with a fresh seed
        sobol_seed = int(rng.integers(0, 2**31 - 1))
        sob = Sobol(d=1, scramble=True, seed=sobol_seed)

        # Generate exactly 2^M quasi-random numbers
        nums = sob.random_base2(m=M).flatten()  # shape (4096,)

        # Stochastic bitstream: 1 if u < p else 0
        bits = ''.join('1' if u < p else '0' for u in nums)

        # Write as: "<p to 3 dp>,<4096-bit string>"
        f.write(f"{p:.3f},{bits}\n")

print(f"Wrote {NUM_STREAMS} streams to {OUTFILE}")
