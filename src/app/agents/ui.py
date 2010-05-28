"""
    @author: jldupont
    @date: May 28, 2010
"""
import os
import gobject
import gtk
from Queue import Queue, Empty

#from Queue import Queue, Empty
        
from   app.system.base import mdispatch
import app.system.mswitch as mswitch

path=os.path.dirname(__file__)
glade_file=path+"/ui.glade"
        
class UiWindow(gobject.GObject): #@UndefinedVariable
    
    def __init__(self, glade_file):
        gobject.GObject.__init__(self) #@UndefinedVariable

        self.iq=Queue()
        mswitch.subscribe(self.iq)

        self.builder = gtk.Builder()
        self.builder.add_from_file(glade_file)
        self.window = self.builder.get_object("ui_window")

        self.reqin=self.builder.get_object("lRequestsData")
        self.mbsuccessful=self.builder.get_object("lMBSuccessfulData")
        self.mbfailed=self.builder.get_object("lMBFailedData")
        self.hits=self.builder.get_object("lHitsData")
        self.dbentries=self.builder.get_object("lDBEntriesData")

        self.window.connect("destroy-event", self.on_destroy)
        self.window.connect("destroy",       self.on_destroy)
        self.window.present()
        
    def on_destroy(self, *_):
        mswitch.publish("__ui__", "__quit__")
        gtk.main_quit()


    def tick(self, *_):
        """
        Performs message dispatch
        """
        while True:
            try:     
                envelope=self.iq.get(False)
                mdispatch(self, "__main__", envelope)
            except Empty:
                break

        return True


        
ui=UiWindow(glade_file)
gobject.timeout_add(250, ui.tick)
gtk.main()

