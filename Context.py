import datetime
import re


def get_wordle_number(date):
    # 505: Nov 6, 2022
    delta = int(re.split(' days|:| day,', str(date - datetime.date(2022, 11, 6)))[0])
    return delta + 505
    #return datetime.date.today - date

