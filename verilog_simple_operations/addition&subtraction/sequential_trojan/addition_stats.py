import matplotlib.pyplot as plt
from statistics import mean, pstdev

# ---------- Helpers ----------
def load_scalar_list(path):
    with open(path, "r") as f:
        return [float(line.strip()) for line in f if line.strip()]

def est_from_bitstreams(path, scale=2.0, clamp01=True):
    """
    Convert lines of 0/1 bits to probability estimates.
    scale=2.0 is correct for the 'random-mux adder' (which outputs 0.5*(a+b)).
    If you switch to a saturating hardware adder (e.g., OR/probabilistic),
    set scale=1.0.
    """
    estimates = []
    with open(path, "r") as f:
        for line in f:
            bits = line.strip().split()
            if not bits:
                continue
            bits = [int(b) for b in bits]
            p = sum(bits) / len(bits)
            y = p * scale
            if clamp01:
                y = 0.0 if y < 0.0 else (1.0 if y > 1.0 else y)
            estimates.append(y)
    return estimates

def summarize_errors(name, errors):
    mae = mean(errors)
    sd  = pstdev(errors) if len(errors) > 1 else 0.0
    print(f"\n--- {name} ---")
    print(f"Streams: {len(errors)}")
    print(f"Mean Absolute Error (MAE): {mae:.6f}")
    print(f"Std Dev of Error:         {sd:.6f}")
    print(f"Min Abs Err: {min(errors):.6f} | Max Abs Err: {max(errors):.6f}")
    return mae

# ---------- Load scalar inputs ----------
a_vals = load_scalar_list("a_vals.txt")
b_vals = load_scalar_list("b_vals.txt")
assert len(a_vals) == len(b_vals), "a_vals and b_vals must have same length"

# Expected true output (unipolar saturated sum)
expected = [min(a + b, 1.0) for a, b in zip(a_vals, b_vals)]

# ---------- Load stochastic outputs ----------
# For your random-mux adder, keep scale=2.0; if you switch to a saturating adder, use scale=1.0.
y_clean   = est_from_bitstreams("y_clean_bits.txt",  scale=2.0, clamp01=True)
y_trojan  = est_from_bitstreams("y_trojan_bits.txt", scale=2.0, clamp01=True)

# Sanity checks
n = len(expected)
assert len(y_clean)  == n, "Mismatch: expected vs y_clean stream count"
assert len(y_trojan) == n, "Mismatch: expected vs y_trojan stream count"

# ---------- Errors ----------
err_clean  = [abs(e - y) for e, y in zip(expected, y_clean)]
err_trojan = [abs(e - y) for e, y in zip(expected, y_trojan)]

mae_clean  = summarize_errors("Stochastic (clean)",  err_clean)
mae_trojan = summarize_errors("Stochastic (trojan)", err_trojan)

delta_mae = mae_trojan - mae_clean
worse_pct = 100.0 * sum(1 for ec, et in zip(err_clean, err_trojan) if et > ec) / n
print(f"\nΔMAE (trojan - clean): {delta_mae:+.6f}")
print(f"Percent of streams with higher error due to trojan: {worse_pct:.1f}%")

# ---------- Visualization ----------
plt.figure(figsize=(7,7))
plt.scatter(expected, y_clean,  alpha=0.6, label="Clean",  s=18)
plt.scatter(expected, y_trojan, alpha=0.6, label="Trojan", s=18, marker="x")
plt.plot([0,1],[0,1],'k--',label='Ideal y=x')
plt.xlabel("Expected Output (min(a+b, 1))")
plt.ylabel("Stochastic Estimate")
plt.title("Stochastic Addition: Clean vs Trojan")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Optional: error comparison plot
plt.figure(figsize=(7,4))
plt.plot(err_clean,  label="Abs Error (Clean)",  linewidth=1)
plt.plot(err_trojan, label="Abs Error (Trojan)", linewidth=1)
plt.xlabel("Stream index")
plt.ylabel("Absolute Error")
plt.title("Per-Stream Absolute Error")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
