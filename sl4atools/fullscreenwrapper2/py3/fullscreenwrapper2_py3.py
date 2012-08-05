'''
Created on Jul 19, 2012

@author: Hariharan Srinath
'''
import abc
#import android
import pickle
import json
import sys
import time
import os
import hashlib

class BaseDict(dict):
    '''
    implements a dictionary that can be accessed by BaseDict[key] as well as by BaseDict.key to allow more pythonic access
    credits: BaseDict pattern at http://code.activestate.com/recipes/473790/ under PSF license
    '''

    def __init__(self, data=None):
        if data:
            dict.__init__(self, data)
        else:
            dict.__init__(self)

    def __setattr__(self, name, val):
        if name in self.__dict__:
            self.__dict__[name]= val
        else:
            self[name] = val

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            return self[name]

    def setDict(self, name, val):
        '''
            setDict(name, val): Assign *val* to the key *name* of __dict__.
            >>> bd.setDict('height', 160)
            {}
            >>> bd.getDict()['height']
            160
            '''
        self.__dict__[name] = val
        return self

    def getDict(self):
        '''
            Return the internal __dict__.
            >>> bd.setDict('height', 160)
            {}
            >>> bd.getDict()['height']
            160
            '''
        return self.__dict__

    def setItem(self, name, val):
        '''
            Set the value of dict key *name* to *val*. Note this dict
            is not the __dict__.
        '''
        self[name] = val
        return self

    def __getstate__(self):
        ''' Needed for cPickle in .copy() '''
        return self.__dict__.copy()

    def __setstate__(self,dict):
        ''' Needed for cPickle in .copy() '''
        self.__dict__.update(dict)

    def copy(self):
        '''
            Return a copy.
        '''
        return pickle.loads(pickle.dumps(self))


class EventHandler(object):
    '''
    Defines an SL4A event handler and provides a matching function to compare vs. Android.eventPoll().result

    SL4A eventdata returned by Android.eventWait() or Android.eventPoll().result in general take the form of a dict:
    {"data":{"attribute1":value,"attribute2":value}, "name":"event_name", "time":eventtime}

    The EventHandler object consists of an event_name, a compare_attribute to look for within the "data" dict & a
    compare_value which the compare_attribute will get matched against. It also has optionally an event_handler_fn
    which stores a reference to the method to be called and the reference to the view referred to by the event.

    fullscreenwrapper2 module pre-defines click_EventHandler, itemclick_EventHandler and key_EventHandler which are
    commonly used with Layout views for your convenience

    When the FullScreenWrapper2App class which handles events finds a match, it will call the function defined in the
    EventHandler passing the view & a copy of the eventdata. The event handler method signature should therefore be:
    def event_handler_function(self, view, eventdata):
    '''

    def __init__(self,event_name, compare_attribute,compare_value,view = None, handler_function=None):
        '''
        creates an SL4A event handler

        SL4A eventdata returned by Android.eventWait() or Android.eventPoll().result in general take the form of a dict:
        {"data":{"attribute1":value,"attribute2":value}, "name":"event_name", "time":eventtime}

        The EventHandler object consists of an event_name, a compare_attribute to look for within the "data" dict & a
        compare_value which the compare_attribute will get matched against. It also has optionally an event_handler_fn
        which stores a reference to the method to be called and the reference to the view referred to by the event.

        The compare_attribute can be None. if this is the case, then the event_name alone is matched. You can use this feature
        to catch other SL4A API events like sensor events
        '''
        self.view = view
        self.event_name = event_name
        self.compare_attribute = compare_attribute
        self.compare_value = compare_value
        self.event_handler_fn = handler_function

    def match_event_data(self, event_data):
        '''
        Provides a matching function to compare event handler vs. data returned by Android.eventPoll().result or Android.eventWait()

        SL4A eventdata returned by Android.eventWait() or Android.eventPoll().result in general take the form of a dict:
        {"data":{"attribute1":value,"attribute2":value}, "name":"event_name", "time":eventtime}

        The function first matches event_data[event_name] and then tries to match event_data["data"][compare_attribute] to compare_value
        returns True on match, False on no-match or event not found

        The compare_attribute can be None. if this is the case, then the event_name alone is matched. You can use this feature
        to catch other SL4A API events like sensor events
        '''
        try:
            if event_data["name"]==self.event_name:
                if self.compare_attribute != None:
                    if event_data["data"][self.compare_attribute]==self.compare_value:
                        return True
                else:
                    return True
        except:
            return False
        else:
            return False

    def __str__(self):
        '''
        convenience function for debugging
        '''
        return str(self.event_name)+":"+str(self.compare_attribute)+"="+str(self.compare_value)

