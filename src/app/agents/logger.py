"""
    Logger Agent
    
    @author: jldupont
    @date: May 21, 2010
"""
import os
import logging
from app.system.base    import AgentThreadedBase

__all__=[]

def getLogPath():
    path="~/musicbrainz-proxy.log"
    return os.path.expanduser(path)


class LoggerAgent(AgentThreadedBase):

    NAME="lastfmsqlite"
    
    mlevel={"info":     logging.INFO
            ,"warning": logging.WARNING
            ,"error":   logging.ERROR
            }
    
    def __init__(self):
        """
        @param interval: interval in seconds
        """
        AgentThreadedBase.__init__(self)
        self._logger=None
        self.fhdlr=None
        self._shutdown=False
        self._setup()
        
    def _setup(self):
        if self._logger is not None:
            return
        
        self._logger=logging.getLogger(self.NAME)
        
        _path=getLogPath()
        path=os.path.expandvars(os.path.expanduser(_path))
        self.fhdlr=logging.FileHandler(path)
        
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        self.fhdlr.setFormatter(formatter)
        self._logger.addHandler(self.fhdlr)
        self._logger.setLevel(logging.INFO)
        
    def h_shutdown(self):
        if self._logger:
            self._shutdown=True
            logging.shutdown([self.fhdlr])
            
    def h_log(self, *arg):
        if self._shutdown:
            return
        
        self._setup()
        
        if len(arg) == 1:
            self._logger.log(logging.INFO, arg[0])
        else:
            level=self.mlevel.get(arg[0], logging.INFO)
            self._logger.log(level, arg[1])
        



_=LoggerAgent()
_.start()
