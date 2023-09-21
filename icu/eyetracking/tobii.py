
from icu import logging
from ..event2.event import SinkBase, SourceLocal
from .filter import NWMAFilter
from ..ui.commands import UI_INPUT_EYETRACKING, UI_WINDOW_WINDOWMOVED, UI_WINDOW_WINDOWRESIZED
from ..ui.draw import draw_circle
from ..ui.utils.math import Point

EYETRACKER_ADDRESS_URI = "tet-tcp://172.28.195.1" # update this for the test to work properly!

class TobiiEyetracker(SourceLocal, SinkBase): 

    def __init__(self, uri : str, smoothing : int = 6):
        SourceLocal.__init__(self)
        self.uri = uri

        try:
            import tobii_research
            self._eyetracker = tobii_research.EyeTracker(uri)
            self._eyetracker.subscribe_to(tobii_research.EYETRACKER_GAZE_DATA, self._internal_callback, as_dictionary=True)
        except Exception as e:
            logging.error(message = f"Eyetracker {self.uri} failed to start.", exception = e, file = __file__)
            raise e # TODO do we want to stop execution when this happens? maybe give an option to continue?

        logging.info(f"Eyetracker {self.uri} created successfully.", file = __file__)
        # screen_info = pygame.display.Info() - this doesnt work on all platforms, it gives the window height not the screen height?
        # instead use screeninfo
        from screeninfo import get_monitors
        monitor = get_monitors()
        assert len(monitor) == 1
        monitor = monitor[0]
        self._screen_size = Point(monitor.width, monitor.height)
        logging.info(f"Eyetracker {self.uri} obtained screen size: {self._screen_size.get()}", file = __file__)

        # these should be set before processing eye events? 
        self._window_position = Point(0,0) 
        self._window_size = Point(1,1) 
        self._smoothing = NWMAFilter(smoothing)
        logging.info(f"Eyetracker {self.uri} using {self._smoothing} smoothing.", file = __file__)

        self.eye_position = Point(0,0)
        self.in_window_bounds = False

    def get_subscriptions(self):
        return [UI_WINDOW_WINDOWMOVED, UI_WINDOW_WINDOWRESIZED]
    
    def sink(self, event):
        if event.type == UI_WINDOW_WINDOWMOVED:
            self._window_position = Point(event.data['x'], event.data['y']) 
        elif event.type == UI_WINDOW_WINDOWRESIZED:
            self._window_size = Point(event.data['width'], event.data['height']) 
    
    def _internal_callback(self, gaze_data):
        self.eye_position = Point(*self._preprocess_gaze_data(gaze_data))
        self.in_window_bounds = 0 <= self.eye_position.x <= self._window_size.x and 0 <= self.eye_position.y <= self._window_size.y
        self.source(UI_INPUT_EYETRACKING, dict(x = self.eye_position.x, y = self.eye_position.y, in_window_bounds = self.in_window_bounds))
    
    def _preprocess_gaze_data(self, gaze_data): 
        # Extract gaze data for left and right eye (assuming it returns coordinates in the range [0, 1])
        lx, ly = gaze_data['left_gaze_point_on_display_area']
        rx, ry = gaze_data['right_gaze_point_on_display_area']
        ax = (lx + rx) / 2
        ay = (ly + ry) / 2
        ax, ay = self._smoothing(ax, ay) # smooth data by past points...
        # Convert gaze data to screen coordinates
        ax, ay = int(ax * self._screen_size.x), int(ay * self._screen_size.y)
        # convert gaze data to window coordinates
        ax, ay = ax - self._window_position.x, ay - self._window_position.y
        return ax, ay
    
    def draw_debug(self, canvas):
        draw_circle(canvas, self.eye_position.get(), 20, "red")
