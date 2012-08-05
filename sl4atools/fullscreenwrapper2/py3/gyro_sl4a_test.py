'''
Created on Aug 1, 2012

@author: Admin
'''

xmldata = """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout
    android:layout_width="fill_parent"
    android:layout_height="fill_parent"
    android:background="#ff314859"
    android:orientation="vertical"
    xmlns:android="http://schemas.android.com/apk/res/android">
    <TextView
            android:layout_width="fill_parent"
            android:layout_height="0px"
            android:textSize="20dp"
            android:id="@+id/txt_logo" 
            android:text="Gyro Test"
            android:textColor="#ffffffff"
            android:layout_weight="19"
            android:gravity="center"
    />
    <LinearLayout
        android:layout_width="fill_parent"
        android:layout_height="0px"
        android:orientation="horizontal"
        android:layout_weight="27">
        <TextView
            android:layout_width="fill_parent"
            android:layout_height="fill_parent"
            android:background="#ff314859"
            android:layout_weight="1"
            android:gravity="center"/>
        <TextView
            android:layout_width="fill_parent"
            android:layout_height="fill_parent"
            android:background="#ff66a3d2"
            android:id="@+id/txt_top" 
            android:layout_weight="1"
            android:gravity="center"/>
        <TextView
            android:layout_width="fill_parent"
            android:layout_height="fill_parent"
            android:background="#ff314859"
            android:layout_weight="1"
            android:gravity="center"/>
    </LinearLayout>
    <LinearLayout
        android:layout_width="fill_parent"
        android:layout_height="0px"
        android:orientation="horizontal"
        android:layout_weight="27">
        <TextView
            android:layout_width="fill_parent"
            android:layout_height="fill_parent"
            android:background="#ff66a3d2"
            android:id="@+id/txt_left"
            android:layout_weight="1"
            android:gravity="center"/>
        <TextView
            android:layout_width="fill_parent"
            android:layout_height="fill_parent"
            android:background="#ff314859"
            android:layout_weight="1"
            android:gravity="center"/>
        <TextView
            android:layout_width="fill_parent"
            android:layout_height="fill_parent"
            android:background="#ff66a3d2"
            android:layout_weight="1"
            android:id="@+id/txt_right"
            android:gravity="center"/>
    </LinearLayout>
    <LinearLayout
        android:layout_width="fill_parent"
        android:layout_height="0px"
        android:orientation="horizontal"
        android:layout_weight="27">
        <TextView
            android:layout_width="fill_parent"
            android:layout_height="fill_parent"
            android:background="#ff314859"
            android:layout_weight="1"
            android:gravity="center"/>
        <TextView
            android:layout_width="fill_parent"
            android:layout_height="fill_parent"
            android:background="#ff66a3d2"
            android:id="@+id/txt_bottom" 
            android:layout_weight="1"
            android:gravity="center"/>
        <TextView
            android:layout_width="fill_parent"
            android:layout_height="fill_parent"
            android:background="#ff314859"
            android:layout_weight="1"
            android:gravity="center"/>
    </LinearLayout>
</LinearLayout>"""
    
import android
import math

droid = android.Android()

from fullscreenwrapper2_py3 import *

class GyroTestLayout(Layout):
    
    def __init__(self):
        super(GyroTestLayout,self).__init__(xmldata,"GyroTest")
        
    def on_show(self):
        self.add_event(key_EventHandler(handler_function=self.close_app))
        self.add_event(EventHandler("sensors", None, None, None, self.gyro))
        
        
    def on_close(self):
        pass
    
    def gyro(self,view,event):
        value = int(event["data"]["pitch"]*60.0/math.pi*2)
        #self.views.txt_logo.text = str(value)
        color, basecolor = self.get_color(abs(value))
        if value > 0:
            self.views.txt_top.background = color
            self.views.txt_bottom.background = basecolor
        else:
            self.views.txt_top.background = basecolor
            self.views.txt_bottom.background = color

        value = int(event["data"]["roll"]*60.0/math.pi*4)
        #self.views.txt_logo.text = str(value)
        color, basecolor = self.get_color(abs(value))
        if value > 0:
            self.views.txt_right.background = color
            self.views.txt_left.background = basecolor
        else:
            self.views.txt_right.background = basecolor
            self.views.txt_left.background = color

    def close_app(self,view,event):
        FullScreenWrapper2App.exit_FullScreenWrapper2App()
        
    colorvals = ["#ff66a3d2","#FF63BE7B", "#FF83C77D","#FFA2D07F", "#FFC1DA81", "#FFE0E383", "#FFFFEB84", "#FFFDD17F", "#FFFCB77A", "#FFFA9D75", "#FFF98370", "#FFF8696B"] 

    def get_color(self,value):
        value = abs(value)
        if value >59:
            value = 59
            
        if value < 0:
            value = 0
            
        return self.colorvals[int(value/5)],self.colorvals[0]
    

if __name__ == '__main__':
    FullScreenWrapper2App.initialize(droid)
    FullScreenWrapper2App.show_layout(GyroTestLayout())
    droid.startSensingTimed(1,200)
    FullScreenWrapper2App.eventloop()
