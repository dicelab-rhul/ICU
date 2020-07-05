from psychopy.iohub import launchHubServer

def connect_eyetracker(sample_rate = 300):
    print("CONNECTING EYETRACKER...")
    iohub_config = {'eyetracker.hw.tobii.EyeTracker':
                   {'name': 'tracker', 'runtime_settings': {'sampling_rate': sample_rate}}}
    
    io = launchHubServer(**iohub_config)  
    print("SUCCESS!")  
    return io

def calibrate(tracker):
    r = tracker.runSetupProcedure()
    
    if r:
        print('calibration success')
    else:
        print('calibration unsuccessful')

def stream(tracker, duration):
    """
    Parameters
    ----------
    tracker : io.devices.tracker attribute
        DESCRIPTION. Object - the connection to a Tobii-Studio Eyetracker
    duration : Float
        DESCRIPTION. Duration in seconds to report stream of gaze coordinates 

    Yields
    ------
    TUPLE
        (Left Eye Gaze Screen Coordinate in X (Pixels),
         Left Eye Gaze Screen Coordinate in Y (Pixels),
         Time)

    """
    import time
    
    # Check for and print any eye tracker events received...
    tracker.setRecordingState(True)

    stime = time.time()
    #print(stime)
    while time.time()-stime < duration:
        #print(time.time())
        for e in tracker.getEvents(asType='dict'):
            #logic to remove bad samples
            
            yield (e['left_gaze_x'], e['left_gaze_y'], e['time'])


def run(duration = 5, # 5 seconds for demo 
             calibrate_system = False,
             sample_rate = 300):
    """
    Parameters
    ----------
    duration : Float
         Duration in seconds to report stream of gaze coordinates
    calibrate : Bool, optional
        Whether to calibrate the eyetracking system or not. 
        The default is False.
    sample_rate : Int, optional
        The sampling frequency of the eyetracker in Hertz
        The default is 300 (Maximum).
        Common options: 300, 250, 200, 120, 100 

    Returns
    -------
    None.

    """
    
    io = connect_eyetracker(sample_rate = sample_rate)
    
    tracker = io.devices.tracker

    print("CALIBRATING EYETRACKER") 
    if calibrate_system:
        calibrate(tracker)
    
    #for event in stream(tracker, duration):
    #    print(event) #do some stuff
    
    io.quit()

run()