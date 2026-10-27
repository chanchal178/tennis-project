"""
Master ETL Orchestrator & CLI Runner for Tennis Analytics Explorer.
Supports --init-db, --all, --competitions, --complexes, --rankings, and --test-conn.
Ensures zero-crash execution, helpful configuration diagnostics, and repeatable runs.
"""

import sys
import argparse
import logging
from datetime import datetime
from db import check_connection, init_db, sanitize_database_url
from config import DATABASE_URL, SPORTRADAR_API_KEY
from etl_competitions import run_competitions_etl
from etl_complexes import run_complexes_etl
from etl_rankings import run_rankings_etl

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def print_banner():
    print("""
====================================================================
           TENNIS ANALYTICS EXPLORER - ETL PIPELINE
                 Sportradar API & SQL Database
====================================================================
""")

def run_diagnostics():
    """Runs connection and environment checks."""
    logger.info(f"Target Database URL: {sanitize_database_url(DATABASE_URL)}")
    if not SPORTRADAR_API_KEY or SPORTRADAR_API_KEY == "your_sportradar_api_key_here":
        logger.warning("No Sportradar API key configured. ETL will automatically use bundled reference datasets.")
    else:
        logger.info("Sportradar API Key detected. Live API fetching enabled.")

    success, msg = check_connection()
    if success:
        logger.info(f"DB Status: OK ({msg})")
    else:
        logger.error(f"DB Status: FAILED ({msg})")
        logger.error("Please verify your DATABASE_URL in .env (or configure PostgreSQL/MySQL/SQLite).")
    return success

def run_all_etl(init_first: bool = False):
    """Executes the complete pipeline in correct dependency order."""
    if init_first:
        logger.info("Initializing schema tables, views, and indexes...")
        init_ok, init_msg = init_db()
        if not init_ok:
            logger.error(f"Schema initialization failed: {init_msg}")
            return False
        logger.info(f"Schema status: {init_msg}")

    start_time = datetime.now()
    results = {}

    # 1. Competitions & Categories
    logger.info("--- Step 1/3: Competitions & Categories ---")
    results["competitions"] = run_competitions_etl()

    # 2. Complexes & Venues
    logger.info("--- Step 2/3: Complexes & Venues ---")
    results["complexes"] = run_complexes_etl()

    # 3. Competitors & Rankings
    logger.info("--- Step 3/3: Competitor Rankings ---")
    results["rankings"] = run_rankings_etl()

    elapsed = (datetime.now() - start_time).total_seconds()

    print("\n" + "=" * 60)
    print(f"ETL Execution Summary (Completed in {elapsed:.2f}s)")
    print("=" * 60)
    all_success = True
    for pipeline, res in results.items():
        status = "SUCCESS" if res.get("success") else "FAILED"
        if not res.get("success"):
            all_success = False
        data_source = "LIVE API" if res.get("is_live") else "REFERENCE"
        print(f" * {pipeline.capitalize():<15}: [{status}] [{data_source}] {res.get('message')}")
    print("=" * 60 + "\n")

    return all_success

def main():
    print_banner()
    parser = argparse.ArgumentParser(description="Tennis Analytics ETL Runner")
    parser.add_argument("--init-db", action="store_true", help="Initialize database tables, views, and indexes from schema.sql")
    parser.add_argument("--test-conn", action="store_true", help="Test database connection and verify configuration")
    parser.add_argument("--all", action="store_true", help="Run database initialization and all ETL pipelines")
    parser.add_argument("--competitions", action="store_true", help="Run only Competitions ETL")
    parser.add_argument("--complexes", action="store_true", help="Run only Complexes & Venues ETL")
    parser.add_argument("--rankings", action="store_true", help="Run only Rankings ETL")

    args = parser.parse_args()

    # Default action if no flags provided: show diagnostics and prompt
    if not any([args.init_db, args.test_conn, args.all, args.competitions, args.complexes, args.rankings]):
        logger.info("No specific option chosen. Checking diagnostics and running full ETL (--all)...")
        args.all = True

    if args.test_conn:
        ok = run_diagnostics()
        sys.exit(0 if ok else 1)

    if args.init_db and not args.all:
        logger.info("Testing database connection before schema initialization...")
        if not check_connection()[0]:
            logger.error("Cannot connect to database. Please inspect your .env DATABASE_URL.")
            sys.exit(1)
        ok, msg = init_db()
        if ok:
            logger.info(f"Database Initialization Succeeded: {msg}")
            sys.exit(0)
        else:
            logger.error(f"Database Initialization Failed: {msg}")
            sys.exit(1)

    if args.all:
        conn_ok, _ = check_connection()
        if not conn_ok:
            logger.error("Cannot connect to database. Please check your .env configuration.")
            sys.exit(1)
        ok = run_all_etl(init_first=True)
        sys.exit(0 if ok else 1)

    # Selective pipelines
    conn_ok, _ = check_connection()
    if not conn_ok:
        logger.error("Cannot connect to database. Please check your .env configuration.")
        sys.exit(1)

    if args.competitions:
        res = run_competitions_etl()
        sys.exit(0 if res.get("success") else 1)

    if args.complexes:
        res = run_complexes_etl()
        sys.exit(0 if res.get("success") else 1)

    if args.rankings:
        res = run_rankings_etl()
        sys.exit(0 if res.get("success") else 1)

if __name__ == "__main__":
    main()
