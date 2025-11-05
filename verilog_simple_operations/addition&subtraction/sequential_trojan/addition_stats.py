import os
import csv
import matplotlib.pyplot as plt
from statistics import mean, pstdev, median
from datetime import datetime

# ---------- Config ----------
SHOW_PLOTS = False          # True to also display figures
OUT_DIR = "graphs"
os.makedirs(OUT_DIR, exist_ok=True)
STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")

# ---------- Helpers ----------
def load_scalar_list(path):
    with open(path, "r") as f:
        return [float(line.strip()) for line in f if line.strip()]

def load_bitstreams(path):
    """
    Returns: list[list[int]] where each inner list is one stream's bits.
    """
    streams = []
    with open(path, "r") as f:
        for line in f:
            bits = line.strip().split()
            if bits:
                streams.append([int(b) for b in bits])
    return streams

def est_from_bitstreams(streams, scale=2.0, clamp01=True):
    """
    Convert bitstreams to probability estimates.
    scale=2.0 for random-mux adder (0.5*(a+b)); use 1.0 for saturating adders.
    """
    est = []
    for bits in streams:
        p = sum(bits) / len(bits)
        y = p * scale
        if clamp01:
            y = 0.0 if y < 0.0 else (1.0 if y > 1.0 else y)
        est.append(y)
    return est

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
N = len(expected)

# ---------- Load bitstreams ----------
clean_streams  = load_bitstreams("y_clean_bits.txt")
trojan_streams = load_bitstreams("y_trojan_bits.txt")
assert len(clean_streams) == N == len(trojan_streams), "Mismatch in stream counts"

BIT_LENGTH = len(clean_streams[0])
assert all(len(s) == BIT_LENGTH for s in clean_streams), "Inconsistent clean bit lengths"
assert all(len(s) == BIT_LENGTH for s in trojan_streams), "Inconsistent trojan bit lengths"

# ---------- Estimates from streams ----------
# Keep scale=2.0 for random-mux adder; change to 1.0 for saturating adders.
y_clean  = est_from_bitstreams(clean_streams,  scale=2.0, clamp01=True)
y_trojan = est_from_bitstreams(trojan_streams, scale=2.0, clamp01=True)

# ---------- Errors ----------
err_clean  = [abs(e - y) for e, y in zip(expected, y_clean)]
err_trojan = [abs(e - y) for e, y in zip(expected, y_trojan)]
mae_clean  = summarize_errors("Stochastic (clean)",  err_clean)
mae_trojan = summarize_errors("Stochastic (trojan)", err_trojan)
delta_mae  = mae_trojan - mae_clean
worse_pct  = 100.0 * sum(1 for ec, et in zip(err_clean, err_trojan) if et > ec) / N
print(f"\nΔMAE (trojan - clean): {delta_mae:+.6f}")
print(f"Percent of streams with higher error due to trojan: {worse_pct:.1f}%")

# ---------- NEW: Bits affected per stream (Hamming distance) ----------
affected_counts  = []
affected_percent = []
for s_clean, s_trojan in zip(clean_streams, trojan_streams):
    flips = sum(1 for c, t in zip(s_clean, s_trojan) if c != t)
    affected_counts.append(flips)
    affected_percent.append(flips / BIT_LENGTH)

print("\n--- Trojan Impact (per addition) ---")
print(f"Bit-length per stream: {BIT_LENGTH}")
print(f"Affected bits (mean/median/min/max): "
      f"{mean(affected_counts):.2f} / {median(affected_counts):.2f} / "
      f"{min(affected_counts)} / {max(affected_counts)}")
print(f"Affected %   (mean/median): "
      f"{100*mean(affected_percent):.2f}% / {100*median(affected_percent):.2f}%")
print(f"Streams with any flips: {sum(x>0 for x in affected_counts)}/{N} "
      f"({100*sum(x>0 for x in affected_counts)/N:.1f}%)")

# Save per-stream metrics to CSV
csv_path = os.path.join(OUT_DIR, f"trojan_impact_{STAMP}.csv")
with open(csv_path, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["stream_index", "expected", "clean_est", "trojan_est",
                "abs_err_clean", "abs_err_trojan", "affected_bits", "affected_percent"])
    for idx, (e, yc, yt, ec, et, flips, frac) in enumerate(
        zip(expected, y_clean, y_trojan, err_clean, err_trojan, affected_counts, affected_percent)
    ):
        w.writerow([idx, e, yc, yt, ec, et, flips, frac])
print(f"Saved per-stream metrics: {csv_path}")

# ---------- Plots ----------
# 1) Expected vs estimates
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
scatter_path = os.path.join(OUT_DIR, f"stoch_add_clean_vs_trojan_{STAMP}.png")
plt.savefig(scatter_path, dpi=200, bbox_inches="tight")
if SHOW_PLOTS: plt.show()
plt.close()

# 2) Absolute error per stream
plt.figure(figsize=(7,4))
plt.plot(err_clean,  label="Abs Error (Clean)",  linewidth=1)
plt.plot(err_trojan, label="Abs Error (Trojan)", linewidth=1)
plt.xlabel("Stream index")
plt.ylabel("Absolute Error")
plt.title("Per-Stream Absolute Error")
plt.legend()
plt.grid(True)
plt.tight_layout()
error_path = os.path.join(OUT_DIR, f"stoch_add_abs_error_clean_vs_trojan_{STAMP}.png")
plt.savefig(error_path, dpi=200, bbox_inches="tight")
if SHOW_PLOTS: plt.show()
plt.close()

# 3) NEW: Affected bits per stream
plt.figure(figsize=(8,4))
plt.plot(affected_counts, linewidth=1)
plt.xlabel("Stream index")
plt.ylabel("Affected bits (Hamming distance)")
plt.title("Trojan-affected bits per addition")
plt.grid(True)
plt.tight_layout()
affected_line_path = os.path.join(OUT_DIR, f"trojan_affected_bits_per_stream_{STAMP}.png")
plt.savefig(affected_line_path, dpi=200, bbox_inches="tight")
if SHOW_PLOTS: plt.show()
plt.close()

# 4) NEW: Histogram of affected percentage
plt.figure(figsize=(6,4))
plt.hist([100*x for x in affected_percent], bins=20)
plt.xlabel("Affected bits (%)")
plt.ylabel("Count of streams")
plt.title("Distribution of Trojan impact per addition")
plt.grid(True)
plt.tight_layout()
affected_hist_path = os.path.join(OUT_DIR, f"trojan_affected_percent_hist_{STAMP}.png")
plt.savefig(affected_hist_path, dpi=200, bbox_inches="tight")
if SHOW_PLOTS: plt.show()
plt.close()

print("\nSaved plots to:")
for p in [scatter_path, error_path, affected_line_path, affected_hist_path]:
    print(" -", p)

