'''
Created on Jul 24, 2012

@author: Admin
'''

from caloriesdb import *
from fullscreenwrapper2 import *
import android
import caloriesdb
import datetime
import os
import pathhelpers
import sys
import time

droid = android.Android()

class AddMealScreen(Layout):
    def __init__(self):
        #initialize your class data attributes
        self._add_datetime = None
        self._add_calories = None
        #load and set your xml
        super(AddMealScreen,self).__init__(pathhelpers.read_layout_xml("addmealscreen.xml"),"Add a Meal")
        
    def on_show(self):
        curdatetime = datetime.datetime.now()
        
        self.views.add_meal_txt_date.text = curdatetime.date().isoformat()
        self.views.add_meal_txt_time.text = curdatetime.time().isoformat()[0:5]
        
        self.add_event(key_EventHandler("4", self,self.cancel ))
        self.views.but_datechange.add_event(click_EventHandler(self.views.but_datechange, self.datechange))
        self.views.but_timechange.add_event(click_EventHandler(self.views.but_timechange, self.timechange))
        self.views.but_save.add_event(click_EventHandler(self.views.but_save, self.save))
        
        self.views.but_add_40.add_event(click_EventHandler(self.views.but_add_40, self.set_calories_to))
        self.views.but_add_70.add_event(click_EventHandler(self.views.but_add_70, self.set_calories_to))
        self.views.but_add_100.add_event(click_EventHandler(self.views.but_add_100, self.set_calories_to))
        self.views.but_add_120.add_event(click_EventHandler(self.views.but_add_120, self.set_calories_to))
        self.views.but_add_150.add_event(click_EventHandler(self.views.but_add_150, self.set_calories_to))
        self.views.but_add_180.add_event(click_EventHandler(self.views.but_add_180, self.set_calories_to))
        self.views.but_add_200.add_event(click_EventHandler(self.views.but_add_200, self.set_calories_to))
        self.views.but_add_250.add_event(click_EventHandler(self.views.but_add_250, self.set_calories_to))
        self.views.but_add_300.add_event(click_EventHandler(self.views.but_add_300, self.set_calories_to))
        self.views.but_add_350.add_event(click_EventHandler(self.views.but_add_350, self.set_calories_to))
        self.views.but_add_400.add_event(click_EventHandler(self.views.but_add_400, self.set_calories_to))
        self.views.but_add_450.add_event(click_EventHandler(self.views.but_add_450, self.set_calories_to))
    
    def on_close(self):
        pass
        
    def cancel(self,view,eventdata):
        FullScreenWrapper2App.close_layout()
    
    def datechange(self, view, eventdata):
        curdateentry = self.views.add_meal_txt_date.text
        droid = FullScreenWrapper2App.get_android_instance()
        droid.dialogCreateDatePicker(int(curdateentry[:4]),int(curdateentry[5:7]),int(curdateentry[8:10]))
        droid.dialogShow()
        response=droid.dialogGetResponse().result
        droid.dialogDismiss()
        cur = datetime.date(response["year"],response['month'],response['day'])
        self.views.add_meal_txt_date.text = cur.isoformat()
        
    
    def timechange(self,view,eventdata):
        curtimeentry = self.views.add_meal_txt_time.text
        droid = FullScreenWrapper2App.get_android_instance()
        droid.dialogCreateTimePicker(int(curtimeentry[0:2]),int(curtimeentry [3:5]),True)
        droid.dialogShow()
        response=droid.dialogGetResponse().result
        droid.dialogDismiss()
        cur = datetime.time(response["hour"],response['minute'])
        self.views.add_meal_txt_time.text = cur.isoformat()[0:5]
        
    def save(self,view,evemtdata):
        #FullScreenWrapper2App.get_android_instance().makeToast("Save yet to be implemented")
        calstext = self.views.add_meal_txt_calories.text
        if(calstext.isdigit()):
            datetext =self.views.add_meal_txt_date.text
            adddate = datetime.date(int(datetext[0:4]),int(datetext[5:7]),int(datetext[8:10]))
            timetext =self.views.add_meal_txt_time.text
            addtime = datetime.time(int(timetext[0:2]),int(timetext[3:5]))
            adddatetime = datetime.datetime.combine(adddate,addtime)
            
            addfooditemtext = self.views.add_meal_txt_fooditem.text
            addcals = int(calstext)
            
            cals = caloriesdb.Calories()
            cals.create(mealtime = adddatetime, calories = addcals, fooditem = addfooditemtext)
            FullScreenWrapper2App.get_android_instance().makeToast("Saving")
            FullScreenWrapper2App.close_layout()
        else:
            FullScreenWrapper2App.get_android_instance().makeToast("You must enter a valid number for calories")
        
    def set_calories_to(self,view,evemtdata):
        self.views.add_meal_txt_calories.text = view.text
        #FullScreenWrapper2App.get_android_instance().makeToast("set_calories_to yet to be implemented")
    
    
