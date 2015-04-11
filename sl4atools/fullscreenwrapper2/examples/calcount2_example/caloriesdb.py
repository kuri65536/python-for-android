#-------------------------------------------------------------------------------
# Name:        caloriesdb
# Purpose:
#
# Author:      srinath.h
#
# Created:     23/05/2012
# Copyright:   (c) srinath.h 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

from peewee import *
import datetime
import datetimehelpers
import sys
import os
import os.path
import random
import pathhelpers

print pathhelpers.get_data_pathname("caloriesdb.db3")
_mydatabase = SqliteDatabase( pathhelpers.get_data_pathname("caloriesdb.db3"))
_mydatabase.connect()

class BaseDB(Model):
    class Meta:
        database = _mydatabase

class Calories(BaseDB):
    mealtime = DateTimeField()
    calories = IntegerField()
    fooditem = CharField()

    def __str__(self):
        txt =str(self.calories)+" KCal, " + self.mealtime.time().isoformat()[:5]
        if(len(self.fooditem)>0):
            txt +=", "+self.fooditem

        return txt

    class TimeRange:
        DAY = 1
        WEEK = 2
        MONTH = 3
    
    @classmethod
    def delete_entry(self,meal):
        delquery = self.delete().where(Q(mealtime=meal.mealtime)&Q(calories=meal.calories))
        delquery.execute()

    @classmethod
    def _get_date_time_range(self,timerange,ref_datetime):
        if(timerange==self.TimeRange.DAY):
            return datetimehelpers.get_full_day_datetime_range(ref_datetime)
        elif(timerange==self.TimeRange.WEEK):
            return datetimehelpers.get_full_week_datetime_range(ref_datetime)
        elif(timerange==self.TimeRange.MONTH):
            return datetimehelpers.get_full_month_datetime_range(ref_datetime)
        else:
            raise AttributeError("The timerange specified must be one of TimeRange.DAY, TimeRange.WEEK, TimeRange.MONTH")

    @classmethod
    def get_meals(self, timerange, ref_datetime=datetime.datetime.now()):
        startdatetime,enddatetime = self._get_date_time_range(timerange,ref_datetime)
        return self.select().where(Q(mealtime__gte=startdatetime) & Q(mealtime__lte=enddatetime)).order_by(('mealtime', 'desc'))

    @classmethod
    def get_calories(self, timerange, ref_datetime=datetime.datetime.now()):
        startdatetime,enddatetime = self._get_date_time_range(timerange,ref_datetime)
        ret = self.select().where(Q(mealtime__gte=startdatetime) & Q(mealtime__lte=enddatetime)).aggregate(Sum("calories"))
        if(ret == None):
            ret = 0

        return ret

    @classmethod
    def gen_testcases(self):
        for j in range(29,-1,-1):
            td = datetime.timedelta(j)
            enterdate = datetime.datetime.today().date()-td
            num_meals = random.randint(5,8)
            for k in range(num_meals):
                cal = random.randint(40,450)
                hrs = random.randint(7,23)
                mins = random.randint(1,59)
                enterdatetime = datetime.datetime.combine(enterdate,datetime.time(hrs,mins))
                self.create(mealtime = enterdatetime, calories = cal, fooditem = "", comment = "")

Calories.create_table(True)



