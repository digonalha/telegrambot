from tracemalloc import start
from dateutil import parser


def days_between(startDate: str, endDate: str):
    startDate = parser.parse(startDate)
    endDate = parser.parse(endDate)
    return abs((startDate - endDate).days)


def days_between(startDate, endDate):
    if startDate.date() == endDate.date():
        return 0

    return abs((startDate - endDate).days)
