
from statistics import mean


with open("a_vals.txt", "r") as fa:
    a_vals = [float(line.strip()) for line in fa if line.strip()]

with open("b_vals.txt", "r") as fb:
    b_vals = [float(line.strip()) for line in fb if line.strip()]

assert len(a_vals) == len(b_vals), "Error: a_vals and b_vals must have the same length"

expected_y_vals = [a -b for a, b in zip(a_vals, b_vals)]

print(expected_y_vals)


y_stochastic_result = []
with open("y_bits.txt", "r") as f:
    for line in f:
        bits = line.strip().split()
        if not bits:
            continue  # skip empty lines

        # Convert bits to integers
        bits = [int(b) for b in bits]

        # Compute stochastic value (mean of bits)
        value = sum(bits) / len(bits)
        y_stochastic_result.append(value)




#absolute error calculation
scaled_y_vals = [2*v - 1 for v in y_stochastic_result]
absolute_errors = [abs((a - b) - scaled) for (a, b), scaled in zip(zip(a_vals, b_vals), scaled_y_vals)]
print(scaled_y_vals)
print(absolute_errors)
print(mean(absolute_errors))