<p><font color='FF0000'><h2>Pls. note that this has now been superseded by <a href='http://code.google.com/p/python-for-android/wiki/fullscreenwrapper2'>FullScreenWrapper2 Framework</a></h2></font>

<h1>Introduction</h1>

With the latest updates to SL4A event facade functions that Robbie pushed over the last couple of days as the R5x18 release, I've put-together a wrapper class in Python to simplify event-oriented GUI programming using FullScreenUI - event loops and event handling etc.<br>
<br>
<h2>Description</h2>
While this still has some rough edges & not too much documentation written in, wanted to share the wrapper-class & a demo script to show what this is headed towards and also get the broader community's feed-back on approach, utility etc. First ALPHA version :-)<br>
<br>
To use the wrapper, you basically -<br>
<br>
<ol><li>Derive a class from the wrapper class which will hold your FullScreenUI view (not strictly necessary but much cleaner)<br>
</li><li>call the initialize() function to supply the xml layout and the "droid" instance<br>
</li><li>set-up the event handlers (buttons, keys, even your own events) by calling add_event_hander()<br>
</li><li>The wrapper class also generates some "pseudo-events" for "SHOW_EVENT", "HIDE_EVENT","CLOSE_EVENT", "UNHANDLED_EVENT",  "CALL_EVERY_EVENTLOOP" and "EVENT_SNIFFER" (for debugging) that the derived class can connect to the same way by add_event_handler()<br>
</li><li>call the show() function to display the layout & start the event loop<br>
</li><li>if you need to programatically set properties, the wrapper class wraps some of the <code>droid.fullSet*()</code> functions as set_property_value(), get_property_value() etc<br>
</li><li>if you want to show a child window, approach is demonstrated in the function on_but_add_click() of main_screen class in the demo. I will eventually probably move this functionality into a show_child() function<br>
</li><li>for setting ListView contents you can call set_list_contents(). Some kind of gotcha in terms of not being able to change a list once it's bound to a view - however, creating a copy of the list works as demonstrated in on_show() function of main_screen class in the demo. will probably move this in to the set_list_contents() function<br>
</li><li>In a real-life execution, you can load the XML from a file or maybe even from the web(?)</li></ol>

Would value feedback!<br>
<br>
Hariharan Srinath<br>
<br>
<h2>Download</h2>
<a href='http://code.google.com/p/python-for-android/downloads/detail?name=full_screen_ui_wrapper.py'>full_screen_ui_wrapper.py</a>

<a href='http://code.google.com/p/python-for-android/downloads/detail?name=full_screen_ui_wrapper_demo.py'>full_screen_ui_wrapper_demo.py</a>