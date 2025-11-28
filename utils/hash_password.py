#!/usr/bin/env python3
from __future__ import annotations

import argparse
import getpass
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.infrastructure.adapters.argon2_password_hasher import Argon2PasswordHasher


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an Argon2 hash compatible with KeepTrack."
    )
    parser.add_argument(
        "password",
        nargs="?",
        help="Password to hash (omit to be prompted securely).",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    password = args.password or getpass.getpass("Password to hash: ")
    if not password:
        print("Password cannot be empty.", file=sys.stderr)
        return 1

    hasher = Argon2PasswordHasher()
    print(hasher.hash(password))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
