#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      srinath.h
#
# Created:     13/05/2012
# Copyright:   (c) srinath.h 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import datetime

def get_full_day_datetime_range(curdatetime):
    startdatetimerange = datetime.datetime.combine(curdatetime.date(),datetime.time(0,0,0))
    enddatetimerange = datetime.datetime.combine(curdatetime.date(),datetime.time(23,59,59))
    return (startdatetimerange,enddatetimerange)

def get_full_week_datetime_range(curdatetime):
    weekstuff = {6:(0,6),0:(-1,5),1:(-2,4),2:(-3,3),3:(-4,2),4:(-5,1),5:(-6,0)}
    curdate = curdatetime.date()
    curweekday = curdate.weekday()
    startdatetimerange = datetime.datetime.combine(curdate+datetime.timedelta(weekstuff[curweekday][0]),datetime.time(0,0,0))
    enddatetimerange =datetime.datetime.combine(curdate+datetime.timedelta(weekstuff[curweekday][1]),datetime.time(23,59,59))
    return(startdatetimerange,enddatetimerange)

def get_full_month_datetime_range(curdatetime):
    curmonth = curdatetime.month
    newmonth = curmonth
    wrkdatetime = curdatetime
    td = datetime.timedelta(1)

    while(newmonth==curmonth):
        wrkdatetime += td
        newmonth = wrkdatetime.month

    wrkdatetime -= td
    lastdate = wrkdatetime.day
    curyear = curdatetime.year

    startdatetimerange = datetime.datetime.combine(datetime.date(curyear, curmonth,1),datetime.time(0,0,0))
    enddatetimerange = datetime.datetime.combine(datetime.date(curyear,curmonth,lastdate),datetime.time(23,59,59))
    return(startdatetimerange,enddatetimerange)
