from datetime import datetime


def now():
    return datetime.utcnow()


def format_datetime(t):
    return t.strftime('%Y-%m-%d %H:%M:%S')


def human_readable(delta):
    dt = delta.total_seconds()

    if abs(dt) < 60:
        return round(dt), 'seconds'
    elif abs(dt) < 3600:
        return round(dt / 60), 'minutes'
    elif abs(dt) < 86400:
        return round(dt / 3600), 'hours'
    else:
        return round(dt / 86400), 'days'
