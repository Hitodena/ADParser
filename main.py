"""Main entry point for AutoDealer parser."""

import argparse
import asyncio
import time
from datetime import datetime

import schedule
from loguru import logger

from src.parser import run_parser


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AutoDealer Parser")
    parser.add_argument(
        "--username", "-u", required=True, help="Login username/email"
    )
    parser.add_argument(
        "--password", "-p", required=True, help="Login password"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="output.csv",
        help="Output CSV path (default: output.csv)",
    )
    parser.add_argument(
        "--scheduled",
        "-s",
        action="store_true",
        help="Run daily at specified time",
    )
    parser.add_argument(
        "--time",
        "-t",
        default="02:00",
        help="Time for scheduled run in HH:MM format (default: 02:00)",
    )

    args = parser.parse_args()

    if args.scheduled:
        logger.info(f"Running in scheduled mode (at {args.time})")

        def job() -> None:
            logger.info(f"Scheduled run at {datetime.now()}")
            asyncio.run(run_parser(args.username, args.password, args.output))

        schedule.every().day.at(args.time).do(job)

        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        logger.info(f"Starting parser with output: {args.output}")
        asyncio.run(run_parser(args.username, args.password, args.output))


if __name__ == "__main__":
    main()
