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
                                       dbus_interface="com.jldupont.musicbrainz-proxy",
                                       bus_name=None,
                                       path="/Tracks"
                                       )            

    @dbus.service.signal(dbus_interface="com.jldupont.musicbrainz-proxy", signature="a{sv}")
    def Track(self, dic):
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
        
    def h_shutdown(self):
        print "ADBus - shutdown"


_=DbusAgent()
_.start()
