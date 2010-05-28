"""
    @author: jldupont
    @date: May 28, 2010
"""
import os
import gobject
import gtk

#from Queue import Queue, Empty
        
#from   app.system.base import mdispatch
import app.system.mswitch as mswitch

path=os.path.dirname(__file__)
glade_file=path+"/ui.glade"
        
class UiWindow(gobject.GObject): #@UndefinedVariable
    
    def __init__(self, glade_file):
        gobject.GObject.__init__(self) #@UndefinedVariable

        self.builder = gtk.Builder()
        self.builder.add_from_file(glade_file)
        self.window = self.builder.get_object("ui_window")

        self.window.connect("destroy-event", self.on_destroy)
        self.window.connect("destroy",       self.on_destroy)
        self.window.present()
        
    def on_destroy(self, *_):
        mswitch.publish("__main__", "__quit__")
        gtk.main_quit()
        
        
ui=UiWindow(glade_file)
gtk.main()

