# Stochastic Computing for Hardware Trojan Defense

This repository contains research implementations and analysis of stochastic computing systems designed to defend against hardware trojan attacks, with comprehensive comparisons to equivalent binary architectures under the same attack conditions.

## Project Overview

Stochastic computing represents values as probabilistic bit streams, offering inherent resilience to hardware trojans due to its distributed nature. This project explores the effectiveness of stochastic computing as a defense mechanism through:

- Implementation of fundamental stochastic operations (multiplication, addition, subtraction)
- Hardware trojan insertion in both combinational and sequential circuits
- Comparative analysis between stochastic and binary implementations
- Image processing applications (Roberts edge detection) using stochastic computing
- Use of Sobol sequences for improved bitstream generation

## Repository Structure

### `simple_operations/`
Basic stochastic computing operations with comprehensive analysis:
- **`multiplication/`** - Stochastic multiplication implementations and comparisons
  - `src/` - Python implementations (binary, stochastic, with/without trojans)
  - `data/` - Experimental results in CSV format
  - `graphs/` - Visualization of error metrics and performance analysis

### `hardware_trojans/`
Hardware trojan analysis and experimental data:
- Combinational and sequential trojan implementations
- Analysis scripts for trojan impact on stochastic multiplication
- Complete experimental results datasets

### `image_processing/`
Image processing applications demonstrating stochastic computing:
- **`MATLAB/`** - MATLAB implementations of Roberts edge detection
- **`Verilog/`** - Hardware implementations (binary and stochastic versions)
- Sobol sequence bitstream generators

### `verilog_simple_operations/`
Verilog/SystemVerilog hardware implementations:
- **`addition&subtraction/`** - Binary and stochastic adder/subtractor circuits
- **`multiplication/`** - Hardware multiplier implementations
- Bitstream generators and test utilities

## Key Features

- **Multiple Comparison Methods**: Binary, stochastic with pseudo-random numbers, stochastic with Sobol sequences
- **Trojan Variants**: Both combinational and sequential hardware trojans
- **Complete Analysis Pipeline**: Data generation, processing, visualization
- **Hardware Verification**: Verilog/SystemVerilog testbenches with VCD output
- **Statistical Analysis**: Error metrics including MAE, percent error, and heatmap visualizations

## Installation

1. Clone the repository:
```bash
git clone https://github.com/camdenlarson7/stochastic_computing.git
cd stochastic_computing
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage Examples

### Running Stochastic Multiplication Analysis
```bash
cd simple_operations/multiplication/src
python analyze_stochastic_results.py
```

### Hardware Trojan Analysis
```bash
cd hardware_trojans
python combinational_trojan_sm_analysis.py
```

### Comparing All Methods
```bash
python compare_all_methods.py
```

### Verilog Simulation
```bash
cd verilog_simple_operations/multiplication
iverilog -o mul_test tb_multiplication.v multiplication.v
vvp mul_test
```

## Results

Key findings from the analysis:
- Stochastic computing shows resilience to certain hardware trojan attacks
- Sobol sequences provide improved accuracy over pseudo-random bitstreams
- Error characteristics vary with bit-width and input values
- Detailed results available in CSV files under respective directories

## Research Context

This project was developed as part of ECSE 398 coursework at Case Western Reserve University, exploring the intersection of hardware security and unconventional computing paradigms.

## Project Status

This is a completed research project. The code is maintained for reference and educational purposes.

## Authors

- Camden Larson
- William Froass
- Andrew Han