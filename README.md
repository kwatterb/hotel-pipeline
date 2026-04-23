# Hotel & Travel Data Pipeline

An ETL pipeline that ingests hotel booking data from a public dataset, cleans and validates it with Pandas, and loads it into a normalized SQLite database.

## Structure

```
hotel-pipeline/
├── pipeline.py       # Main orchestrator — run this
├── ingest.py         # Downloads / loads raw CSV data
├── transform.py      # Cleans, validates, and normalizes data
├── load.py           # Inserts into SQLite (properties, bookings, pricing)
├── query.py          # Sample queries to inspect loaded data
├── schema.sql        # Table definitions
├── logger.py         # Shared logging config
├── requirements.txt
└── data/             # Created on first run (gitignored)
└── logs/             # Created on first run (gitignored)
```

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
# Full run — downloads fresh data and loads everything
python pipeline.py --mode full

# Incremental — skips download if data/hotels_raw.csv already exists
python pipeline.py --mode incremental
```

## Inspect Results

```bash
python query.py
```

## Data Source

[Hotel Booking Demand Dataset](https://github.com/rfordatascience/tidytuesday/blob/master/data/2020/2020-02-11/readme.md) — 119,000+ real hotel booking records (City Hotel & Resort Hotel).

## Schema

- `properties` — hotel type, country, market segment
- `bookings` — stay details, room types, guest counts, cancellation status
- `pricing` — average daily rate, parking, special requests
- `pipeline_log` — audit log of every pipeline run
