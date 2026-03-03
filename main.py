"""Main entry point for AutoDealer parser."""

import argparse
import asyncio
import time
from datetime import datetime

import schedule
from loguru import logger

from src.parser import run_parser
from src.warehouse_parser import run_warehouse_parser


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
        "--output-warehouse",
        "-ow",
        default="warehouse.csv",
        help="Output CSV path (default: warehouse.csv)",
    )
    parser.add_argument(
        "--warehouse",
        "-w",
        action="store_true",
        help="Also parse warehouse after services",
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
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Parse with headless",
    )

    args = parser.parse_args()

    if args.scheduled:
        logger.info(f"Running in scheduled mode (at {args.time})")

        def job() -> None:
            logger.info(f"Scheduled run at {datetime.now()}")
            # Always run regular parser first
            asyncio.run(run_parser(args.username, args.password, args.output, args.headless))
            # Then run warehouse parser if requested
            if args.warehouse:
                logger.info(
                    f"Starting warehouse parser with output: {args.output_warehouse}"
                )
                asyncio.run(
                    run_warehouse_parser(
                        args.username,
                        args.password,
                        args.output_warehouse,
                        args.headless,
                    )
                )

        schedule.every().day.at(args.time).do(job)

        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        logger.info(f"Starting parser with output: {args.output}")
        # Always run regular parser first
        # asyncio.run(run_parser(args.username, args.password, args.output))
        # Then run warehouse parser if requested
        if args.warehouse:
            logger.info(
                f"Starting warehouse parser with output: {args.output_warehouse}"
            )
            asyncio.run(
                run_warehouse_parser(
                    args.username,
                    args.password,
                    args.output_warehouse,
                    args.headless,
                )
            )


if __name__ == "__main__":
    main()
