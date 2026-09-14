#!/usr/bin/env python3
"""fixbet-bot  —  Bu script'i doğrudan çalıştırmak için kullanın.

    python fixbet.py run
    python fixbet.py serve 5
"""
import sys

sys.path.insert(0, "src")

from fixbet.main import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
