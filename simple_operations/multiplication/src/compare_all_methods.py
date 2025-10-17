import struct
import matplotlib.pyplot as plt
from sequential_trojan_binary import binary_multiply, binary_mult_gatelevel_with_sequential_trojan
from stochastic import generate_sobol_bitstream
import numpy as np
import pandas as pd
import random

BIT_LENGTH = 131072

N = 100  # Number of random test cases
abs_diff_bin_trojan = []
abs_diff_stoch = []
abs_diff_stoch_trojan = []
labels = []

for i in range(N):
    A_VAL = random.uniform(0, 1)
    B_VAL = random.uniform(0, 1)
    bin_a = ''.join(f'{b:08b}' for b in struct.pack('>f', A_VAL))
    bin_b = ''.join(f'{b:08b}' for b in struct.pack('>f', B_VAL))
    true_val = A_VAL * B_VAL

    # Binary with trojan
    trojan_result, _, _ = binary_mult_gatelevel_with_sequential_trojan(
        bin_a, bin_b, k_trigger=8, show_final_a=True)
    abs_diff_bin_trojan.append(abs(true_val - trojan_result))

    # Stochastic without trojan
    def stochastic_multiply_fixed(num_bits, a, b):
        x, _ = generate_sobol_bitstream(a, num_bits, seed=123)
        y, _ = generate_sobol_bitstream(b, num_bits, seed=567)
        result = [(x[c] & y[c]) for c in range(num_bits)]
        count = sum(result)
        return round(count / num_bits, 8)
    stoch_result = stochastic_multiply_fixed(BIT_LENGTH, A_VAL, B_VAL)
    abs_diff_stoch.append(abs(true_val - stoch_result))

    # Stochastic with trojan
    x, _ = generate_sobol_bitstream(A_VAL, BIT_LENGTH, seed=123)
    y, _ = generate_sobol_bitstream(B_VAL, BIT_LENGTH, seed=567)
    A_trojan = x.copy()
    for j in range(0, BIT_LENGTH, 8):
        A_trojan[j] ^= 1
    result_trojan = [(A_trojan[c] & y[c]) for c in range(BIT_LENGTH)]
    stoch_result_trojan = round(sum(result_trojan) / BIT_LENGTH, 8)
    abs_diff_stoch_trojan.append(abs(true_val - stoch_result_trojan))

    labels.append(f"{A_VAL:.3f}*{B_VAL:.3f}")

# Calculate mean and variance
mean_bin_trojan = np.mean(abs_diff_bin_trojan)
var_bin_trojan = np.var(abs_diff_bin_trojan)
mean_stoch = np.mean(abs_diff_stoch)
var_stoch = np.var(abs_diff_stoch)
mean_stoch_trojan = np.mean(abs_diff_stoch_trojan)
var_stoch_trojan = np.var(abs_diff_stoch_trojan)

# Create table
results_df = pd.DataFrame({
    'Method': ['Binary (Trojan)', 'Stochastic (No Trojan)', 'Stochastic (Trojan)'],
    'Mean Absolute Error': [mean_bin_trojan, mean_stoch, mean_stoch_trojan],
    'Variance': [var_bin_trojan, var_stoch, var_stoch_trojan]
})
print('\nSummary Table:')
print(results_df.to_string(index=False))

plt.figure(figsize=(12, 6))
trial_numbers = list(range(1, N + 1))
plt.plot(trial_numbers, abs_diff_bin_trojan, marker='o', label='Binary (Trojan)')
plt.plot(trial_numbers, abs_diff_stoch, marker='s', label='Stochastic (No Trojan)')
plt.plot(trial_numbers, abs_diff_stoch_trojan, marker='^', label='Stochastic (Trojan)')
plt.ylabel('Absolute Error')
plt.xlabel('Trial Number')
plt.title('Absolute Error vs True Value for Multiplication Methods')
plt.legend()
plt.xticks(np.arange(1, N+1, max(1, N//10)))
plt.tight_layout()
plt.show()

# Plot the summary table as a graphic
fig, ax = plt.subplots(figsize=(7, 2))
ax.axis('off')
table = ax.table(
    cellText=results_df.round(8).values,
    colLabels=results_df.columns,
    cellLoc='center',
    loc='center',
    colColours=['#dbeafe']*len(results_df.columns)
)
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1.2, 1.5)
plt.title('Summary Table: Mean and Variance of Absolute Error', pad=20)
plt.tight_layout()
plt.show()
