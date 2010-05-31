"""
    Cache Agent

    Messages Emitted:
    - "track"
    
    Messages Processed:
    - "track?"
    - "track"
    
    @author: jldupont
    @date: May 28, 2010
"""
import os
import sqlite3
import time

from app.system.base import AgentThreadedBase

__all__=[]


FIELDS=["id", "created", "updated", 
        "track_name",  "track_mbid",
        "artist_name", "artist_mbid"]

def makeTrackDict(track_tuple):
    if track_tuple is None:
        return {}
    dic={}
    index=0
    for el in track_tuple:
        key=FIELDS[index]
        dic[key]=el
        index += 1
    return dic


class CacheAgent(AgentThreadedBase):
    
    DBPATH="~/musicbrainz-proxy.sqlite"
    
    def __init__(self):
        AgentThreadedBase.__init__(self)

        self.path=os.path.expanduser(self.DBPATH)
        self.conn=sqlite3.connect(self.path, check_same_thread=False)
        self.c = self.conn.cursor()
        
        self.c.execute("""create table if not exists tracks (id integer primary key,
                            created integer,
                            updated integer,
                            track_name text,  track_mbid text,
                            artist_name text, artist_mbid text)
                        """)
        
    ## ========================================================= HANDLERS
        
    def hq_track(self, ref, artist_name, track_name):
        """
        Question: 'track?'
        """
        #print "Cache.h_qtrack: artist(%s) track(%s)" % (artist_name, track_name)
        track=self._findTrack(artist_name, track_name)
        self.pub("track", "cache", ref, track)

    def h_track(self, _source, _ref, track):
        """
        Handler for the 'track' message
        
        Updates the cache, if necessary
        """
        
        ## Should occur but hey, better safe than sorry ;-)
        if track is None:
            return

        ## Update the cache regardless of the 'track' object we get:
        ##  if the entry wasn't found on Musicbrainz, we'll have at least
        ##  a trace of the attempt (i.e. 'updated' field) and thus we can
        ##  rate limit the retries.        
        _new=self._updateOrInsert(track)
        
        ## Insert/Update a record based on the answer provided
        ##  by Musicbrainz: this way, we have more ways to "hit"
        ##  a potential track target in the cache
        mb_artist_name=track.get("mb_artist_name", None)
        mb_track_name=track.get("mb_track_name", None)
        
        if mb_artist_name is not None:
            if mb_track_name is not None:
                details=(0,0,0,  ## fillout anyhow by update/insert method
                         mb_track_name,  track["track_mbid"],
                         mb_artist_name, track["artist_mbid"]
                         )
                
                mb_track=makeTrackDict(details)
                self._updateOrInsert(mb_track)
        
        
    ## ========================================================= PRIVATE
    def _updateOrInsert(self, track):
        """
        Updates the track OR inserts it
        """
        new=False
        now=time.time()        

        self.c.execute("""UPDATE tracks SET 
                        track_mbid=?, artist_mbid=?,
                        updated=? WHERE artist_name=? AND track_name=?""", 
                        (track["track_mbid"], track["artist_mbid"],
                         now,
                        track["artist_name"], track["track_name"],
                        ))
        
        
        if self.c.rowcount != 1:
            self.c.execute("""INSERT INTO tracks (created, updated,  
                            track_name, track_mbid,
                            artist_name, artist_mbid
                            ) VALUES (?, ?, ?, ?, ?, ?)""", 
                            (now, 0, track["track_name"], track["track_mbid"],
                            track["artist_name"], track["artist_mbid"]) )
            new=True
            
        self.conn.commit()
        return new
        
        
        
    def _findTrack(self, artist_name, track_name):
        """
        Locates a 'track'
        """
        try:
            self.c.execute("""SELECT * FROM tracks WHERE track_name=? AND artist_name=?""", (track_name, artist_name))
            track_tuple=self.c.fetchone()
        except:
            track_tuple=None
            
        track=makeTrackDict(track_tuple)
        track["track_name"]=track_name
        track["artist_name"]=artist_name
        return track


if __name__!="__main__":
    _=CacheAgent()
    _.start()


