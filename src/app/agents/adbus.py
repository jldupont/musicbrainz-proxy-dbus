"""
    DBus Agent
    
    Messages Emitted:
    - "track?"
    
    Messages Processed:
    - "track"

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

    @dbus.service.signal(dbus_interface="com.jldupont.musicbrainz.proxy", signature="ssaa{sv}")
    def Tracks(self, source, ref, list_dic):
        pass

    def sQTrack(self, ref, artist_name, track_name, priority):
        """
        DBus signal handler - /Tracks/qTrack
        
        @param ref: string - an opaque "reference"
        @param artist_name: string
        @param track_name:  string
        @param priority:    string [low|high]
        
        @todo: better error handling
        """
        try:    artist=str(artist_name)
        except: artist=None
        try:    track=str(track_name)
        except: track=None
        
        mswitch.publish(self.agent, "track?", ref, artist, track, priority)


class DbusAgent(AgentThreadedBase):
    
    def __init__(self):
        """
        @param interval: interval in seconds
        """
        AgentThreadedBase.__init__(self)

        self.srx=SignalRx(self)
           
    def h_tracks(self, source, ref, tracks):
        """
        Handler for the 'tracks' message
        
        Sends back a message on DBus
        """
        ## if the origin was "TrackInfo"
        if source=="info":
            return
        
        if tracks is None:
            return
    
        result=[]
        for track in tracks:
            if track is not None:
                result.append(self._format(track))
            
        self.srx.Tracks(source, ref, result)

    def h_tracksv2(self, source, ref, tracks):
        """
        Handler for the 'tracks' message
        
        Sends back a message on DBus
        """
        if source=="info":
            return
        
        if tracks is None:
            return

        self.srx.Tracks(source, ref, tracks)
            
        
    def _format(self, track):
        details={}
        details["artist_name"]=    str( track.get("artist_name", "") )
        details["track_name"]=     str( track.get("track_name", "") )
        details["artist_mbid"]=    str( track.get("artist_mbid", "") )
        details["track_mbid"]=     str( track.get("track_mbid", "") )
        details["mb_artist_name"]= str( track.get("mb_artist_name", "") )
        details["mb_track_name"]=  str( track.get("mb_track_name", "") )
        return details
    
        

_=DbusAgent()
_.start()