class click_EventHandler(EventHandler):
    '''
    predefined click event handler for use with  Views

    This is the event handler to typically associate with TextView, Button, ImageView etc. You only need to pass the view to
    link the click event to & the handler function & rest of event handler initialization is handled automatically
    '''
    EVENT_NAME = "click"
    COMPARE_ATTRIBUTE = "id"

    def __init__(self,view, handler_function=None):
        '''
        predefined click event handler for use with  Views

        This is the event handler to typically associate with TextView, Button, ImageView etc. You only need to pass the view to
        link the click event to & the handler function & rest of event handler initialization is handled automatically
        '''
        super(click_EventHandler,self).__init__(self.EVENT_NAME,self.COMPARE_ATTRIBUTE,view.view_id,view,handler_function)

class itemclick_EventHandler(EventHandler):
    '''
    predefined itemclick event handler for use with  Views

    This is the event handler to typically associate with ListView. You only need to pass the ListView to link the itemclick event
    to & the handler function & rest of event handler initialization is handled automatically
    '''
    EVENT_NAME = "itemclick"
    COMPARE_ATTRIBUTE = "id"

    def __init__(self,view,handler_function=None):
        super(itemclick_EventHandler,self).__init__(self.EVENT_NAME,self.COMPARE_ATTRIBUTE,view.view_id,view,handler_function)

class key_EventHandler(EventHandler):
    '''
    predefined key event handler for use with Layout. defaults to Back Key with key_id = "4"

    This is the event handler to typically associate with a layout. You need to pass key_id to associate with (defaults to
    back key = "4") & the handler function & rest of event handler initialization is handled automatically
    '''
    EVENT_NAME = "key"
    COMPARE_ATTRIBUTE = "key"

    def __init__(self,key_match_id="4",view=None,handler_function=None):
        super(key_EventHandler,self).__init__(self.EVENT_NAME,self.COMPARE_ATTRIBUTE,key_match_id,view,handler_function)

class _internal_exit_signal():
    '''
    Internal to fullscreenwrapper2 - do not use in your programs. Used by FullScreenWrapper2App to signal the eventloop to stop.
    '''
    EVENT_NAME = "fullscreenwrapper2_internal_exit_signal"
    COMPARE_ATTRIBUTE = "id"
    '''
    the event handler in exit signal checks to ensure it is receiving exit signal from the same Process ID
    '''
    eventhandler = EventHandler(EVENT_NAME,COMPARE_ATTRIBUTE,str(os.getpid()),None,None)

    '''
    used to post exit signal to the event loop
    '''
    @classmethod
    def post_internal_exit_signal(cls):
        data = {cls.COMPARE_ATTRIBUTE:str(os.getpid())}
        FullScreenWrapper2App.get_android_instance().eventPost(cls.EVENT_NAME, json.dumps(data),True)


