# Used Car Optimizer

Used Car Optimizer is a small Python project for ranking used-car listings by payment fit, cargo usefulness, reliability, and ownership risk. It is built for a practical shopping workflow: paste listings into a CSV, run the optimizer, and review both a ranked spreadsheet-style output and a plain-English markdown summary.

## What It Does

- Reads a CSV of used-car listings.
- Estimates out-the-door cost with tax and fees.
- Estimates monthly payment after a down payment.
- Applies APR penalties for older and high-mileage vehicles.
- Scores each listing across affordability, financing friendliness, age, mileage, model reputation, cargo value, and history risk.
- Writes a ranked CSV and a markdown report you can read without opening a spreadsheet.

## Project Layout

```text
used-car-optimizer/
|-- README.md
|-- Project_Notes.md
|-- requirements.txt
|-- config.json
|-- car_optimizer.py
|-- data/
|   |-- sample_cars.csv
|   |-- sample_cars_ranked.csv
|   `-- used_car_optimizer.xlsx
|-- output/
|-- src/
|   `-- used_car_optimizer/
|       |-- __init__.py
|       |-- cli.py
|       |-- config.py
|       |-- finance.py
|       |-- loader.py
|       |-- models.py
|       |-- reporting.py
|       `-- scoring.py
`-- tests/
    |-- test_finance.py
    |-- test_loader.py
    `-- test_scoring.py
```

## Quick Start

1. Install Python 3.11 or newer.
2. Open this project folder in a terminal.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the optimizer on the sample file:

```bash
python car_optimizer.py --input data/sample_cars.csv
```

5. Open the generated files in `output/`.

## CSV Format

The optimizer expects a CSV with columns like:

```text
year, make, model, trim, price, mileage, body_style, cargo_cuft, vin, accidents, owners, prior_use, title_status
```

It also accepts the legacy starter columns from the original script, such as `rental_fleet`, `title_issue`, and `model_key`. Missing optional columns are filled with safe defaults.

## Configuration

All main assumptions live in `config.json`. You can adjust:

- monthly budget
- down payment
- loan term
- base APR
- APR penalties
- tax rate
- DMV and dealer fees
- preferred body styles
- model reputation scores

## Adding Cars

1. Copy `data/sample_cars.csv`.
2. Paste your new listings into the file.
3. Keep one car per row.
4. Use plain numbers for price and mileage when possible.
5. For history details, use simple values like `clean`, `salvage`, `rental`, or `lease`.

## Understanding The Output

The ranked CSV is best for sorting and filtering.

The markdown report is best for fast review:

- `Strong fit` means the car scores well overall and is close to your preferences.
- `Borderline` means it may still be worth checking, but there are tradeoffs.
- `Pass` means it is likely too risky, too expensive, or too weak a fit.

The score is not a promise that a car is good. It is a decision aid that helps compare options consistently.

## Running Tests

```bash
pytest
```

If you do not want to install `pytest`, the tests can also be adapted to Python's built-in `unittest` runner later.

## First-Version Scope

This version keeps things simple on purpose:

- no scraping
- no live lender quotes
- no VIN decoding API
- no dealership integration

That keeps the tool easier to trust, inspect, and modify.
