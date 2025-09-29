# Stochastic Computing Practice

This repository contains scripts and tools for simulating, analyzing, and visualizing stochastic multiplication using bitstreams. The project is designed to help explore the accuracy and behavior of stochastic arithmetic under various conditions.

## Contents

- `sc_arith.py` — Runs a single stochastic multiplication experiment for a fixed pair of random factors (`a`, `b`) across a range of bitstream lengths. Results are appended to stochastic_multiplication_results.csv for later analysis.
- `bulk_arith.py` — Automates running `sc_arith.py` many times to build a large dataset of stochastic multiplication results for different random factors.
- `stochastic_graphs.py` — Generates interactive HTML graphs (with draggable tables) for a single run, saved in the `single_run_graphs/` folder.
- `analyze_stochastic_results.py` — Aggregates and visualizes results from all runs in `all_stochastic_results.csv`, saving summary graphs in the `analysis_graphs/` folder.
- `all_stochastic_results.csv` — Master CSV file containing results from all runs, suitable for large-scale analysis.
- `single_run_graphs/` — Folder for HTML graphs from individual runs.
- `analysis_graphs/` — Folder for HTML graphs from cumulative analysis.

## How to Use

1. **Run a single experiment:**
   ```bash
   python sc_arith.py
   ```
   This generates `stochastic_multiplication_results.csv` and updates `all_stochastic_results.csv`.

2. **Run many experiments in batch:**
   ```bash
   python bulk_arith.py
   ```
   This will call `sc_arith.py` multiple times, building a large dataset in `all_stochastic_results.csv`.

3. **Visualize a single run:**
   ```bash
   python stochastic_graphs.py
   ```
   This creates interactive HTML graphs for the most recent run in `single_run_graphs/`.

4. **Analyze all results:**
   ```bash
   python analyze_stochastic_results.py
   ```
   This creates summary and outlier graphs for all runs in `analysis_graphs/`.

## Requirements

- Python 3.7+
- pandas
- plotly

Install requirements with:
```bash
pip install pandas plotly
```

## Features
- Simulate stochastic multiplication for random factors and various bitstream lengths
- Save and aggregate results for large-scale analysis
- Generate interactive, draggable-table HTML graphs for both single runs and cumulative data
- Identify outliers and trends in stochastic computing accuracy

## License
MIT License

## Author
[Camden Larson]
