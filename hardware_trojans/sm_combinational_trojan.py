import numpy as np
import random
import math
import pandas as pd
import os
import uuid
from combinational import combination_hardware_trojan
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

# Only handles generating and saving the stochastic multiplication results as CSV
if __name__ == "__main__":
    bit_sizes = [2**i for i in range(1, 18)]
    diffs = []
    abs_diffs = []
    expected_results = []
    stochastic_results = []
    trojan_triggered_flags = []
    trojan_notes = []
    trojan_counts = []

    # Generate a and b once for all bit lengths (matching your original design)
    a = round(random.random() * 1, 6)
    b = round(random.random() * 1, 6)
    run_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    print(f"Fixed a: {a}, Fixed b: {b}, Run ID: {run_id}, Timestamp: {timestamp}")

    def stochastic_multiply_fixed(num_bits, a, b, trojan_enabled=True):
        """
        Build x and y iteratively. On each iteration i:
          - generate x[i], y[i] using a and b
          - generate three random trigger bits ta,tb,tc in {0,1}
          - if (not ta & tb & tc) == 1: choose randomly x or y and flip one random
            already-built bit (index chosen uniformly from 0..i)
        """
        x = []
        y = []
        xcount = 0
        ycount = 0
        trojan_triggered = False
        trojan_events = []
        trojan_count = 0

        for i in range(num_bits):
            # generate bits for this iteration
            if random.random() < a:
                xb = 1
                xcount += 1
            else:
                xb = 0
            if random.random() < b:
                yb = 1
                ycount += 1
            else:
                yb = 0

            # append to streams
            x.append(xb)
            y.append(yb)

            if trojan_enabled:
                # generate trigger bits for this iteration (ta, tb, tc)
                ta = random.randint(0, 1)
                tb = random.randint(0, 1)
                tc = random.randint(0, 1)
                td = random.randint(0, 1)
                te = random.randint(0, 1) 

                activated = (1 - ta) & tb & tc & td & te  # combinational trigger: not a & b & c
                if activated == 1:
                    trojan_count += 1
                    # choose which stream to corrupt
                    target = random.choice(['x', 'y'])
                    # pick a random already-built index in [0..i] to flip
                    flip_index = random.randrange(i + 1)
                    if target == 'x':
                        orig = x[flip_index]
                        x[flip_index] = combination_hardware_trojan(ta, tb, tc, td, te, x[flip_index])
                        trojan_events.append(f"iter{i}: flipped x[{flip_index}] {orig}->{x[flip_index]} (ta,tb,tc,td,te={ta},{tb},{tc},{td},{te})")
                    else:
                        orig = y[flip_index]
                        y[flip_index] = combination_hardware_trojan(ta, tb, tc, td, te, y[flip_index])
                        trojan_events.append(f"iter{i}: flipped y[{flip_index}] {orig}->{y[flip_index]} (ta,tb,tc,td,te={ta},{tb},{tc},{td},{te})")
                    trojan_triggered = True
                    

        result = []
        for c in range(num_bits):
            if ((x[c] and y[c]) == 1):
                result.append(1)
            else:
                result.append(0)

        count = sum(result)
        stochastic_result = round(count / num_bits, 8)
        expected_result = round(a * b, 8)
        return stochastic_result, expected_result, trojan_triggered, trojan_count, trojan_events
    
    for bits in bit_sizes:
        print("test ", bits)
        stochastic_result, expected_result, trojan_triggered, trojan_count, trojan_events = stochastic_multiply_fixed(bits, a, b, trojan_enabled=True)
        if expected_result != 0:
            percent_diff = abs(stochastic_result - expected_result) / abs(expected_result) * 100
        else:
            percent_diff = 0
        abs_diff = abs(stochastic_result - expected_result)
        diffs.append(percent_diff)
        abs_diffs.append(abs_diff)
        expected_results.append(expected_result)
        stochastic_results.append(stochastic_result)
        trojan_triggered_flags.append(trojan_triggered)
        # join events into one string (may be empty)
        trojan_notes.append(" | ".join(trojan_events))
        trojan_counts.append(trojan_count)

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
        'Absolute Error': abs_diffs,
        #'Trojan Triggered': trojan_triggered_flags,
        'Trojan Activation Count': trojan_counts, 
        #'Trojan Note': trojan_notes
    })
    df.to_csv('stochastic_multiplication_results_with_combinational_trojan.csv', index=False)
    print(df)
    # Append to master file
    master_file = 'all_stochastic_results.csv'
    file_exists = os.path.isfile(master_file)
    df.to_csv(master_file, mode='a', header=not file_exists, index=False)

