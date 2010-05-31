"""
    DBus Agent
    
    Messages Emitted:
    - "track?"
    
    Messages Processed:
    - 

    @author: jldupont
    @date: May 28, 2010
"""
import dbus.service
    
from app.system.base import AgentThreadedBase
from app.system import mswitch

__all__=[]


class SignalRx(dbus.service.Object):
    """
    DBus signals for the /Player path
    """
    PATH="/Tracks"
    
    def __init__(self, agent):
        dbus.service.Object.__init__(self, dbus.SessionBus(), self.PATH)
        self.agent=agent
        
        dbus.Bus().add_signal_receiver(self.sQTrack,
                                       signal_name="qTrack",
                                       dbus_interface="com.jldupont.musicbrainz.proxy",
                                       bus_name=None,
                                       path="/Tracks"
                                       )            

    @dbus.service.signal(dbus_interface="com.jldupont.musicbrainz.proxy", signature="ssa{sv}")
    def Track(self, source, ref, dic):
        pass


    def sQTrack(self, ref, artist_name, track_name):
        """
        DBus signal handler - /Tracks/qTrack
        
        @param ref: string - an opaque "reference"
        @param artist_name: string
        @param track_name:  string
        
        @todo: better error handling
        """
        try:    artist=str(artist_name)
        except: artist=None
        try:    track=str(track_name)
        except: track=None
        
        mswitch.publish(self.agent, "track?", ref, artist, track)


class DbusAgent(AgentThreadedBase):
    
    def __init__(self):
        """
        @param interval: interval in seconds
        """
        AgentThreadedBase.__init__(self)

        self.srx=SignalRx(self)
           
        
    def hq_test_track(self, ref, artist_name, track_name):
        """
        For testing purpose
        """
        self.pub("track?", ref, artist_name, track_name)
        
        
    def h_track(self, source, ref, track):
        """
        Handler for the 'track' message
        
        Send back a message on DBus
        """
        if track is None:
            return
        
        details={}
        details["artist_name"]=    str( track.get("artist_name", None) )
        details["track_name"]=     str( track.get("track_name", None) )
        details["artist_mbid"]=    str( track.get("artist_mbid", None) )
        details["track_mbid"]=     str( track.get("track_mbid", None) )
        details["mb_artist_name"]= str( track.get("mb_artist_name", None) )
        details["mb_track_name"]=  str( track.get("mb_track_name", None) )
        
        if track.get("artist_mbid", None) is None:
            return
        
        #print "dbus.h_track: ", source, ref, track
        
        ## Only send a response if we have a meaningful track_mbid
        if len(track["artist_mbid"]) > 1:
            self.srx.Track(source, ref, details)

_=DbusAgent()
_.start()
