"""
    Heart Agent
    
    Responsible for generating a regular 'heart beat'
    available through DBus
        
    Created on 2010-08-25
    @author: jldupont
"""
from app.system.base import AgentThreadedBase

class HeartAgent(AgentThreadedBase):
    
    INTERVAL=5
    
    def __init__(self):
        AgentThreadedBase.__init__(self)
        self.timeout=0
        
    def h_tick(self, _ticks_second, tick_second):
        self.timeout += 1
        if tick_second:
            if (self.timeout % self.INTERVAL)==0:
                self.pub("random_track_missing_mbid?")
                
                
    def h_random_track_missing_mbid(self, track):
        self.pub("tracksv2", "__heart__", "", [track])
        
        
_=HeartAgent()
_.start()
