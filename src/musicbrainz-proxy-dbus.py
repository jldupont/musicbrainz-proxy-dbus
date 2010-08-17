"""
    Proxy service over Dbus for
    Musicbrainz's webservice API
    
    @author: jldupont
    @date: May 28, 2010
"""
APP_NAME="musicbrainz-proxy-dbus"
APP_ICON = "musicbrainz-proxy-dbus"
ICON_PATH="/usr/share/icons/"
ICON_FILE="musicbrainz-proxy-dbus.png"
LOG_PATH="~/musicbrainz-proxy-dbus.log"
DB_PATH ="~/musicbrainz-proxy-dbus.sqlite"
HELP_URL="http://www.systemical.com/doc/opensource/musicbrainz-proxy-dbus"
TIME_BASE=250  ##milliseconds
TICKS_SECOND=1000/TIME_BASE
       

import os
import sys

## For development environment
ppkg=os.path.abspath( os.getcwd() +"/app")
if os.path.exists(ppkg):
    sys.path.insert(0, ppkg)

import gobject
import dbus.glib
from dbus.mainloop.glib import DBusGMainLoop
import gtk

gobject.threads_init()
dbus.glib.init_threads()
DBusGMainLoop(set_as_default=True)

from app.system import mswitch

## ------------------------------
## configurables
from app.agents.tray import TrayAgent
_ta=TrayAgent(APP_NAME, ICON_PATH, ICON_FILE)

from app.agents.logger import LoggerAgent
_la=LoggerAgent(APP_NAME, LOG_PATH)
_la.start()

from app.agents.cache import CacheAgent
_ca=CacheAgent(DB_PATH)
_ca.start()

from app.agents import adbus
from app.agents import mb

from app.agents.ui import UiAgent
ui=UiAgent(HELP_URL, TICKS_SECOND)
gobject.timeout_add(TIME_BASE, ui.tick)



gtk.main()