class View(object):
    '''
    Defines a View and provides pythonic access to its properties & a mechanism to define events.

    You don't create views yourself. They are created by FullScreenWrapper2App.show_layout() after showing the xml
    and are populated in the Layout.views which is a BaseDict => ie. a dict that allows access by both [key] and .key

    You can access a view's properties simply by Layout.views.viewname.property to get & set property. Doing this
    calls the appropriate SL4A api function like fullSetProperty()

    To add and remove events, use the View.add_event() and View.remove_event() methods. To set the contents of
    a ListView, use the View.set_listitems() method
    '''
    def __init__(self,view_id, view_type):
        '''
        View constructer called with view_id & view_type. DO NOT create a view yourself.

        Views are created by FullScreenWrapper2App.show_layout() after showing the xml and are populated
        in the Layout.views which is a BaseDict => ie. a dict that allows access by both [key] and .key
        '''
        self.view_type = view_type
        self.view_id = view_id
        self._events = {}

    def add_event(self, eventhandler):
        '''
        Used to add an EventHandler to the view.

        You would typically add one of click_EventHandler or itemclick_EventHandler (for List Views)
        to a view
        '''
        self._events[eventhandler.event_name]=eventhandler

    def remove_event(self,event_name):
        '''
        removes an event added previously by matching the event_name. Use this to temporarily disable a view's click event
        '''
        self._events.pop(event_name)

    def set_listitems(self,listitems):
        '''
        sets a list for a ListView. Takes a list of str as input
        '''
        FullScreenWrapper2App.set_list_contents(self.view_id, listitems)

    def __setattr__(self, name, value):
        '''
        This allows pythonic access to setting a View's properties by calling SL4A api

        For eg: Layout.views.viewname.color = "#FFFFFFFF"
        '''
        if name in ("view_type","view_id","_events"):
            object.__setattr__(self,name,value)
        else:
            #sys.stderr.write("calling sl4a to set name:"+str(name)+" value:"+value+"\n")
            return FullScreenWrapper2App.set_property_value(self.id, name, value)

    def __getattr__(self, name):
        '''
        This allows pythonic access to getting a View's properties by calling SL4A api

        For eg: buttontext = Layout.views.buttonname.text
        '''
        #sys.stderr.write("calling sl4a to get name:"+str(name)+"\n")
        return FullScreenWrapper2App.get_property_value(self.view_id, name)

    def __str__(self):
        '''
        str(View) will return the View.text
        '''
        try:
            return self.text
        except AttributeError:
            return None

class Layout(object, metaclass=abc.ABCMeta):
    '''
    Defines a "screen" with an xml layout that contains views. Layout is a abstract class - you MUST derive your own Layout class.

    To use a Layout, you need to first derive a class with Layout as a base class: MyLayout(Layout) and define the functions on_show(self)
    and on_close(self). in your MyLayout.__init__(), you MUST include a call to super(MyLayout,self).__init__(xml, title)

    the xml property stores the xml text. This is used by FullScreenWrapper2App.show_layout() to actually display the layout.

    The layout contains importantly a BaseDict called views. A BaseDict is a dict that allows access to members by either [key] or .key

    IMPORTANT: The views BaseDict is populated by FullScreenWrapper2App.show_layout() once the xml is displayed on the screen. Your layout's Views that have an id
    only become accessible once the xml is displayed & the Layout.on_show() function is caled by the framework. DO NOT try to access views in the __init__() and
    put all your view initialization code & event handler attachment in the on_show() function.

    The views BaseDict allows you to access & modify properties of your views & allows event based interaction. You would typically access view
    properties as Layout.views.view_id.property with the FullScreenWrapper2 framework making the appropriate SL4A api calls
    to access the property. To set events for the views, use Layout.views.view_id.add_event(EventHandler)

    The FullScreenWrapper2App actually stores layout objects in a stack allowing you to seamlessly the right parent layout on closing a child layout. This
    lets you build a natural interaction using the "back" key. Note however that every time a layout is shown, its views are created afresh & the Layout.views
    BaseDict is cleared & re-populated and the Layout.on_show() function is called. This is why you should put all your view initialization & event handler setup
    code in Layout.on_show()

    Layout.on_close method MUST also be defined - though it can simply be a 1 line function containing pass. This is called when a layout is either closed
    or a child layout is opened. This method to save state.

    Layouts also allow you to set "Layout" events through Layout.add_event() - you would typically use this for things like "back key press" or even for
    other events which are accessible through the SL4A EventFacade's event system like sensor data. For catching these events, you would typically set
    EventHandler.compare_attribute to None.

    Layout events are internally handled by adding a special "layout" view to the views collection identified by a hashtag. You should not yourself
    access this special view.
    '''

    def __init__(self,xml,title):
        '''
        creates a layout and stes its xml and title, initializes the views collection

        NOTE that this DOES NOT display the layout and the layout Views are also not populated. The special "layout" view for handling Layout
        evnets however is created here
        '''
        self.uid = hashlib.md5((str(title)+str(os.getpid())+str(time.time())).encode("utf8")).hexdigest()
        self.title = title
        self.xml = xml
        self.views = BaseDict()
        self._reset()

    def _reset(self):
        '''
        This function will clear the views collection & add the special "Layout" view
        which is used to handle layout events internally
        '''
        self.views.clear()
        #adds a dummy view representing the layout for event management
        self.views[self.uid]= View(self.uid,"Layout")

    def add_event(self, eventhandler):
        '''
        This function adds a Layout event. This event is added to the special "layout" view in the views collection
        '''
        self.views[self.uid].add_event(eventhandler)

    def remove_event(self,event_name):
        '''
        This function removes a Layout event by event name. This event is actually stored in the special "layout" view in the views collection
        '''
        self.views[self.uid].remove_event(event_name)

    @abc.abstractmethod
    def on_show(self):
        '''
        The on_show method is called after your layout is displayed to allow you to initialize your layout's views' attributes & setup event handlers.

        on_show is an abstract method which MUST be defined in the your layout class. FullScreenWrapper2App.show_layout() displays the layout & populates the views BaseDict collection
        and then calls Layout.on_show() letting you do your view initializations & setup event handlers. This function is called every time a view is displayed - for eg. after a child
        layout is closed & the parent layout shown again on screen

        If you have saved state in Layout.on_close() be sure to read back state & populate data in your layout's views in on_show()
        '''
        pass

    @abc.abstractmethod
    def on_close(self):
        '''
        The on_close method MUST be defined & is called both when your layout is closed or before displaying a child layout to let you save state.

        If you're saving state here, you can read back state on on_show() method
        '''
        pass


