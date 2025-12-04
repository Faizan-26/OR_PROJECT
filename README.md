# PP Chemicals - Operations Research Problem Solver

A desktop application for solving Operations Research problems including:

- **Linear Programming** (Simplex Method with Sensitivity Analysis)
- **Assignment Problems** (Hungarian Algorithm)
- **Transportation Problems** (VAM + MODI Method)

## Features

### Linear Programming (Simplex)

- Support for 10+ decision variables and 10+ constraints
- Maximize or minimize objective functions
- Sensitivity analysis with shadow prices and reduced costs
- Allowable ranges for RHS and objective coefficients

### Assignment Problem

- 10x10 or larger cost/efficiency matrices
- Maximize efficiency or minimize cost
- Hungarian Algorithm for optimal assignment
- Visual assignment matrix display

### Transportation Problem

- 10x10 or larger supply-demand matrices
- Three initial solution methods: VAM, Least Cost, NW Corner
- MODI optimization for optimal solution
- Handles balanced and unbalanced problems

## Installation

1. Make sure you have Python 3.8+ installed

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python main.py
```

## Project Structure

```
pp_chemicals_or_solver/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
│
├── algorithms/            # OR Algorithm implementations
│   ├── simplex.py         # Simplex method with sensitivity
│   ├── assignment.py      # Hungarian algorithm
│   └── transportation.py  # VAM + MODI
│
├── models/               # Data models
│   ├── lp_model.py       # LP problem structure
│   ├── assignment_model.py
│   └── transportation_model.py
│
├── ui/                   # User interface
│   ├── app.py            # Main application window
│   ├── dashboard.py      # Home screen
│   ├── simplex_view.py   # LP input/output
│   ├── assignment_view.py
│   ├── transportation_view.py
│   └── components/       # Reusable widgets
│       ├── matrix_input.py
│       ├── result_display.py
│       └── sensitivity_table.py
│
├── utils/               # Utility functions
│   ├── validators.py    # Input validation
│   ├── formatters.py    # Output formatting
│   └── export.py        # CSV/Excel export
│
├── config/              # Configuration
│   └── settings.py      # App settings & constants
│
└── assets/             # Icons and images
```

## Usage

### PP Chemicals Context

This application is designed for PP Chemicals, a chemical manufacturing company for roads and buildings. The three OR problems correspond to:

1. **Linear Programming**: Production optimization - determining optimal production quantities for 10 chemical products (bitumen, plasticizers, coatings, etc.) subject to resource constraints

2. **Assignment Problem**: Worker-task allocation - assigning 10 workers to 10 tasks (mixing, testing, packing, etc.) based on efficiency ratings

3. **Transportation Problem**: Distribution planning - shipping chemicals from 10 plants to 10 construction sites at minimum cost

### Loading Sample Data

Each problem view includes a "Load PP Chemicals Example" button that populates sample data relevant to the chemical industry context.

## Dependencies

- customtkinter >= 5.2.0 - Modern UI framework
- numpy >= 1.24.0 - Numerical operations
- scipy >= 1.11.0 - Optimization algorithms
- pandas >= 2.0.0 - Data handling
- openpyxl >= 3.1.0 - Excel export

## License

© 2024 PP Chemicals. All rights reserved.
