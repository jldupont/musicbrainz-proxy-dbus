"""
    @author: jldupont
    @date: May 29, 2010
"""

from app.system.base import AgentThreadedBase

__all__=[]


class TestAgent(AgentThreadedBase):
    
    LIMIT=5
    
    def __init__(self):
        AgentThreadedBase.__init__(self)
        self.c=0

    def h_tick(self, *_):
        """
        """
        self.c += 1
        if self.c > self.LIMIT:
            return
        
        print "test!"
        self.pub("test_track?", "test", "Beyonce", "Baby Boy")
        


_=TestAgent()
_.start()