class FullScreenWrapper2App(object):
    '''
    FullScreenWrapper2App implements the "App" incorporating an eventloop & a layout stack with methods to display & close layouts and access SL4A FullScreenUI API functions

    You SHOULD NOT instantiate a FullScreenWrapper2App but rather, simply call its class methods. To use the app, you first need to call FullScreenWrapper2App.initialize(android_instance) with the droid = android.Android()
    object that you have created in you program. This is always subsequently accessible by FullScreenWrapper2App.get_android_instance()

    You can then call FullScreenWrapper2App.show_layout() and FullScreenWrapper2App.close_layout() to show and close layouts respectively. FullScreenWrapper2App places layouts in an internal stack. This lets the framework seamlessly handle
    parent->show child->close child->show parent type of transitions simplifying your code. It also gives you a method to exit the app by calling FullScreenWrapper2App.exit_FullScreenWrapper2App() at any time. This internally works by signalling
    the eventloop to terminate the loop by posting an internal event

    the internal function called by FullScreenWrapper2App.show_layout() and close_layout() actually populates the layout's views once it is shown & also calls the Layout.on_show() function

    Once you have called show_layout() and your first layout is displayed on screen with its view properties & event handlers set, you should call FullScreenWrapper2App.eventloop() to start the event loop. The event loop will keep polling for
    the event queue and dispatch events to the appropriate handler functions

    The FullScreenWrapper also defines a few "convenience" functions which are used to set and access fullscreen properties via SL4A api calls
    '''
    _android_instance = None
    _layouts = []

    SHOW_LAYOUT_PUSH_OVER_CURRENT = 0
    SHOW_LAYOUT_REPLACING_CURRENT = 1
    _SHOW_LAYOUT_POP_CURRENT = 2


    @classmethod
    def initialize(cls, android_instance):
        '''
        You MUST call this first with your droid = android.Android() instance before calling any other function
        '''
        cls._android_instance = android_instance

    @classmethod
    def get_android_instance(cls):
        '''
        this allows you to access the android.Android() instance set in FullScreenWrapper2App.initialize() at any time
        '''
        if cls._android_instance!=None:
            return cls._android_instance
        else:
            raise RuntimeError("You need to call FullScreenWrapper2App.initialize(android_instance) first")

    @classmethod
    def show_layout(cls, layout, show_mode = SHOW_LAYOUT_PUSH_OVER_CURRENT):
        '''
        This will show the layout, set the title, clean & re-populate layout's views BaseDict collection & call the Layout.on_show()

        if the show_mode is SHOW_LAYOUT_PUSH_OVER_CURRENT (default) this will also push the layout to the top FullScreenWrapper2App._layouts[] stack.
        If there is already a parent layout showing, then this will call the parent layout's on_close() function to let the parent layout save state
        if the show_mode is SHOW_LAYOUT_REPLACING_CURRENT, then the current layout being shown will be replaced by the supplied layout
        '''

        if show_mode == cls.SHOW_LAYOUT_PUSH_OVER_CURRENT or show_mode == cls.SHOW_LAYOUT_REPLACING_CURRENT or show_mode == cls._SHOW_LAYOUT_POP_CURRENT:
            curlayoutidx = len(cls._layouts)-1

            if(curlayoutidx > -1):
                cls._layouts[curlayoutidx].on_close()

            cls.get_android_instance().fullShow(layout.xml)
            cls.get_android_instance().fullSetTitle(layout.title)

            viewsdict = cls.get_android_instance().fullQuery().result
            layout._reset()

            for viewname in iter(viewsdict):
                layout.views[viewname] = View(viewname, viewsdict[viewname]["type"])

            if show_mode == cls.SHOW_LAYOUT_PUSH_OVER_CURRENT:
                cls._layouts.append(layout)
            elif show_mode == cls.SHOW_LAYOUT_REPLACING_CURRENT:
                if(curlayoutidx > -1):
                    cls._layouts.pop()
                cls._layouts.append(layout)
            elif show_mode == cls._SHOW_LAYOUT_POP_CURRENT:
                if(curlayoutidx > -1):
                    cls._layouts.pop()

            layout.on_show()

    @classmethod
    def close_layout(cls):
        '''
        This will first call a layout's on_close() function to help save state & then close the active layout.

        If the layout being closed is a child layout, then this will pop the child layout from the FullScreenWrapper2App._layouts[] stack
        and show the parent immediately below the child layout in the stack.
        '''
        curlayoutidx = len(cls._layouts)-1

        if curlayoutidx >0:
            cls.show_layout(cls._layouts[curlayoutidx-1], cls._SHOW_LAYOUT_POP_CURRENT)
        elif curlayoutidx == 0:
            cls.get_android_instance().fullDismiss()
            cls.exit_FullScreenWrapper2App()

    @classmethod
    def exit_FullScreenWrapper2App(cls):
        '''
        convenience function to exit the app. this works by signalling the eventloop to stop
        '''
        cls.get_android_instance().fullDismiss()
        #curlayout = cls._layouts[len(cls._layouts)-1]
        #curlayout._reset()
        _internal_exit_signal.post_internal_exit_signal()

    @classmethod
    def eventloop(cls):
        '''
        The main event loop to catch & dispatch events in the active/topmost layout in the _layouts[] stack & its views.

        Call this once your first layout's event handlers are setup from your main() program. This catches & dispatches events
        by matching EventHandlers in the ACTIVE/TOPMOST layout int he _layouts[] stack & its views.

        Note that only the active layout & its views are matched with events. This function also looks for "exit" signal
        which can be raised by calling exit_FullScreenWrapper2App() to terminate the event loop.
        '''
        if len(cls._layouts)<1:
            raise RuntimeError("Trying to start eventloop without a layout visible")

        while(True):
            evt=cls.get_android_instance().eventPoll()
            if(len(evt.result)>0):
                eventdata=evt.result[0]

                #this corrects an eventpost issue where an extra "" wraps the json
                try:
                    if type(eventdata["data"]) != type({}):
                        eventdata["data"]=json.loads(eventdata["data"])
                except:
                    pass

                #sys.stderr.write("in event loop-got an event\n")
                #sys.stderr.write(str(eventdata)+"\n")

                if _internal_exit_signal.eventhandler.match_event_data(eventdata):
                    break

                curlayout = cls._layouts[len(cls._layouts)-1]

                for viewname in iter(curlayout.views):
                    view = curlayout.views[viewname]
                    #sys.stderr.write("Checking with"+ view.view_id+"\n")
                    for eventname in iter(view._events):
                        event = view._events[eventname]
                        if event.match_event_data(eventdata):
                            if event.event_handler_fn != None:
                                event.event_handler_fn(event.view, eventdata)
                                event_handled = True
                                #sys.stderr.write("found a match in view "+str(event.view.view_id))
                                break



    #Functions to manipulate contents of the FullScreen - these provide a thin cover over droid.fullset/query
    @classmethod
    def set_list_contents(cls,id, list):
        return cls.get_android_instance().fullSetList(id, list)

    @classmethod
    def set_property_value(cls,id, property, value):
        '''Set the value of an XML view's property'''
        return cls.get_android_instance().fullSetProperty(id, property,value)

    @classmethod
    def get_property_value(cls,id, property):
        '''Get the value of a given XML view's property'''
        ret = cls.get_android_instance().fullQueryDetail(id).result

        try:
            return ret[property]
        except:
            #sys.stderr.write("The property "+property+" for the view "+id+" was not found\n")
            return None
