"""
    Musicbrainz Agent

    Messages Processed:
    - "track"
    - "tick"
    
    Messages Emitted:
    - "track"
    - "mb_queue_full"
    - "mb_error"
    

    @author: jldupont
    @date: May 29, 2010
"""
import copy
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
    

       


class MBAgent(AgentThreadedBase):

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
        
        btrack=self._queryTrack(track)
        self.pub("track", "mb", ref, btrack)
        

    def h_track(self, _source, ref, track):
        """
        Handler for the 'track' message
    
        @param ref: opaque reference
        @param track: track details object
        """
        #print "mb.h_track, source, ref, track", _source, ref, track
        
        ## if the track message already contains
        ##  an mbid id, then no use making a call to Musicbrainz:
        ##  it is the 'cache agent' that's probably emitting this message 
        track_mbid=track.get("track_mbid", None)
        if track_mbid is not None:
            return
        
        ctrack=copy.deepcopy(track)
        
        try:
            self.qtodo.put((ref, ctrack))
        except Full:
            self.pub("mb_queue_full", (ref, ctrack))
        
    
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
            tuuid=u.extractUuid(result.track.id)
            auuid=u.extractUuid(result.track.artist.id)
            artist=result.track.artist.name
            title=result.track.title
        except IndexError,_e:
            return None
        except Exception,e:
            self.pub("mb_error", e)
            return None
        
        #print "mb._queryTrack: track_mbid: ", tuuid
        
        btrack=copy.deepcopy(track)
        
        btrack["track_mbid"]=tuuid
        btrack["artist_mbid"]=auuid

        ## Add these details to the original 'track' object:
        ##  these should help populate the cache with useful information                
        btrack["mb_artist_name"]=artist
        btrack["mb_track_name"]=title
        
        return btrack
    
        
        

if __name__ != "__main__":
   
    _=MBAgent()
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
    
        
        
    
    
    