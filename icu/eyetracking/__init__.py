"""
    Defines eyetracking classes, most notably the Eyetracker class which interfaces with psychopy. 

    @Author: Benedict Wilkins
    @Date: 2020-04-02 21:49:01
"""

import threading
import traceback
import math
from types import SimpleNamespace

from collections import deque

from threading import Thread
import random

from time import sleep, time

from .. import event

from . import filter

import logging
LOGGER = logging.getLogger("ICU")

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
        if filter is None:
            filter =lambda t,x,y:dict(timestamp=t,x=x,y=y,label="place")
            
        self.__filter = filter
        self.x, self.y = None, None

    def source(self, x, y, timestamp=None):
        e = self.__filter(timestamp,x,y)
        if e is not None:
            if self.x != e['x'] or self.y != e['y']: # only trigger if the eyes moved...
                self.x, self.y = e['x'], e['y']
                super().source('Overlay:0', **e)

class EyeTracker(EyeTrackerBase):

    def __init__(self, root, filter=None, sample_rate = 300, calibrate=True):
        super(EyeTracker, self).__init__(filter)
        self.daemon = True #??? TODO any issue with this closing down psychopy?
        #https://stackoverflow.com/questions/40391812/running-code-when-closing-a-python-daemon
        try:
            from psychopy.iohub import launchHubServer
        except Exception as e:
            raise EyeTrackingError("IMPORT FAILED.", cause=e)

        #self.io = connect_eyetracker(sample_rate = sample_rate)

        # HACKZ, this is required for the psychopy 3 (we have our own window, so fake it...)
        window = SimpleNamespace(units = 'pix', colorSpace = 'rgb', _isFullScr = True, 
                      screen = 0, monitor = SimpleNamespace(name = "monitor"))

        iohub_config = {'eyetracker.hw.tobii.EyeTracker':
                       {'name':'tracker',
                        'model_name': '',
                        'serial_number': '',
                        'runtime_settings':{'sampling_rate':sample_rate}
                       }}
        self.io = launchHubServer(window=window, **iohub_config)    
        self.tracker = self.io.devices.tracker

        self.sample_rate = sample_rate
        self.tk_root = root
        
        #self.tk_root.bind("<Configure>", self.tk_update) #TODO some thought here, cannot bind multiple <Configure>..?

        # transform eye tracking coordinates to tk window coordinates
        self.tk_position = (self.tk_root.winfo_x(), self.tk_root.winfo_y())
        self.tk_screen_size2 = (root.winfo_screenwidth()/2, root.winfo_screenheight()/2) #psychopy coordinate system is 0,0 screen center

        if calibrate:
            if not self.tracker.runSetupProcedure():
                print("WARNING: EYETRACKER CALIBRATION FAILED")
        
        self.closed = threading.Event()
        name = "{0}:{1}".format(EyeTracker.__name__, str(0))
        self.register(name)
    
    def tk_update(self, event):
        self.tk_position = (self.tk_root.winfo_x(), self.tk_root.winfo_y()) #(event.x, event.y) using the event information has some issues?

    def transform(self, x, y):
        return x - self.tk_root.winfo_x() + self.tk_screen_size2[0], -y - self.tk_root.winfo_y() + self.tk_screen_size2[1] #TODO update when <Configure> is avaliable...
        
        #return x - self.tk_position[0] + self.tk_screen_size2[0], -y - self.tk_position[1] + self.tk_screen_size2[1]
            
    def run(self):
        self.tracker.setRecordingState(True) #what is this?
        while not self.closed.is_set():
            for e in self.tracker.getEvents(asType='dict'): #this might cause the thread to hang... TODO fix it!
                x,y = e['left_gaze_x'], e['left_gaze_y']
                #print(e)
                if not (math.isnan(x) or math.isnan(y)):
                    #print("EYE TRACKER: {0} {1}".format(x, y))
                    x,y = self.transform(x,y) # convert to tk coordinates
                    #print("EYE TRACKER: {0} {1}".format(x, y))
                    self.source(x=x,y=y, timestamp=e['time'])
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
            #print(time(), self._n_mouse_x, self._n_mouse_y)
            self.source(x=self._n_mouse_x, y=self._n_mouse_y, timestamp=time())
            
            self._p_mouse_x = self._n_mouse_x
            self._p_mouse_y = self._n_mouse_y

    def close(self):
        """ 
            Force the thread to exit.
        """
        self.closed.set()


def eyetracker(root, filter=None, sample_rate=300, calibrate=True, stub=False, **kwargs):
    """ Creates a new Eyetracker (there should only ever be one).
    Args:
        root (tk): tk root window.
        filter: a filter for x,y - averaging, gaze points etc (see eyetracker.filter)
        sample_rate (int, optional): number of samples (events) per second. Defaults to 300.
        calibrate (bool, optional): calibrate the eyetracker. Defaults to True.
        stub (bool, optional): use a stub class (see StubEyeTracker) if hardware is not available. Defaults to False.
    
    Returns:
        (EyeTracker): The new EyeTracker.
    """ 
    LOGGER.debug("Initialising eyetracker... ")
    if not stub:
        try:
            return EyeTracker(root, filter=filter, sample_rate=sample_rate, calibrate=calibrate)
        except Exception as e: 
            LOGGER.error("Failed to initialise eyetracker")
            LOGGER.exception(e)
           
    
    LOGGER.debug("Using stub eyetracker (MOUSE COORDINATE)")
    return EyeTrackerStub(root, filter=filter, sample_rate=sample_rate)

