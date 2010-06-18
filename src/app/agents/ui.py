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
        self.isq=Queue()
        
        mswitch.subscribe(self.iq, self.isq)
        self.tick_count=0

        self.builder = gtk.Builder()
        self.builder.add_from_file(glade_file)
        self.window = self.builder.get_object("ui_window")

        self.reqin=self.builder.get_object("lRequestsData")
        self.reqInfoData=self.builder.get_object("lRequestsInfoData")
        
        self.reqdrop=self.builder.get_object("lRequestsDroppedData")
        self.mbfailed=self.builder.get_object("lMBFailedData")
        self.hits=self.builder.get_object("lHitsData")
        self.misses=self.builder.get_object("lMissesData")
        self.notfound=self.builder.get_object("lNotFoundData")
        self.filtered=self.builder.get_object("lFilteredData")
        self.retries_dropped=self.builder.get_object("lRetriesDroppedData")

        self.total_records=self.builder.get_object("lTotalRecordsData")
        self.records_mbid=self.builder.get_object("lRecordsWithMbidData")
        self.job_queue=self.builder.get_object("lJobQueueData")
        self.job_info_queue=self.builder.get_object("lJobInfoQueueData")
        
        self.window.connect("destroy-event", self.on_destroy)
        self.window.connect("destroy",       self.on_destroy)
        self.window.present()
        
        self.cRequestsIn = 0
        self.cRequestsInfo = 0
        self.cRequestsDropped = 0
        self.cHits = 0
        self.cMisses = 0
        self.cFailed = 0
        self.cNotFound = 0
        self.cRetriesDropped = 0
        self.cFiltered=0
        
    def on_destroy(self, *_):
        mswitch.publish("__ui__", "__quit__")
        gtk.main_quit()

    def h_filtered(self, *_):
        self.cFiltered += 1
        self.filtered.set_text(str(self.cFiltered))
        
    def h_job_queues(self, todo, info):
        self.job_queue.set_text(str(todo))
        self.job_info_queue.set_text(str(info))

    def h_cache_stats(self, ctotal_records, ctotal_records_mbid):
        self.total_records.set_text(str(ctotal_records))
        self.records_mbid.set_text(str(ctotal_records_mbid))

    def hq_track(self, ref, _artist, _track, priority):
        """
        For computing the 'requests in' counter
        """
        if priority=="low":
            self.cRequestsInfo += 1
            self.reqInfoData.set_text(str(self.cRequestsInfo))
        else:
            self.cRequestsIn += 1
            self.reqin.set_text(str(self.cRequestsIn))

    def h_mb_queue_full(self, *_):
        """
        For computing the 'requests dropped' counter
        """
        self.cRequestsDropped += 1
        self.reqdrop.set_text(str(self.cRequestsDropped)) 

    def h_mb_retry_dropped(self, *_):
        self.cRetriesDropped += 1
        self.retries_dropped.set_text(str(self.cRetriesDropped))

    def h_tracks(self, source, _ref, tracks):
        """
        For computing the 'hits' and 'misses'
        """
        track=tracks[0]
        
        try:    track_mbid=track["track_mbid"]
        except: track_mbid=None
        
        if source=="mb":
            if track is None or track_mbid is None or track_mbid=="":
                self.cNotFound += 1
                self.notfound.set_text(str(self.cNotFound))
                return
        
        #print "ui.h_track: ", source, _ref, track
        if source == "cache":
            if track_mbid!="" and track_mbid is not None:
                self.cHits += 1
                self.hits.set_text(str(self.cHits))
            else:
                self.cMisses += 1
                self.misses.set_text(str(self.cMisses))
                
    def h_cache_miss(self, *_):
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
        self.tick_count += 1
        
        #print "tick! ", tick_second
        
        mswitch.publish("__main__", "tick", TICKS_SECOND, tick_second)
        
        while True:
            try:     
                envelope=self.isq.get(False)
                quit, mtype, handled=mdispatch(self, "__main__", envelope)
                if handled==False:
                    mswitch.publish(self.__class__, "__interest__", (mtype, False, self.isq))
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
                    
                burst -= 1
                if burst == 0:
                    break
            except Empty:
                break
            
            continue

        return True


        
ui=UiWindow(glade_file)
gobject.timeout_add(TIME_BASE, ui.tick)


