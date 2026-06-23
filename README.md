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
|-- collect_listings.py
|-- data/
|   |-- sample_cars.csv
|   |-- sample_cars_ranked.csv
|   |-- incoming/
|   |   |-- browser_captures/
|   |   |-- browser_snapshots/
|   |   |-- html_snapshots/
|   |   `-- manual/
|   `-- used_car_optimizer.xlsx
|-- output/
|-- src/
|   `-- used_car_optimizer/
|       |-- __init__.py
|       |-- cli.py
|       |-- collect/
|       |   |-- __init__.py
|       |   |-- base.py
|       |   |-- browser_capture.py
|       |   |-- browser_snapshot.py
|       |   |-- cli.py
|       |   |-- dealer_com.py
|       |   |-- dealer_sources.py
|       |   |-- fetch.py
|       |   |-- manual_csv.py
|       |   |-- models.py
|       |   |-- normalize.py
|       |   |-- parsers.py
|       |   |-- pipeline.py
|       |   |-- saved_html.py
|       |   `-- time_utils.py
|       |-- config.py
|       |-- finance.py
|       |-- loader.py
|       |-- models.py
|       |-- reporting.py
|       `-- scoring.py
`-- tests/
    |-- test_collect_browser_capture.py
    |-- test_collect_browser_snapshot.py
    |-- test_collect_dealer_com.py
    |-- test_collect_parsers.py
    |-- test_collect_pipeline.py
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

## Collection Workflow

The repo now includes a first-pass dealer collection framework. It is designed to be conservative and auditable:

- it can read manual dealer CSV exports from `data/incoming/manual/`
- it can parse saved dealer HTML pages from `data/incoming/html_snapshots/`
- it writes raw audit output, cleaned normalized output, and a ready-to-score optimizer CSV

Run collection with:

```bash
python collect_listings.py
```

You can also choose how collection runs:

```bash
python collect_listings.py --mode offline
python collect_listings.py --mode live
python collect_listings.py --mode browser
python collect_listings.py --mode all
```

This writes:

- `output/collection/raw_listings.csv`
- `output/collection/normalized_listings.csv`
- `data/dealer_inventory.csv`

Then run the optimizer on the collected data:

```bash
python car_optimizer.py --input data/dealer_inventory.csv
```

### How Collection Is Structured

1. One collector per source.
2. Raw listings are preserved before cleanup.
3. Normalization standardizes price, mileage, body style, and key listing fields.
4. Deduping prefers stronger records when the same car appears more than once.
5. Only the cleaned export is fed into the optimizer.

### Why Start This Way

This first version does not jump straight into brittle live scraping. It starts with:

- local CSV imports
- saved HTML snapshots
- structured-data parsing

That gives you a trustworthy foundation before adding live dealer adapters.

### Live Dealer Collection

The first live adapter is aimed at Dealer.com-style inventory pages, which currently includes:

- Maita Subaru
- Elk Grove Honda

Example:

```bash
python collect_listings.py --mode live --dealer "Maita Subaru"
```

What live mode does:

1. Fetches the dealer inventory page with a normal browser-like request.
2. Saves the fetched HTML into `data/incoming/html_snapshots/`.
3. Extracts visible listing details conservatively.
4. Exports the cleaned result into `data/dealer_inventory.csv`.

Current limitation:

- The first live parser is intentionally lightweight and conservative.
- It is best treated as a starting adapter, not a fully hardened production scraper yet.

### Browser-Assisted Collection

For dealer sites that block simple HTTP requests, the safer fallback is browser-assisted collection.

Workflow:

1. Open the dealer inventory page in a real browser.
2. Save a structured browser capture into `data/incoming/browser_captures/`, or a rendered DOM snapshot into `data/incoming/browser_snapshots/`.
3. Run:

```bash
python collect_listings.py --mode browser --dealer "Maita Subaru"
```

Why this helps:

- the browser handles JavaScript rendering and site protections better than a plain request
- the collector still keeps an auditable text snapshot
- the same normalization and export pipeline is reused

Preferred browser capture order for Dealer.com pages:

1. Use structured listing data already embedded in the rendered page.
2. Fall back to card-level browser capture JSON if you saved that instead.
3. Only fall back to plain text snapshots when no stronger capture file exists.

This matters because text snapshots are a last resort, while structured browser captures keep price, VIN, and mileage fields much more reliably.

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

- limited dealer collection only
- no live lender quotes
- no VIN decoding API
- no dealership integration

That keeps the tool easier to trust, inspect, and modify.
