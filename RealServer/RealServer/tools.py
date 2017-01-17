from django.utils import timezone
from datetime import timedelta

def nextDayOfWeekToDatetime(dt, day_of_week):
    days_of_week = ['mon', 'tue', 'wed', 'thur', 'fri', 'sat', 'sun']
    while dt.weekday() != days_of_week.index(day_of_week):
        dt+=timedelta(days=1)
    return dt