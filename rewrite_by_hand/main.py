#!/usr/bin/env python3

import sys
from typing import List, Optional

from rewrite_by_hand.cli.parser import create_parser


def main(args: Optional[List[str]] = None) -> int:
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    return parsed_args.func(parsed_args)


if __name__ == "__main__":
    sys.exit(main())
