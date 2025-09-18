import numpy as np
import random
import math
import pandas as pd
import os
import uuid
from datetime import datetime

def stochastic_multiply(num_bits=128):

    a = round(random.random() * 1, 6)
    print("number a: ", a)
    b = round(random.random() * 1, 6)
    print("number b :", b)
    x = []
    y = []
    xcount = 0
    ycount = 0
    for i in range(num_bits):
        num = random.random() * 1
        if num < a:
            x.append(1)
            xcount = xcount + 1
        else:
            x.append(0)
            
    for j in range(num_bits):
        num = random.random() * 1
        if num < b:
            y.append(1)
            ycount = ycount + 1
        else:
            y.append(0)
            

    print("number a stochastic value: ", xcount / num_bits)
    print("number b stochastic value: ", ycount / num_bits)
    # print("number a bit stream ", x)
    # print("number b bit stream: ", y)
    result = []
    for c in range(num_bits):
        if ((x[c] and y[c]) == 1):
            result.append(1)
        else:
            result.append(0)
        
    # print("result: ", result)

    count = 0
    for num in result:
        if num == 1:
            count = count + 1
    stochastic_result = round(count / num_bits, 8)
    expected_result = round(a * b, 8)
    print("Stochastic result: ", stochastic_result)
    print("Expected Result: ", expected_result)
    return stochastic_result, expected_result

# Only handles generating and saving the stochastic multiplication results as CSV
if __name__ == "__main__":
    bit_sizes = [2**i for i in range(1, 18)]
    diffs = []
    abs_diffs = []
    expected_results = []
    stochastic_results = []
    # Generate a and b once for all bit lengths
    a = round(random.random() * 1, 6)
    b = round(random.random() * 1, 6)
    run_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    print(f"Fixed a: {a}, Fixed b: {b}, Run ID: {run_id}, Timestamp: {timestamp}")
    def stochastic_multiply_fixed(num_bits, a, b):
        x = []
        y = []
        xcount = 0
        ycount = 0
        for i in range(num_bits):
            num = random.random() * 1
            if num < a:
                x.append(1)
                xcount = xcount + 1
            else:
                x.append(0)
        for j in range(num_bits):
            num = random.random() * 1
            if num < b:
                y.append(1)
                ycount = ycount + 1
            else:
                y.append(0)
        result = []
        for c in range(num_bits):
            if ((x[c] and y[c]) == 1):
                result.append(1)
            else:
                result.append(0)
        count = 0
        for num in result:
            if num == 1:
                count = count + 1
        stochastic_result = round(count / num_bits, 8)
        expected_result = round(a * b, 8)
        return stochastic_result, expected_result
    for bits in bit_sizes:
        print("test ", bits)
        stochastic_result, expected_result = stochastic_multiply_fixed(bits, a, b)
        if expected_result != 0:
            percent_diff = abs(stochastic_result - expected_result) / abs(expected_result) * 100
        else:
            percent_diff = 0
        abs_diff = abs(stochastic_result - expected_result)
        diffs.append(percent_diff)
        abs_diffs.append(abs_diff)
        expected_results.append(expected_result)
        stochastic_results.append(stochastic_result)
    # Create DataFrame for results
    df = pd.DataFrame({
        'Run ID': run_id,
        'Timestamp': timestamp,
        'a': a,
        'b': b,
        'Number of Bits': bit_sizes,
        'Expected Result': expected_results,
        'Stochastic Result': stochastic_results,
        'Percent Error (%)': diffs,
        'Absolute Error': abs_diffs
    })
    df.to_csv('stochastic_multiplication_results.csv', index=False)
    print(df)
    # Append to master file
    master_file = 'all_stochastic_results.csv'
    file_exists = os.path.isfile(master_file)
    df.to_csv(master_file, mode='a', header=not file_exists, index=False)