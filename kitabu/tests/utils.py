import datetime


def parse_date(date_string):
    return datetime.datetime.strptime(date_string, '%Y-%m-%d')
