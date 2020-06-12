from random import randint
import datetime as dt

tday = dt.date.today()
now = dt.datetime.now()
td = dt.timedelta(days=31)

thisYear = str(tday.year)
thisMonth = str(tday.month)
thisDate = str(tday.day)
thisHour = str(now.hour)
thisMinute = str(now.minute)
thisSecond = str(now.second)


def accountNumber():
    rawCardNum = ''
    counter = [1, 2, 3, 4]
    for count in counter:
        rawCardNum += str(randint(1000, 9999))
        if(count != 4):
            rawCardNum += '-'

    return rawCardNum


def regNumber():
    rawCardNum = ''
    counter = [1, 2, 3]
    for count in counter:
        rawCardNum += str(randint(100, 999))
    return rawCardNum


def transID():
    return 'TRID' + thisYear + thisMonth + thisDate + '-' + thisHour + ':' + thisMinute


def getMyDate():
    return thisYear + '-' + thisMonth + '-' + thisDate


def getMyTime():
    return thisHour + ':' + thisMinute


def getMySec():
    return thisSecond


def getMyDatePlusMonth():
    return str(tday+td)
