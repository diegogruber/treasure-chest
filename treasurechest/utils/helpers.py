import time


def get_date_from_timestamp(timestamp: int, dt_format="%Y-%m-%d %H:%M:%S") -> str:
    date = time.strftime(dt_format, time.localtime(timestamp))
    return date