class MainScreen(Layout):
    def __init__(self):
        #initialize your class data attributes
        self.max_cals_per_day = 2000
        self.show_meals_list =[]
        self.lst_view_items =[]
        self.view_day = True 
        #load & set your xml
        super(MainScreen,self).__init__(pathhelpers.read_layout_xml("main.xml"),"CalCount")

    def on_show(self):
        #initialize your layout views on screen_show
        self.views.logo.src = pathhelpers.get_drawable_pathname("logo.png")
        self.update_todays_meals_list()
        
        #setup the event handlers for your layout views        
        self.views.but_exit.add_event(click_EventHandler(self.views.but_exit, self.close_out))
        self.views.but_add.add_event(click_EventHandler(self.views.but_add,self.add_meal))
        self.views.lst_today_meals.add_event(itemclick_EventHandler(self.views.lst_today_meals, self.mealitem_click))
        self.add_event(key_EventHandler("4", self,self.close_out ))
        self.views.but_lookup.add_event(click_EventHandler(self.views.but_lookup, self.flip_today_7_days))
        
    def flip_today_7_days(self,view, eventdata):
        self.view_day = not self.view_day
        self.on_show()
        
    def on_close(self):
        pass

    def mealitem_click(self,view,eventdata):
        if not self.view_day:
            return
        
        position = int(eventdata["data"]["position"])
        FullScreenWrapper2App.get_android_instance().dialogCreateAlert("Do you want to delete the meal - "+str(self.show_meals_list[position]))
        FullScreenWrapper2App.get_android_instance().dialogSetPositiveButtonText("Yes")
        FullScreenWrapper2App.get_android_instance().dialogSetNegativeButtonText("No")
        FullScreenWrapper2App.get_android_instance().dialogShow()
        response=FullScreenWrapper2App.get_android_instance().dialogGetResponse().result
        FullScreenWrapper2App.get_android_instance().dialogDismiss()
        
        try:
            if response["which"]=="positive":
                Calories.delete_entry(self.show_meals_list[position])
        except:
            pass
                
        self.update_todays_meals_list()
        FullScreenWrapper2App.get_android_instance().makeToast("Deleting...")
        
        
    def add_meal(self,view,eventdata):
        FullScreenWrapper2App.show_layout(AddMealScreen())
        
    def close_out(self,view,event ):
        FullScreenWrapper2App.close_layout()
        
    def update_todays_meals_list(self):
        self.show_meals_list =[]
        self.lst_view_items =[]
        
        if self.view_day:
            for meal in Calories.get_meals(Calories.TimeRange.DAY):
                self.show_meals_list.append(meal)
                self.lst_view_items.append(str(meal))
                
            self.views.but_lookup.text = "Last 7 Days"
        else:
            curdate = datetime.datetime.today()
            for j in range(7):
                curdate = curdate - datetime.timedelta(j)
                cals = Calories.get_calories(Calories.TimeRange.DAY, curdate)
                text = curdate.date().isoformat() + "-"+str(cals)
                self.show_meals_list.append(text)
                self.lst_view_items.append(text)
            self.views.but_lookup.text = "Today"

        self.views.lst_today_meals.set_listitems(self.lst_view_items)
        #self.views.lst_today_meals.set_listitems(["abc","def"])

        picpercent = int(round(float(Calories.get_calories(Calories.TimeRange.DAY))/float(self.max_cals_per_day)*float(100),-1))
        self.views.todaycal.src = pathhelpers.get_drawable_pathname(str(picpercent)+".png")

        totalcals = int(round(float(Calories.get_calories(Calories.TimeRange.WEEK))/float(self.max_cals_per_day*7)*float(100),-1))
        self.views.weekcal.src = pathhelpers.get_drawable_pathname(str(totalcals)+".png")
        

if __name__ == '__main__':
    FullScreenWrapper2App.initialize(droid)
    FullScreenWrapper2App.show_layout(MainScreen())
    FullScreenWrapper2App.eventloop()
    
