"""check.py: the repo's one-command check (tests + text lint). The pre-commit hook runs it.

Runs every tests/test_*.py with unittest (stdlib only, so a fresh clone needs nothing installed).
Tests that need the ROM skip themselves when rom/ is missing. Exit code is the gate.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))


def main():
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    lint_rc = 0
    if (ROOT / "tools" / "lint.py").is_file():
        import lint
        lint_rc = lint.main()
    return 0 if result.wasSuccessful() and lint_rc == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
