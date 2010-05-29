"""
    Musicbrainz Agent

    Messages Processed:
    - "track"
    - "tick"
    
    Messages Emitted:
    - "track"
    

    @author: jldupont
    @date: May 29, 2010
"""
from Queue import Queue, Empty, Full

import musicbrainz2.webservice as ws #@UnresolvedImport
import musicbrainz2.utils as u       #@UnresolvedImport

from app.system.base import AgentThreadedBase
from app.system import mswitch

__all__=[]


class Agent(AgentThreadedBase):

    QUEUE_SIZE=512
    
    def __init__(self):
        AgentThreadedBase.__init__(self)

        self.qtodo=Queue(self.QUEUE_SIZE)


    def h_tick(self, ticks_second, tick_second):
        """
        Handler for the 'tick' message
        
        @param ticks_second: number of ticks per second
        @param tick_second:  True for when the 'tick' marks the second
        """

    def h_track(self, ref, track):
        """
        Handler for the 'track' message
    
        @param ref: opaque reference
        @param track: track details object
        """
        
        ## if the track message already contains
        ##  an mbid id, then no use making a call to Musicbrainz:
        ##  it is the 'cache agent' that's probably emitting this message 
        track_mbid=track["track_mbid"]
        if len(track_mbid) != 0:
            return
        
        try:
            self.qtodo.put((ref, track), block=False)
        except Full:
            self.pub("", msg)
        
        

if __name__ != "__main__":
   
    _=Agent()
    _.start()
