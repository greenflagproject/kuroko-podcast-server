#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from index_generator import FeedGenerator, FileIO
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

crontab_setting_text: str = os.environ["CRONTAB_SETTING_TEXT"]

scheduler = BlockingScheduler()
scheduler.add_job(FeedGenerator.generate, CronTrigger.from_crontab(crontab_setting_text, timezone=FileIO.timezone_info))

scheduler.start()
