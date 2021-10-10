from datetime import datetime
from enum import Enum
import os
import time
import pytz

from django.conf import settings

ROUND_START = int(os.environ['DJANGO_ROUND_START'])

ROUND_END = int(os.environ['DJANGO_ROUND_END'])

ROUND_SUBMISSION_CLOSING = int(os.environ['DJANGO_ROUND_SUBMISSION_CLOSING'])

ROUND_EMBARGO_LIFT = int(os.environ['DJANGO_ROUND_EMBARGO_LIFT'])


def get_datetime() -> datetime:
    return datetime.now(tz=pytz.timezone(settings.TIME_ZONE))


def get_millisec_time() -> int:
    return int(time.time() * 1000)


class RoundStatus(Enum):
    NOT_YET_STARTED = 0
    IN_PROGRESS = 1
    EXTRA_SUBMISSION_TIME = 2
    EMBARGO_IN_PLACE = 3
    SUBMISSION_CLOSED = 4


def get_round_status() -> RoundStatus:
    now = time.time()
    if now < ROUND_START:
        return RoundStatus.NOT_YET_STARTED
    if now < ROUND_END:
        return RoundStatus.IN_PROGRESS
    if now < ROUND_SUBMISSION_CLOSING:
        return RoundStatus.EXTRA_SUBMISSION_TIME
    if now < ROUND_EMBARGO_LIFT:
        return RoundStatus.EMBARGO_IN_PLACE
    return RoundStatus.SUBMISSION_CLOSED


def round_has_started() -> bool:
    return time.time() >= ROUND_START


def submission_is_open() -> bool:
    status = get_round_status()
    return status in (RoundStatus.IN_PROGRESS,
                      RoundStatus.EXTRA_SUBMISSION_TIME,
                      RoundStatus.EMBARGO_IN_PLACE)


def get_millisec_time_until_start() -> int:
    return int((ROUND_START - time.time()) * 1000)


def get_millisec_time_until_end() -> int:
    return int((ROUND_END - time.time()) * 1000)
