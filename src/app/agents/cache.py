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


class Track(object):
    FIELDS=["id", "created", "updated", 
            "track_name",  "track_mbid",
            "artist_name", "artist_mbid"]
    
    def __init__(self, track_tuple=None):
        
        if track_tuple is None:
            return
        
        index=0
        for el in track_tuple:
            key=self.FIELDS[index]
            setattr(self, key, el)
            index += 1
            
    def __getattribute(self, key):
        #print "track.__getattribute__: key: %s" % key
        value=self.__dict__.get(key, None)
        return value       
            
    def __getattr__(self, key):
        #print "track.__getattr__: key: %s" % key
        value=self.__dict__.get(key, None)
        return value
    
    def __setattr__(self, key, value):
        self.__dict__[key]=value
        
    def __setitem__(self, key, value):
        self.__dict__[key]=value
        
    def __getitem__(self, key):
        return self.__dict__.get(key, None)
    

class CacheAgent(AgentThreadedBase):
    
    DBPATH="~/musicbrainz-proxy.sqlite"
    
    def __init__(self):
        AgentThreadedBase.__init__(self)

        self.path=os.path.expanduser(self.DBPATH)
        self.conn=sqlite3.connect(self.path)
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
        print "cache.h_track"
        
        ## If no mbid is present, don't bother updating the cache
        ##  because the mbid is the most important piece of it all
        track_mbid=track.track_mbid
        if track_mbid is None:
            return
            
        _new=self._updateOrInsert(track)
        
        ## Insert/Update a record based on the answer provided
        ##  by Musicbrainz: this way, we have more ways to "hit"
        ##  a potential track target in the cache
        mb_artist_name=track["mb_artist_name"]
        mb_track_name=track["mb_track_name"]
        
        if mb_artist_name is not None:
            if mb_track_name is not None:
                details=(0,0,0,  ## fillout anyhow by update/insert method
                         mb_track_name,  track["track_mbid"],
                         mb_artist_name, track["artist_mbid"]
                         )
                mb_track=Track(details)
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
                        (track.track_mbid, track.artist_mbid,
                         now,
                        track.artist_name, track.track_name,
                        ))
        
        
        if self.c.rowcount != 1:
            self.c.execute("""INSERT INTO tracks (created, updated,  
                            track_name, track_mbid,
                            artist_name, artist_mbid,
                            ) VALUES (?, ?, ?, ?, ?, ?)""", 
                            (now, 0, track.track_name, track.track_mbid,
                            track.artist_name, track.artist_mbid) )
            new=True
            
        self.conn.commit()
        return new
        
        
        
    def _findTrack(self, artist_name, track_name):
        """
        Locates a 'track'
        """
        try:
            self.c.execute("""SELECT * FROM tracks WHERE track_name=? AND artist_name=?""", (track_name, artist_name))
            track_tuple=self.c.fetchone()[0]
            print "!! cache._findTrack: FOUND: ", track_tuple
        except:
            print "** cache._findTrack: MISS: ", artist_name, track_name
            track_tuple=None
            
        track=Track(track_tuple)
        track.track_name=track_name
        track.artist_name=artist_name
        
        return track


if __name__!="__main__":
    _=CacheAgent()
    _.start()


if __name__=="__main__":
    t=Track()
    print t.artist_name
    t.track_name="track name!"
    print t.track_name
    
    d=t["test_dic"]
    print d
    
