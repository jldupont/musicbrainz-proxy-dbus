"""
    Musicbrainz Agent

    Messages Processed:
    - "track"
    - "tick"
    
    Messages Emitted:
    - "track"
    - "mb_queue_full"
    

    @author: jldupont
    @date: May 29, 2010
"""
from Queue import Queue, Empty, Full

import musicbrainz2.webservice as ws #@UnresolvedImport
import musicbrainz2.utils as u       #@UnresolvedImport

from app.system.base import AgentThreadedBase

__all__=[]


class MBQuery(object):
    def __init__(self, track):
        self.track=track
        
    def do(self):
        """
        Perform the query
        """
        q=ws.Query()
        title=self.track["track_name"]
        artist=self.track["artist_name"]
        
        f=ws.TrackFilter(title=title, artistName=artist)
        results=q.getTracks(f)

        return results
    
        

class Agent(AgentThreadedBase):

    QUEUE_SIZE=512
    
    def __init__(self):
        AgentThreadedBase.__init__(self)

        self.qtodo=Queue(self.QUEUE_SIZE)


    ## ================================================================== HANDLERS

    def h_tick(self, _ticks_second, tick_second):
        """
        Handler for the 'tick' message
        
        @param ticks_second: number of ticks per second
        @param tick_second:  True for when the 'tick' marks the second
        """
        
        ## Only 1 call / second to Musicbrainz
        if not tick_second:
            return
        
        try:
            (ref, track)=self.qtodo.get(block=False)
        except Empty:
            track=None
            
        ## nothing todo!
        if track is None:
            return
        
        uuid=self._queryTrack(track)
        track.track_mbid=uuid
        
        self.pub("track", ref, track)
        
        

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
            self.pub("mb_queue_full", (ref, track))
        
    
    ## ================================================================== PRIVATE
    
    def _queryTrack(self, track):
        """
        Query the Musicbrainz webservice for information on 'track'
        
        We are assuming that the first result has the highest 'score'
        """
        mbq=MBQuery(track)
        try:
            results=mbq.do()
        except Exception,e:
            self.pub("mb_error", e)
            return None
        
        try:
            result=results[0]
            uuid=u.extractUuid(result.track.id)
        except Exception,e:
            self.pub("mb_error", e)
            return None
        
        return uuid
    
        
        

if __name__ != "__main__":
   
    _=Agent()
    _.start()


## ========================================================================= TESTS


if __name__ == "__main__":
    track={}
    track["track_name"]="Baby Boy"
    track["artist_name"]="Beyonce"
    mbq=MBQuery(track)
    r=mbq.do()
    e=r[0]
    print e
    
    for e in r:
        id=e.track.id
        auuid=u.extractUuid(e.track.artist.id)
        
        uuid=u.extractUuid(id)
        print "Artist, Artist uuid, title, uuid: ", e.track.artist.name, auuid, e.track.title, uuid
    
        
        
    
    
    