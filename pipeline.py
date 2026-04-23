"""
Hotel & Travel Data Pipeline
Usage:
    python pipeline.py --mode full         # re-download and reload everything
    python pipeline.py --mode incremental  # use cached CSV if available
"""

import argparse
import sys
from logger import get_logger
from ingest import fetch_data
from transform import clean
from load import get_connection, init_db, load, write_pipeline_log

log = get_logger("pipeline")


def run(mode: str) -> None:
    log.info(f"=== Pipeline starting | mode={mode} ===")

    conn = get_connection()
    init_db(conn)

    rows_ingested = rows_cleaned = rows_loaded = 0
    status = "success"
    error_msg = None

    try:
        # Step 1 — Ingest
        raw_df = fetch_data(mode)
        rows_ingested = len(raw_df)

        # Step 2 — Transform / Clean
        clean_df = clean(raw_df)
        rows_cleaned = len(clean_df)

        # Step 3 — Load into DB
        rows_loaded = load(clean_df, conn)

    except Exception as e:
        status = "failed"
        error_msg = str(e)
        log.error(f"Pipeline failed: {e}")

    finally:
        write_pipeline_log(conn, mode, rows_ingested, rows_cleaned, rows_loaded, status, error_msg)
        conn.close()

    if status == "failed":
        log.error("=== Pipeline finished with errors ===")
        sys.exit(1)
    else:
        log.info(f"=== Pipeline complete | ingested={rows_ingested:,} | cleaned={rows_cleaned:,} | loaded={rows_loaded:,} ===")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hotel Data Pipeline")
    parser.add_argument(
        "--mode",
        choices=["full", "incremental"],
        default="full",
        help="full = re-download everything; incremental = use cached CSV"
    )
    args = parser.parse_args()
    run(args.mode)
