from __future__ import annotations

from datetime import datetime
from typing import Callable

from apscheduler.schedulers.blocking import BlockingScheduler
from pytz import timezone

from .config import SCHEDULE_CONFIG


def schedule_daily(job: Callable[[], None]) -> None:
    scheduler = BlockingScheduler(timezone=timezone(SCHEDULE_CONFIG.tz))
    scheduler.add_job(job, "cron", hour=SCHEDULE_CONFIG.run_hour, minute=SCHEDULE_CONFIG.run_minute)
    print(  # pragma: no cover
        f"Scheduler started for {SCHEDULE_CONFIG.tz} at {SCHEDULE_CONFIG.run_hour:02d}:{SCHEDULE_CONFIG.run_minute:02d}"
    )
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped at", datetime.now())
