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
import gtk
from Queue import Queue, Empty
import webbrowser

#from Queue import Queue, Empty
        
from   app.system.base import mdispatch
import app.system.mswitch as mswitch

class UiWindow(object): #@UndefinedVariable
    
    CONTROLS=["lRequestsData",
              "lRequestsInfoData",
              "lRequestsDroppedData",
              "lMBFailedData",
              "lHitsData",
              "lMissesData",
              "lNotFoundData",
              "lFilteredData",
              "lRetriesDroppedData",
              "lTotalRecordsData",
              "lRecordsWithMbidData",
              "lJobQueueData",
              "lJobInfoQueueData"
              ]
    
    def __init__(self, glade_file, help_url):
        self.help_url=help_url
        
        self.builder = gtk.Builder()
        self.builder.add_from_file(glade_file)
        self.window = self.builder.get_object("ui_window")

        for ctl in self.CONTROLS:
            self.__dict__[ctl]=self.builder.get_object(ctl)
        
        self.bHelp=self.builder.get_object("bHelp")
        self.bHelp.connect("clicked", self.on_help)
        
        self.window.connect("destroy-event", self.do_destroy)
        self.window.connect("destroy",       self.do_destroy)
        self.window.present()
        
    def on_help(self, *_):
        print "ui.window: help"
        webbrowser.open(self.help_url)
        
    def do_destroy(self, *_):
        print "ui.window: destroy"
        mswitch.publish(self, "__destroy__")
        
    def updateAll(self, data):
        for ctl, value in data.iteritems():
            self.__dict__[ctl].set_text(str(value))
        
    def update(self, param, value):
        ctl=self.__dict__[param]
        ctl.set_text(str(value))
        


### ================================================================================
### ================================================================================


    
class UiAgent(object):
    def __init__(self, help_url, ticks_seconds):
        self.ticks_seconds=ticks_seconds
        
        path=os.path.dirname(__file__)
        self.glade_file=path+"/ui.glade"       
        
        self.help_url=help_url
        self.iq=Queue()
        self.isq=Queue()
        
        mswitch.subscribe(self.iq, self.isq)
        self.tick_count=0
        self.window=None
        
        self.data={}

    def h___show__(self, *_):
        """ We should show the main application window
        """
        print "ui.agent: show"
        if self.window is None:
            print "ui.agent: create window"
            self.window=UiWindow(self.glade_file, self.help_url)
        try:  self.window.updateAll(self.data)
        except:
            print "ui.agent: show: retry"
            self.window=None
            self.pub("__show__")

    def h___destroy__(self, *_):
        """ Seems that the application window was closed...
        """
        print "ui.agent: destroy"
        self.window=None


    def h_filtered(self, *_):
        self._iu("lFilteredData")  
        
    def h_job_queues(self, todo, info):
        self.data["lJobQueueData"]=todo
        self.data["lJobInfoQueueData"]=info
        
        try:    
            self.window.update("lJobQueueData", todo)
            self.window.update("lJobInfoQueueData", info)
        except: pass

    def h_cache_stats(self, ctotal_records, ctotal_records_mbid):
        self.data["lTotalRecordsData"]=ctotal_records
        self.data["lRecordsWithMbidData"]=ctotal_records_mbid

        try:    
            self.window.update("lTotalRecordsData", ctotal_records)
            self.window.update("lRecordsWithMbidData", ctotal_records_mbid)
        except: pass
        
    def hq_track(self, ref, _artist, _track, priority):
        if priority=="low":
            self._iu("lRequestsInfoData") 
        else:
            self._iu("lRequestsData")            
        
    def h_mb_queue_full(self, *_):
        self._iu("lRequestsDroppedData")        

    def h_mb_retry_dropped(self, *_):
        self._iu("lRetriesDroppedData")

    def _iu(self, param):
        d=self.data.get(param, 0)+1
        self.data[param]=d
        self._u(param, d)

    def _u(self, param, d):
        try:    self.window.update(param, d)
        except: pass

    def h_tracks(self, source, _ref, tracks):
        """
        For computing the 'hits' and 'misses'
        """
        track=tracks[0]
        
        try:    track_mbid=track["track_mbid"]
        except: track_mbid=None
        
        if source=="mb":
            if track is None or track_mbid is None or track_mbid=="":
                self._iu("lNotFoundData")
                return
        
        #print "ui.h_track: ", source, _ref, track
        if source == "cache":
            if track_mbid!="" and track_mbid is not None:
                self._iu("lHitsData")                
            else:
                self._iu("lMissesData")   

                
    def h_cache_miss(self, *_):
        self._iu("lMissesData")
        
    def h_mb_error(self, *_):
        self._iu("lMBFailedData")
    
    def h_app_exit(self, *_):
        self.on_destroy()

    def on_destroy(self):
        gtk.main_quit()
    
    def tick(self, *_):
        """
        Performs message dispatch
        """
        
        tick_second = (self.tick_count % self.ticks_seconds) == 0 
        self.tick_count += 1
        
        #print "tick! ", tick_second
        
        mswitch.publish("__main__", "tick", self.ticks_seconds, tick_second)
        
        while True:
            try:     
                envelope=self.isq.get(False)
                quit, mtype, handled=mdispatch(self, "__main__", envelope)
                if handled==False:
                    mswitch.publish(self.__class__, "__interest__", (mtype, False, self.isq))
                if quit:
                    self.on_destroy()
                    
            except Empty:
                break
            continue            
        
        burst=5
        
        while True:
            try:     
                envelope=self.iq.get(False)
                quit, mtype, handled=mdispatch(self, "__main__", envelope)
                if handled==False:
                    mswitch.publish(self.__class__, "__interest__", (mtype, False, self.iq))
                if quit:
                    self.on_destroy()
                    
                burst -= 1
                if burst == 0:
                    break
            except Empty:
                break
            
            continue

        return True
    
"""
ui=UiAgent(HELP_URL, TICKS_SECONDS)
gobject.timeout_add(TIME_BASE, ui.tick)
"""

