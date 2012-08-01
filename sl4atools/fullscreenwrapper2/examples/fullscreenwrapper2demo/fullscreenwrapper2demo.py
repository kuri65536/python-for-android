'''
@copyright: Hariharan Srinath, 2012
@license: This work is licensed under a Creative Commons Attribution 3.0 Unported License. http://creativecommons.org/licenses/by/3.0/
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
            android:textSize="16dp"
            android:text="FullScreenWrapper2 Demo"
            android:textColor="#ffffffff"
            android:layout_weight="20"
            android:gravity="center"/>
    <TextView
            android:layout_width="fill_parent"
            android:layout_height="0px"
            android:background="#ff000000"
            android:id="@+id/txt_colorbox" 
            android:layout_weight="60"
            android:gravity="center"/>
    <LinearLayout
        android:layout_width="fill_parent"
        android:layout_height="0px"
        android:orientation="horizontal"
        android:layout_weight="20">
        <Button
            android:layout_width="fill_parent"
            android:layout_height="fill_parent"
            android:background="#ff66a3d2"
            android:text = "Random Color"
            android:layout_weight="1"
            android:id="@+id/but_change" 
            android:textSize="14dp"
            android:gravity="center"/>
        <Button
            android:layout_width="fill_parent"
            android:layout_height="fill_parent"
            android:background="#ff25567b"
            android:layout_weight="1"
            android:text = "Exit"
            android:textSize="14dp"
            android:id="@+id/but_exit" 
            android:gravity="center"/>

    </LinearLayout>
</LinearLayout>"""

import android, random
from fullscreenwrapper2 import *

class DemoLayout(Layout):
    def __init__(self):
        super(DemoLayout,self).__init__(xmldata,"FullScreenWrapper Demo")
        
    def on_show(self):
        self.add_event(key_EventHandler(handler_function=self.close_app))
        self.views.but_change.add_event(click_EventHandler(self.views.but_change, self.change_color))
        self.views.but_exit.add_event(click_EventHandler(self.views.but_exit, self.close_app))
        
    def on_close(self):
        pass
    
    def close_app(self,view,event):
        FullScreenWrapper2App.exit_FullScreenWrapper2App()

    def change_color(self,view, event):
        colorvalue = "#ff"+self.get_rand_hex_byte()+self.get_rand_hex_byte()+self.get_rand_hex_byte()
        self.views.txt_colorbox.background=colorvalue
    
    def get_rand_hex_byte(self):
        j = random.randint(0,255)
        hexrep = hex(j)[2:]
        if(len(hexrep)==1):
            hexrep = '0'+hexrep   
        return hexrep 

if __name__ == '__main__':
    droid = android.Android()
    random.seed()
    FullScreenWrapper2App.initialize(droid)
    FullScreenWrapper2App.show_layout(DemoLayout())
    FullScreenWrapper2App.eventloop()
