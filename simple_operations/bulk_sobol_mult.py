import subprocess

if __name__ == "__main__":
    num_runs = 1000  # Number of times to run sc_arith
    for i in range(num_runs):
        print(f"Run {i+1} of {num_runs}")
        subprocess.run(['python', 'sobol_mult.py'])
