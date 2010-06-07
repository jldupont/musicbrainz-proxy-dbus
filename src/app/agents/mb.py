"""
    Musicbrainz Agent

    Messages Processed:
    - "tick"
    - "cache_miss"
    
    Messages Emitted:
    - "tracks"
    - "mb_queue_full"
    - "mb_error"
    - "mb_retry_dropped"
    

    @author: jldupont
    @date: May 29, 2010
"""
import time
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

    QUEUE_SIZE=8192
    
    RETRY_TIMEOUT=60*60*24
    
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
        self.pub("tracks", "mb", ref, [btrack])
        

    def h_cache_miss(self, ref, track):
        """
        Handler for the 'cache_miss' message
    
        @param ref: opaque reference
        @param track: track details object
        """
        #print "mb.h_track, source, ref, track", _source, ref, track
        
        ## Let's see if we can retry fetching a possible
        ##  entry from Musicbrainz
        updated=track.get("updated", 0)
        now=time.time()
        delta=now-updated
        
        #print "updated, now, delta: ", updated, now, delta
        
        if delta < self.RETRY_TIMEOUT:
            artist_name=track.get("artist_name", "")
            track_name=track.get("track_name", "")
            self.pub("log", "Will retry later: artist(%s) track(%s)" % (artist_name, track_name))
            self.pub("mb_retry_dropped", ref, track)
            return
            
        ctrack=copy.deepcopy(track)
        
        try:
            self.qtodo.put((ref, ctrack))
        except Full:
            self.pub("mb_queue_full", (ref, ctrack))
        
    
    ## ================================================================== PRIVATE
    def _buildDefault(self, track):
        dtrack={}
        dtrack["artist_name"]=track["artist_name"]
        dtrack["track_name"]=track["track_name"]
        dtrack["artist_mbid"]=""
        dtrack["track_mbid"]=""
        return dtrack
    
    def _queryTrack(self, track):
        """
        Query the Musicbrainz webservice for information on 'track'
        
        We are assuming that the first result has the highest 'score'
        """
        artist_name=track["artist_name"]
        track_name=track["track_name"]
        
        try:    la=len(artist_name)
        except: la=0
        
        try:    lt=len(track_name)
        except: lt=0
        
        if la==0:
            self.pub("log", "error", "Query: invalid artist name")
            return None
        
        if lt==0:
            self.pub("log", "error", "Query: invalid track name")
            return None
        
        mbq=MBQuery(track)
        try:
            results=mbq.do()
        except Exception,e:
            self.pub("mb_error", e)
            self.pub("log", "error", "Failed call to Musicbrainz webservice: %s" % e)
            return self._buildDefault(track)
        
        try:
            result=results[0]
            tuuid=u.extractUuid(result.track.id)
            auuid=u.extractUuid(result.track.artist.id)
            artist=result.track.artist.name
            title=result.track.title
        except IndexError,_e:
            ## Return a basic 'track' dictionary:
            ##  This is useful for keeping coherent
            ##  with the 'message type' and help the cache
            ##  update itself i.e. 'updated' field
            self.pub("log", "warning", "Not found on Musicbrainz: artist(%s) track(%s)" % (track["artist_name"], track["track_name"]))
            return self._buildDefault(track)

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
    
        
        
    
    
    