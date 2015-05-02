# FullScreenWrapper2 Framework #
FullScreenWapper2 is a GUI Framework for developing full screen apps using the [FullScreenUI API](http://code.google.com/p/android-scripting/wiki/FullScreenUI) functions provided by SL4A in Python. This lets you design a  look & feel similar to Android Java apps using the same XML Layouts and let you respond to View events.

It is a significant (**non-backward compatible**) enhancement over [FullScreenWrapper](http://code.google.com/p/python-for-android/wiki/FullScreenWrapper) that attempts to make programming using FullScreenUI as simple as programming in standard GUI Frameworks.

<font color='red'>Update:</font>**A working [Python3 compatible version](http://python-for-android.googlecode.com/hg/sl4atools/fullscreenwrapper2/py3/fullscreenwrapper2_py3.py) is now available - could do with more testing.**

## Features ##
  * An FullScreenWrapper2App class that manages the eventloop & a layout stack enabling easy parent->child->parent transitions
  * EventHandler classes with event-matching functions pre-built for standard View events like **click**,**itemclick**(ListView) and **key**
  * Device Sensors & other similar SL4A/Custom events can also be caught & managed using the same eventloop + EventHandler class
  * Object like access to a layout's views and properties (ie. MainLayout.views.txt\_label.background = "#FFAA00AA")

![http://python-for-android.googlecode.com/files/fullscreenwrapper2.png](http://python-for-android.googlecode.com/files/fullscreenwrapper2.png)

## Demo Screenshots ##
![http://python-for-android.googlecode.com/files/fullscreenwrapper2_demo_screenshots.png](http://python-for-android.googlecode.com/files/fullscreenwrapper2_demo_screenshots.png)

## Download ##
You can find [FullScreenWrapper2 files](http://code.google.com/p/python-for-android/source/browse/sl4atools/fullscreenwrapper2/) under the sl4atools directory in the Python for Android repository.
  1. **[fullscreenwrapper2.py](http://code.google.com/p/python-for-android/source/browse/sl4atools/fullscreenwrapper2/fullscreenwrapper2.py)** is the main file you need to import
  1. <font color='red'>Update:</font>**A working [Python3 compatible version](http://python-for-android.googlecode.com/hg/sl4atools/fullscreenwrapper2/py3/fullscreenwrapper2_py3.py) is now available - could do with more testing.
  1.**[API Docs](http://python-for-android.googlecode.com/hg/sl4atools/fullscreenwrapper2/docs.zip)**generated from docstrings are available
  1. The following FullScreenWrapper2 examples are available
    ***[Simple Demo](http://code.google.com/p/python-for-android/source/browse/sl4atools/fullscreenwrapper2/examples/fullscreenwrapper2demo/fullscreenwrapper2demo.py)**to show basic usage of the Framework
    ***[Gyroscope Sensor](http://code.google.com/p/python-for-android/source/browse/sl4atools/fullscreenwrapper2/examples/gyro_sl4a_test/gyro_sl4a_test.py)**tilting example to show how FullScreenWrapper2 EventHandler classes can be used to catch SL4A events & use them in your User Interface
    ***[A Full App](http://code.google.com/p/python-for-android/source/browse/sl4atools/fullscreenwrapper2/examples/calcount2_example.zip)**(a calorie counter) that has parent & child layouts, resources & layouts being loaded from files, database access etc.
  1. A zip file with**[everything](http://code.google.com/p/python-for-android/source/browse/sl4atools/fullscreenwrapper2/fullscreenwrapper2_everything.zip)**is available**

## How to Use Guide ##
#### 1. Import fullscreenwrapper2 & define your layout class ####
First place fullscreenwrapper2.py in the same folder as your script. You start by importing everything from fullscreenwrapper2 & inheriting a class for your own layout from the Layout class and calling **init** function of Layout using **super** keyword with the XML Layout (string) and the Screen Title (string).
```
from fullscreenwrapper2 import *

class DemoLayout(Layout):
    def __init__(self):
        super(DemoLayout,self).__init__(xmldata,"FullScreenWrapper Demo")
```

#### 2. Define **on\_show()** and **on\_close()** functions ####

The **on\_show()** function is **very important** as your views become accessible through the FullScreenWrapper2 framework **ONLY AFTER** on\_show() is called by the framework. This is the place where you initialize / set the values of your views & setup event handlers. If you're having parent->child layouts, on\_show() is also called when a child layout closes & the parent layout comes back on.

Views & their properties can be accessed via **Layout.views.view\_id.property**. In the example below, we're setting the background color - most simple properties should work without a hitch.

Both the Layout & the individual Views can have events associated with them. You would typically use **click\_EventHandler** & **itemclick\_EventHandlers** (for ListView) with Views. The **init** for these take the View itself & an event handler function reference to call when the event occurs as parameters.

You would typically associate **key\_EventHandler** with the layout itself. The **init** for key\_EventHandler takes a key\_match\_id (defaults to "4" which is the back key), a view (defaults to None) and an event handler function reference as parameters.

```
    def on_show(self):
        self.add_event(key_EventHandler(handler_function=self.close_app))
        self.views.but_change.add_event(click_EventHandler(self.views.but_change, self.change_color))
        self.views.but_exit.add_event(click_EventHandler(self.views.but_exit, self.close_app))
        self.views.txt_colorbox.background="#ffffffff"

```

For Sensor events like Gyroscope, you can directly use the EventHandler class - just set

You can access a view's properties  Layout.views.view\_id.property

```
    def on_show(self):
        self.add_event(key_EventHandler(handler_function=self.close_app))
        self.views.but_change.add_event(click_EventHandler(self.views.but_change, self.change_color))
        self.views.but_exit.add_event(click_EventHandler(self.views.but_exit, self.close_app))
        self.views.txt_colorbox.background="#ffffffff"
```

The on\_close() is mainly allow you to save state before a layout dissappears if needed. You can have **pass** as the only statement.
```
    def on_close(self):
        pass
```

The restriction of views becoming accessible only after the framework calls on\_show() of a layout is because of the the way FullScreenUI works. You need to show a layout first before you can access its views. FullScreenWrapper2 uses Android.fullGetProperty() to find out which views contain an "id" and are available for access and creates & populates View objects in each layout's views collection. These View objects let you associate events with them & allow you to access properties through SL4A reflection using setattr() and getattr(). Layouts handle their events through a special view added to the views collection.

#### 3. Create your event handler functions & other functions ####
The event handler function definition signature should be as follows:
```
    def event_handler_function(self,view,event):
```
Each event handler is passed a reference to the view with which the event is associated (can be None) & the SL4A event data obtained from Android.eventPoll().result[0](0.md). In the example below, every time a button on screen is pressed, the textbox changes to a random color background.
```
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
```

#### 4. Initialize FullScreenWrapper2, Show Layout & Execute eventloop ####
Once your layout class is setup, in your main function, initialize the framework first with Android.Android(). Then show the layout using **FullScreenWrapper2App.show\_layout()** and initiate the eventloop().
```
if __name__ == '__main__':
    droid = android.Android()
    random.seed()
    FullScreenWrapper2App.initialize(droid)
    FullScreenWrapper2App.show_layout(DemoLayout())
    FullScreenWrapper2App.eventloop()
```

#### 5. Putting it together ####
The full code from above example is shown here to show how simple it all is. The full source code **[including the XML Layout](http://code.google.com/p/python-for-android/source/browse/sl4atools/fullscreenwrapper2/examples/fullscreenwrapper2demo/fullscreenwrapper2demo.py)** is also availble.

For simple XML layouts, you can just define layout in a string variable in your module. However, as your apps become more complex, you may want to load from sdcard files or even the internet.
```
import android, random
from fullscreenwrapper2 import *

class DemoLayout(Layout):
    def __init__(self):
        super(DemoLayout,self).__init__(xmldata,"FullScreenWrapper Demo")
        
    def on_show(self):
        self.add_event(key_EventHandler(handler_function=self.close_app))
        self.views.but_change.add_event(click_EventHandler(self.views.but_change, self.change_color))
        self.views.but_exit.add_event(click_EventHandler(self.views.but_exit, self.close_app))
        self.views.txt_colorbox.background="#ffffffff"
        
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

```

## License ##
This work is open source & licensed under a [Creative Commons Attribution 3.0 Unported License](http://creativecommons.org/licenses/by/3.0/deed.en_US). This is a very permissive license & you're pretty much free to use & modify any way you want (including commercial use) with attribution.

[![](http://i.creativecommons.org/l/by/3.0/88x31.png)](http://creativecommons.org/licenses/by/3.0/deed.en_US)