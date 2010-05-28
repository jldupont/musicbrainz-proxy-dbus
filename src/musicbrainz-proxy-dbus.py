"""
    Proxy service over Dbus for
    Musicbrainz's webservice API
    
    @author: jldupont
    @date: May 28, 2010
"""
import os
import sys
import gtk

## For development environment
ppkg=os.path.abspath( os.getcwd() +"/app")
if os.path.exists(ppkg):
    sys.path.insert(0, ppkg)


import dbus.glib
import gobject              #@UnresolvedImport

gobject.threads_init()
dbus.glib.init_threads()

from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

from app.system import mswitch
from app.agents import ui


pcount=0
def idle():
    global pcount
    mswitch.publish("__idle__", "%poll", pcount)
    pcount=pcount+1
    return True

gobject.timeout_add(250, idle)
gtk.main()

