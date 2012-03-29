import android
import curses

droid = android.Android()

win=curses.initscr()
result="No result"
try:
  win.box()
  w,h=win.getmaxyx()
  win.addstr(2,2,"Curses Test %sx%s" % (w,h))
  win.addstr(10,10,"Hit a key")
  win.getch()
finally:
  curses.endwin()
  print("Result=",result)