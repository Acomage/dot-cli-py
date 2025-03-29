#!/usr/bin/env python3
"""Dot: A dotfile management tool for Linux systems."""

import os
import sys
from typing import List, Optional

from dot.cli.parser import create_parser
from dot.cli.output import output_manager
from dot.core.health import health_check
from dot.utils.logger import setup_logger


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the Dot CLI tool."""
    # Setup logger
    logger = setup_logger()

    # Parse command line arguments
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Run the appropriate command
    return parsed_args.func(parsed_args)


if __name__ == "__main__":
    sys.exit(main())
