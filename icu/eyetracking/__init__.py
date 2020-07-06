"""
    Defines eyetracking classes, most notably the Eyetracker class which interfaces with psychopy. 

    @Author: Benedict Wilkins
    @Date: 2020-04-02 21:49:01
"""

import threading

from collections import deque

from threading import Thread
import random

from time import sleep

from sys import version_info

if version_info.major + version_info.minor / 10 < 3.7:
    from time import time
else:
    from time import time_ns as time

from .. import event

from . import filter

__all__ = ('filter',)


class EyeTrackingError(Exception):
    """ 
        An error that may be thrown by an EyeTracker, typically will wrap a psychopy error.
    """
    
    def __init__(self, message, cause=None):
        super(EyeTrackingError, self).__init__(message)
        if cause is not None:
            self.__cause__ = cause

class EyeTrackerBase(event.EventCallback, threading.Thread):

    def __init__(self, filter=None, **kwargs):
        super(EyeTrackerBase, self).__init__(**kwargs)
        self.__filter = filter

    def source(self, t, x, y):
        if self.__filter is not None:
            e = self.__filter(t, x, y)
            if e is not None:
                d = dict(label='place', x=x, y=x, timestamp=t)
                d.update(e)
                #print(e)
                super().source('Overlay:0', **d) #TODO change Overlay if we want to event to go elsewhere
        else:
            super().source('Overlay:0', label='place', x=x, y=x, timestamp=t)

class EyeTracker(EyeTrackerBase):

    def __init__(self, filter=None, sample_rate = 300, calibrate_system=True):
        super(EyeTracker, self).__init__(filter)
        self.daemon = True #??? TODO any issue with this closing down psychopy?
        #https://stackoverflow.com/questions/40391812/running-code-when-closing-a-python-daemon
        try:
            from psychopy.iohub import launchHubServer
        except Exception as e:
            raise EyeTrackingError("required import failed.", cause=e)

        #self.io = connect_eyetracker(sample_rate = sample_rate)
    
        iohub_config = {'eyetracker.hw.tobii.EyeTracker':
                       {'name':'tracker','runtime_settings':{'sampling_rate':sample_rate}}}
        self.io = launchHubServer(**iohub_config)    
        self.tracker = self.io.devices.tracker
        self.sample_rate = sample_rate
        
        if calibrate_system:
            if not self.tracker.runSetupProcedure():
                raise EyeTrackingError("failed to calibrate eyetracker.")
        
        self.closed = threading.Event()
        name = "{0}:{1}".format(EyeTracker.__name__, str(0))
        self.register(name)
            
    def run(self):
        self.tracker.setRecordingState(True) #what is this?
        while not self.closed.is_set():
            for e in self.tracker.getEvents(asType='dict'): #this might cause the thread to hang... TODO fix it!
                pass #TODO #self.source('TODO', label='place', x=e['left_gaze_x'], y=e['left_gaze_y'], timestamp=e['time'])
        self.io.quit()
    
    def close(self):
        self.closed.set()

class EyeTrackerStub(EyeTrackerBase):
    """ 
        A stub EyeTracker class that uses the current mouse position as a stand in for gaze position, 
        use for testing without eyetracking hardware.
    """

    def __init__(self, root, filter=None, sample_rate = 300, **kwargs):
        super(EyeTrackerStub, self).__init__(filter, **kwargs)
        self.daemon = True
        self.sample_rate = sample_rate
        self.__time = 0
        root.bind("<Motion>", self.update)

        self.closed = threading.Event()
        self.register(self.__class__.__name__)

        self._p_mouse_x = 0
        self._p_mouse_y = 0

        self._n_mouse_x = 0
        self._n_mouse_y = 0
    
    def update(self, event):
        """ 
            Called when the mouse moves, updates internal mouse (x,y).

            Args:
                event (mouseevent): a mouse event generated that defines x,y attributes.
        """
        self._n_mouse_x = event.x
        self._n_mouse_y = event.y

    def run(self):
        """
            Generates events that move the current overlay (if it exists).
        """
        while not self.closed.is_set():
            self.__time += 1
            sleep(1. / self.sample_rate)
            #self.source('Overlay:Overlay', label='move', dx=random.randint(0,10), dy=random.randint(0,10), timestamp=self.__time)
            #if self._p_mouse_x != self._n_mouse_x or self._p_mouse_y != self._n_mouse_y:
            self.source(time(), self._n_mouse_x, self._n_mouse_y)
            
            self._p_mouse_x = self._n_mouse_x
            self._p_mouse_y = self._n_mouse_y

    def close(self):
        """ 
            Force the thread to exit.
        """
        self.closed.set()

def eyetracker(root, filter=None, sample_rate=300, calibrate_system=True, stub=False):
    """ Creates a new Eyetracker (there should only ever be one).
    
    Args:
        root (tk): tk root window.
        filter: a filter for x,y - averaging, gaze points etc (see eyetracker.filter)
        sample_rate (int, optional): number of samples (events) per second. Defaults to 300.
        calibrate_system (bool, optional): calibrate the eyetracker. Defaults to True.
        stub (bool, optional): use a stub class (see StubEyeTracker) if hardware is not available. Defaults to False.
    
    Returns:
        EyeTracker, StubEyeTracker: The new EyeTracker.
    """
    if not stub:
        eyetracker = EyeTracker(filter=filter, sample_rate=sample_rate, calibrate_system=calibrate_system)
    else:
        eyetracker = EyeTrackerStub(root, filter=filter, sample_rate=sample_rate)
    return eyetracker


