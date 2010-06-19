"""
    Base class for threaded Agents
    
    * high/low priority message queues
    * message bursting controlled
    * message dispatching based on Agent 'interest'
    
    @author: jldupont
    @date: May 17, 2010
    @revised: June 18, 2010
"""

from threading import Thread
from Queue import Queue, Empty
import uuid

import mswitch

__all__=["AgentThreadedBase", "debug", "mdispatch"]

debug=False


def mdispatch(obj, obj_orig, envelope):
    """
    Dispatches a message to the target
    handler inside a class instance
    """
    mtype, payload = envelope
    orig, msg, pargs, kargs = payload
    
    ## Avoid sending to self
    if orig == obj_orig:
        return (False, mtype, None)

    if mtype=="__quit__":
        return (True, mtype, None)

    handled=False

    if mtype.endswith("?"):
        handlerName="hq_%s" % mtype[:-1]
    else:
        handlerName="h_%s" % mtype
    handler=getattr(obj, handlerName, None)
    
    if handler is None:
        handler=getattr(obj, "h_default", None)    
        if handler is not None:
            handler(mtype, msg, *pargs, **kargs)
            handled=True
    else:
        handler(msg, *pargs, **kargs)
        handled=True

    if handler is None:
        if debug:
            print "! No handler for message-type: %s" % mtype
    
    return (False, mtype, handled)


class AgentThreadedBase(Thread):
    """
    Base class for Agent running in a 'thread' 
    """
    
    LOW_PRIORITY_BURST_SIZE=5
    
    def __init__(self, debug=False):
        Thread.__init__(self)
        self.mmap={}
        
        self.debug=debug
        self.id = uuid.uuid1()
        self.iq = Queue()
        self.isq= Queue()
        
    def pub(self, msgType, msg, *pargs, **kargs):
        mswitch.publish(self.id, msgType, msg, *pargs, **kargs)
        
    def run(self):
        """
        Main Loop
        """
        ## subscribe this agent to all
        ## the messages of the switch
        mswitch.subscribe(self.iq, self.isq)
        
        quit=False
        while not quit:
            #print str(self.__class__)+ "BEGIN"
            while True:
                try:
                    envelope=self.isq.get(block=True, timeout=0.1)
                    mquit=self._process(envelope)
                    if mquit:
                        quit=True
                        break
                    continue
                except Empty:
                    break
                

            burst=self.LOW_PRIORITY_BURST_SIZE
            while True and not quit:                
                try:
                    envelope=self.iq.get(block=False)#(block=True, timeout=0.1)
                    mquit=self._process(envelope)
                    if mquit:
                        quit=True
                        break

                    burst -= 1
                    if burst == 0:
                        break
                except Empty:
                    break
        print str(self.__class__) + " - shutdown"
                
    def _process(self, envelope):
        mtype, _payload = envelope
        
        #if mtype!="tick":
        #    print "base._process: mtype: " + str(mtype)
        
        interested=self.mmap.get(mtype, None)
        if interested==False:
            return False
        
        quit, _mtype, handled=mdispatch(self, self.id, envelope)
        if quit:
            shutdown_handler=getattr(self, "h_shutdown", None)
            if shutdown_handler is not None:
                shutdown_handler()

        self.mmap[mtype]=handled
            
        ### signal this Agent's interest status (True/False)
        ### to the central message switch
        if interested is None:
            if mtype!="__quit__":
                mswitch.publish(self.__class__, "__interest__", (mtype, handled, self.iq))
            
        ### This debug info is extermely low overhead... keep it.
        if interested is None and handled:
            print "Agent(%s) interested(%s)" % (self.__class__, mtype)

        return quit
            


## ============================================================
## ============================================================ TESTS
## ============================================================


if __name__=="__main__":
    
    class Agent1(AgentThreadedBase):
        def __init__(self):
            AgentThreadedBase.__init__(self)
            
        def h_mtype1(self, *pargs, **kargs):
            print "Agent1.h_mtype1: pargs: %s  kargs: %s" % (pargs, kargs)

        def h_mtype2(self, *pargs, **kargs):
            print "Agent1.h_mtype2: pargs: %s  kargs: %s" % (pargs, kargs)
            

    class Agent2(AgentThreadedBase):
        def __init__(self):
            AgentThreadedBase.__init__(self)
            
        def h_mtype1(self, *pargs, **kargs):
            print "Agent2.h_mtype1: pargs: %s  kargs: %s" % (pargs, kargs)
            self.pub("mtype2", "mtype2 message!")

        def h_mtype2(self, *pargs, **kargs):
            print "Agent2.h_mtype2: pargs: %s  kargs: %s" % (pargs, kargs)


    a1=Agent1()
    a2=Agent2()
    
    a1.start()
    a2.start()
    
    mswitch.publish(None, "mtype1", "coucou!")
    mswitch.publish(None, "mtype1", "coucou2!")

    while True:
        pass
