import threading

from threading import Thread

from .. import event

class EyeTrackingError(Exception):
    
    def __init__(self, message, cause=None):
        super(EyeTrackingError, self).__init__(message)
        if cause is not None:
            self.__cause__ = cause

class EyeTracker(event.EventCallback, threading.Thread):

    def __init__(self, sample_rate = 300, calibrate_system=True):
        super(EyeTracker, self).__init__()
        
        try:
            from psychopy.iohub import launchHubServer
        except Exception as e:
            raise EyeTrackingError("required import failed.", cause=e)

        self.io = connect_eyetracker(sample_rate = sample_rate)
    
        iohub_config = {'eyetracker.hw.tobii.EyeTracker':
                       {'name':'tracker','runtime_settings':{'sampling_rate':sample_rate}}}
        self.io = launchHubServer(**iohub_config)    
        self.tracker = io.devices.tracker
        self.sample_rate = sample_rate
        
        if calibrate_system:
            if not tracker.runSetupProcedure():
                raise EyeTrackingError("failed to calibrate eyetracker.")
        
        self.closed = threading.Event()
        self.register('eyetracker')
            
    def run(self):
        def __thunk():
            while True:
                for e in tracker.getEvents(asType='dict'): #this might cause the thread to hang... TODO fix it!
                    self.source('eyetracker', e['left_gaze_x'], e['left_gaze_y'], e['time'])
                    if self.closed.is_set():
                        return
        
        self.tracker.setRecordingState(True) #what is this?
        __thunk()
        io.quit()
    
    def close(self):
        self.closed.set()

class EyeTrackerStub(event.EventCallback, threading.Thread):

    def __init__(self, sample_rate = 300, **kwargs):
        super(EyeTrackerStub, self).__init__()

        self.sample_rate = sample_rate
        self.__time = 0

        self.closed = threading.Event()
        self.register('eyetracker')

    def run(self):
        import random
        import time
        while True:
            self.__time += 1
            time.sleep(1. / self.sample_rate)
            self.source('eyetracker', random.randint(0,100), random.randint(0,100), self.__time)
            if self.closed.is_set():
                return

    def close(self):
        self.closed.set()

def eyetracker(sample_rate= 300, calibrate_system=True, stub=False):
    if not stub:
        eyetracker = EyeTracker(sample_rate=sample_rate, calibrate_system=calibrate_system)
    else:
        eyetracker = EyeTrackerStub(sample_rate=sample_rate, calibrate_system=calibrate_system)
    return eyetracker