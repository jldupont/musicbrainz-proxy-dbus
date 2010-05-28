"""
    Cache Agent

    Messages Emitted:
    - "track"
    
    Messages Processed:
    - "track?"
    - "mbtrack"
    
    @author: jldupont
    @date: May 28, 2010
"""
import os
import sqlite3
import time

from app.system.base import AgentThreadedBase
from app.system import mswitch

__all__=[]

class Track(object):
    FIELDS=["id", "created", "updated", 
            "track_name",  "track_mbid",
            "artist_name", "artist_mbid",
            "album_name",  "album_mbid"]
    
    def __init__(self, track_tuple=None):
        
        if track_tuple is None:
            return
        
        index=0
        for el in track_tuple:
            key=self.FIELDS[index]
            setattr(self, key, el)
            index += 1
            
    def __getattr__(self, key):
        value=self.__dict__.get(key, None)
        return value
    
    

class Agent(AgentThreadedBase):
    
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
                            artist_name text, artist_mbid text,
                            album_name text,  album_mbid text)
                        """)
        
    def hq_track(self, ref, artist_name, track_name):
        """
        Question: 'track?'
        """
        print "Cache.h_qtrack: artist(%s) track(%s)" % (artist_name, track_name)
        track=self.findTrack(artist_name, track_name)
        self.pub("track", ref, track)
            
        
    def findTrack(self, artist_name, track_name):
        """
        Locates a 'track'
        """
        try:
            self.c.execute("""SELECT * FROM tracks WHERE track_name=? AND artist_name=?""", (track_name, artist_name))
            track_tuple=self.c.fetchone()[0]
        except:
            track_tuple=None
            
        return Track(track_tuple)


if __name__!="__main__":
    _=Agent()
    _.start()


if __name__=="__main__":
    t=Track()
    print t.artist_name
    t.track_name="track name!"
    print t.track_name
    
