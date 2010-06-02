"""
    Proxy service over Dbus for
    Musicbrainz's webservice API
    
    @author: jldupont
    @date: May 28, 2010
"""
import os
import sys

## For development environment
ppkg=os.path.abspath( os.getcwd() +"/app")
if os.path.exists(ppkg):
    sys.path.insert(0, ppkg)

import gobject
import dbus.glib
from dbus.mainloop.glib import DBusGMainLoop

gobject.threads_init()
dbus.glib.init_threads()
DBusGMainLoop(set_as_default=True)


from app.system import mswitch
from app.agents import adbus
from app.agents import cache
from app.agents import mb
from app.agents import logger
#from app.agents import test

from app.agents import ui

import gtk
gtk.main()