from psychopy.iohub import launchHubServer
import traceback

def connect_eyetracker(sample_rate = 300):
    print("CONNECTING EYETRACKER...")
    iohub_config = {'eyetracker.hw.tobii.EyeTracker':
                   {'name': 'tracker', 
                   'runtime_settings': {'sampling_rate': sample_rate}}}
                   
    
    io = launchHubServer(**iohub_config)  
    print("SUCCESS!")  
    return io

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


def run(duration = 5, calibrate = True, sample_rate = 300):
    """
        Tets the eye tracker.
        
        Args:
            duration (int, optional):  Duration in seconds to report stream of gaze coordinates. Defaults to 5.
            calibrate (bool, optional):   Whether to calibrate the eyetracking system or not. Defaults to True.
            sample_rate (int, optional): The sampling frequency of the eyetracker in Hertz. Defaults to 300.
    """

    io = connect_eyetracker(sample_rate = sample_rate)
    try:    
        tracker = io.devices.tracker
        if calibrate:
            print("CALIBRATING EYETRACKER...") 
            r = tracker.runSetupProcedure()
            print(r)
            print(["FAILED", "SUCCESS"][int(r)])
        
        print("STEAMING EVENTS: ...")
        for event in stream(tracker, duration):
            print(event) #do some stuff
        
        print("FINSIHED.")
    except:
        traceback.print_exc()
    io.quit()

run(calibrate=True)