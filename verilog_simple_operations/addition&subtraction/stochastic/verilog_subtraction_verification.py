# quick_subtraction_check.py
# Shows a few stochastic subtraction results vs. expected to sanity-check accuracy.

import random
from statistics import mean

# -------- Config --------
SAMPLE_MODE   = "first"   # one of: "first", "last", "random"
SAMPLE_COUNT  = 10        # how many streams to show
RANDOM_SEED   = 42        # used only if SAMPLE_MODE == "random"

A_PATH = "a_vals.txt"
B_PATH = "b_vals.txt"
Y_PATH = "y_bits.txt"     # one line per stream, bits separated by spaces

# -------- Load scalars --------
with open(A_PATH, "r") as fa:
    a_vals = [float(line.strip()) for line in fa if line.strip()]

with open(B_PATH, "r") as fb:
    b_vals = [float(line.strip()) for line in fb if line.strip()]

assert len(a_vals) == len(b_vals), "a_vals and b_vals must be same length"

# Expected subtraction (bipolar range [-1,1] if a,b in [0,1])
expected = [a - b for a, b in zip(a_vals, b_vals)]

# -------- Load stochastic bitstreams and estimate values --------
y_est = []
with open(Y_PATH, "r") as f:
    for line in f:
        bits = line.strip().split()
        if not bits:
            continue
        bits = [int(b) for b in bits]
        p = sum(bits) / len(bits)   # fraction of 1s in stream
        y = 2 * p - 1               # map [0,1] -> [-1,1] for subtraction
        y_est.append(y)

n = len(expected)
assert len(y_est) == n, f"Stream count mismatch: expected {n}, got {len(y_est)} from {Y_PATH}"

# -------- Choose sample indices --------
if SAMPLE_MODE == "first":
    idxs = list(range(min(SAMPLE_COUNT, n)))
elif SAMPLE_MODE == "last":
    m = min(SAMPLE_COUNT, n)
    idxs = list(range(n - m, n))
elif SAMPLE_MODE == "random":
    random.seed(RANDOM_SEED)
    m = min(SAMPLE_COUNT, n)
    idxs = random.sample(range(n), m)
    idxs.sort()
else:
    raise ValueError("SAMPLE_MODE must be one of: first, last, random")

# -------- Compute absolute errors --------
abs_err = [abs(e - y) for e, y in zip(expected, y_est)]
sample_err = [abs_err[i] for i in idxs]

# -------- Pretty print sample --------
print(f"\nShowing {len(idxs)} of {n} subtraction streams (mode={SAMPLE_MODE})\n")
print(f"{'idx':>5} | {'a':>8} {'b':>8} | {'exp(a-b)':>9} {'stoch':>9} | {'abs err':>8}")
print("-" * 60)
for i in idxs:
    print(f"{i:5d} | {a_vals[i]:8.5f} {b_vals[i]:8.5f} | {expected[i]:9.5f} {y_est[i]:9.5f} | {abs_err[i]:8.5f}")

# -------- Summary --------
print("\n--- Summary ---")
print(f"Sample MAE: {mean(sample_err):.6f}")
print(f"Overall MAE (all streams): {mean(abs_err):.6f}")
