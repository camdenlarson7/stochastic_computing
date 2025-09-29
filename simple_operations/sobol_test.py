from scipy.stats.qmc import Sobol
import numpy as np

sobol = Sobol(d=1, scramble=True)
a = sobol.random()
b = sobol.random()
product = a*b

bitstream_a = []
bitstream_b = []

a_count = 0
b_count = 0
for i in range(128):
    test = sobol.random()
    if a > test:
        bitstream_a.append(1)
        a_count = a_count + 1
    else:
        bitstream_a.append(0)
for j in range(128):
    test = sobol.random()
    if b > test:
        bitstream_b.append(1)
        b_count = b_count + 1
    else:
        bitstream_b.append(0)

stochastic_a = a_count / 128
stochastic_b = b_count / 128

count = 0
for c in range(128):
    if ((bitstream_a[c] and bitstream_b[c])):
        count = count + 1

stochastic_product = count / 128

print("a: ", a, " b: ", b, " a*b: ", product, " stochastic a: ", stochastic_a, " stochastic b: ", stochastic_b, " stochastic a*b: ", stochastic_product)
