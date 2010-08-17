"""
    Cache Agent

    Messages Emitted:
    - "track"
    - "cache_miss"
    
    Messages Processed:
    - "track?"
    - "tracks"
    
    @author: jldupont
    @date: May 28, 2010
"""
import os
import sqlite3
import time

from app.system.base import AgentThreadedBase
from app.system.filter import filterArtist

__all__=["CacheAgent"]


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
    
    REFRESH_TIMEOUT=10 ##seconds
    
    def __init__(self, dbpath):
        AgentThreadedBase.__init__(self)

        self.dbpath=dbpath
        self.path=os.path.expanduser(self.dbpath)
        self.conn=sqlite3.connect(self.path, check_same_thread=False)
        self.c = self.conn.cursor()
        
        self.c.execute("""create table if not exists tracks (id integer primary key,
                            created integer,
                            updated integer,
                            track_name text,  track_mbid text,
                            artist_name text, artist_mbid text)
                        """)
        
        self.refresh_counter=0
        
    ## ========================================================= HANDLERS
    def h_tick(self, _ticks_per_second, second_marker):
        """
        """
        if second_marker:
            self.refresh_counter += 1
            
        if self.refresh_counter == self.REFRESH_TIMEOUT:
            self.refresh_counter=0
            self._doRefresh()
        
    def _doRefresh(self):
        """
        Refresh the stats
        """
        total_records=self.getRowCount()
        total_records_mbid=self.getRowCountWithTrackMbid()
        
        self.pub("cache_stats", total_records, total_records_mbid)
        
        
    def hq_track(self, ref, artist_name, track_name, priority):
        """
        Question: 'track?'
        """
        try:    l=len(artist_name)
        except: l=0
        
        if artist_name is None or l==0:
            self.pub("log", "error", "qTrack: invalid artist_name")
            return
        
        try:    l=len(track_name)
        except: l=0
        if track_name is None or l==0:
            self.pub("log", "error", "qTrack: invalid track_name")
            return
        
        ## perform filtering phase
        if filterArtist(artist_name):
            ##self.pub("log", "warning", "Filtered artist(%s) track(%s)" % (artist_name, track_name))
            self.pub("filtered", artist_name, track_name)
            return
        
        
        #print "Cache.h_qtrack: artist(%s) track(%s)" % (artist_name, track_name)
        tlist=[]
        
        track=self._findTrack(artist_name, track_name)
        
        track["artist_name"]=artist_name
        track["track_name"]=track_name
        track_mbid=track.get("track_mbid", "")
        
        ## only one result unfortunately...
        if track_mbid is None or track_mbid=="":
            self.pub("cache_miss", ref, track, priority)
            return
        
        ## maybe we'll get lucky and pull more tracks
        ## based on the mbid we got...
        tracks=self._findTracksBasedOnTrackMbid(track_mbid)
        
        ## nope, just one still
        if tracks is None:
            self.pub("tracks", "cache", ref, [track])
            return
            
        for track_tuple in tracks:
            t=makeTrackDict(track_tuple)
            tlist.append(t)

        self.pub("tracks", "cache", ref, tlist)
            

    def h_tracks(self, _source, _ref, tracks):
        """
        Handler for the 'track' message
        
        Updates the cache, if necessary
        """
        
        ## Should occur but hey, better safe than sorry ;-)
        if tracks is None:
            return

        track=tracks[0]

        ## Update the cache regardless of the 'track' object we get:
        ##  if the entry wasn't found on Musicbrainz, we'll have at least
        ##  a trace of the attempt (i.e. 'updated' field) and thus we can
        ##  rate limit the retries.  
        try:      
            new=self._updateOrInsert(track)
        except Exception,e:
            self.pub("log", "error", "Exception whilst Accessing database: %s" % e)
            return
        
        if new:
            artist_name=track["artist_name"]
            track_name= track["track_name"]
            track_mbid= track["track_mbid"]
            self.pub("log", "New: artist(%s) track(%s) mbid(%s)" % (artist_name, track_name, track_mbid))
        
        ## Insert/Update a record based on the answer provided
        ##  by Musicbrainz: this way, we have more ways to "hit"
        ##  a potential track target in the cache
        mb_artist_name=track.get("mb_artist_name", None)
        mb_track_name=track.get("mb_track_name", None)
        
        if mb_artist_name is not None:
            if mb_track_name is not None:
                details=(0,0,0,  ## filled out anyhow by update/insert method
                         mb_track_name,  track["track_mbid"],
                         mb_artist_name, track["artist_mbid"]
                         )
                
                mb_track=makeTrackDict(details)
                try:
                    self._updateOrInsert(mb_track)
                except Exception,e:
                    self.pub("log", "error", "Exception whilst Accessing database: %s" % e)                   
        
        
    ## ========================================================= PRIVATE
    def _updateOrInsert(self, track):
        """
        Updates the track OR inserts it
        """
        new=False
        now=time.time()        

        artist_name=unicode(track["artist_name"])
        track_name=unicode(track["track_name"])

        self.c.execute("""UPDATE tracks SET 
                        track_mbid=?, artist_mbid=?,
                        updated=? WHERE artist_name=? AND track_name=?""", 
                        (track["track_mbid"], track["artist_mbid"],
                         now,
                        artist_name, track_name,
                        ))
        
        
        if self.c.rowcount != 1:
            self.c.execute("""INSERT INTO tracks (created, updated,  
                            track_name, track_mbid,
                            artist_name, artist_mbid
                            ) VALUES (?, ?, ?, ?, ?, ?)""", 
                            (now, 0, track_name, track["track_mbid"],
                            artist_name, track["artist_mbid"]) )
            new=True
            
        self.conn.commit()
        return new
        
        
        
    def _findTrack(self, artist_name, track_name):
        """
        Locates a 'track'
        """
        try:
            self.c.execute("""SELECT * FROM tracks WHERE track_name=? AND artist_name=?""", 
                           (unicode(track_name), unicode(artist_name)))
            track_tuple=self.c.fetchone()
        except:
            track_tuple=None

        track=makeTrackDict(track_tuple)
        return track


    def _findTracksBasedOnTrackMbid(self, track_mbid):
        """
        Locates tracks based on track_mbid
        """
        try:
            self.c.execute("""SELECT * FROM tracks WHERE track_mbid=?""", (track_mbid,))
            track_tuples=self.c.fetchall()
        except:
            track_tuples=None
            
        return track_tuples

    def getRowCount(self):
        """
        Returns the total row count
        """
        try:
            self.c.execute("""SELECT Count(*) FROM tracks""")    
            count=self.c.fetchone()[0]
        except: count=0
        
        return count

    def getRowCountWithTrackMbid(self):
        """
        Returns the total row count
        """
        try:
            self.c.execute("""SELECT Count(*) FROM tracks WHERE track_mbid<>'' """)    
            count=self.c.fetchone()[0]
        except: count=0
        
        return count

"""
_=CacheAgent()
_.start()
"""
