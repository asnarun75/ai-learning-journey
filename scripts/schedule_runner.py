from __future__ import annotations

from datetime import date
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.scheduler import schedule_daily
from scripts.daily_run import run_for_date


def job() -> None:
    run_for_date(date.today())


if __name__ == "__main__":
    schedule_daily(job)
