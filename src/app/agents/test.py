"""
    @author: jldupont
    @date: May 29, 2010
"""

from app.system.base import AgentThreadedBase

__all__=[]


class TestAgent(AgentThreadedBase):
    
    LIMIT=2
    
    def __init__(self):
        AgentThreadedBase.__init__(self)
        self.c=0

    def h_tick(self, *_):
        """
        """
        self.c += 1
        if self.c > self.LIMIT:
            return
        
        self.pub("track?", "test", "Beyonce",      "Baby Boy")
        self.pub("track?", "test", "Beyonce",      "Baby Boy2")
        self.pub("track?", "test", "Depeche Mode", "Little 20")
        


_=TestAgent()
_.start()
