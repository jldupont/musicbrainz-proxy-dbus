"""
    UI Agent
    
    Messages Emitted:
    - "tick"
    - "__quit__"
    
    Messages Processed:
    - "track?"
    - "track"
    - "mb_queue_full"
    - "mb_error"
    
    Requests In      --> track?
    Requests Dropped --> mb_queue_full
    Hits             --> track from source 'cache'
    Misses           --> track from source 'mb'
    Failed           --> mb_error

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
        
TIME_BASE=250  ##milliseconds
TICKS_SECOND=1000/TIME_BASE
        
class UiWindow(gobject.GObject): #@UndefinedVariable
    
    def __init__(self, glade_file):
        gobject.GObject.__init__(self) #@UndefinedVariable

        self.iq=Queue()
        mswitch.subscribe(self.iq)
        self.tick_count=0

        self.builder = gtk.Builder()
        self.builder.add_from_file(glade_file)
        self.window = self.builder.get_object("ui_window")

        self.reqin=self.builder.get_object("lRequestsData")
        self.reqdrop=self.builder.get_object("lRequestsDroppedData")
        self.mbfailed=self.builder.get_object("lMBFailedData")
        self.hits=self.builder.get_object("lHitsData")
        self.misses=self.builder.get_object("lMissesData")

        self.window.connect("destroy-event", self.on_destroy)
        self.window.connect("destroy",       self.on_destroy)
        self.window.present()
        
        self.cRequestsIn = 0
        self.cRequestsDropped = 0
        self.cHits = 0
        self.cMisses = 0
        self.cFailed = 0
        
    def on_destroy(self, *_):
        mswitch.publish("__ui__", "__quit__")
        gtk.main_quit()


    def hq_track(self, *_):
        """
        For computing the 'requests in' counter
        """
        self.cRequestsIn += 1
        self.reqin.set_text(str(self.cRequestsIn))

    def h_mb_queue_full(self, *_):
        """
        For computing the 'requests dropped' counter
        """
        self.cRequestsDropped += 1
        self.reqdrop.set_text(str(self.cRequestsDropped)) 

    def h_track(self, source, _ref, _track):
        """
        For computing the 'hits' and 'misses'
        """
        if source == "cache":
            self.cHits += 1
            self.hits.set_text(str(self.cHits))
        else:
            self.cMisses += 1
            self.misses.set_text(str(self.cMisses))
            

    def h_mb_error(self, *_):
        """
        For computing 'failed' counter
        """
        self.cFailed += 1
        self.mbfailed.set_text(str(self.cFailed))

    def tick(self, *_):
        """
        Performs message dispatch
        """
        tick_second = (self.tick_count % TICKS_SECOND) == 0 
        
        mswitch.publish("__main__", "tick", TICKS_SECOND, tick_second)
        
        while True:
            try:     
                envelope=self.iq.get(False)
                mdispatch(self, "__main__", envelope)
            except Empty:
                break

        return True


        
ui=UiWindow(glade_file)
gobject.timeout_add(TIME_BASE, ui.tick)
gtk.main()

