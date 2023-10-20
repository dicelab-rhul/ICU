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

__all__ = ("filter",)


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
            filter = lambda t, x, y: dict(timestamp=t, x=x, y=y, label="place")

        self.__filter = filter
        self.x, self.y = None, None

    def source(self, x, y, timestamp=None):
        e = self.__filter(timestamp, x, y)
        if e is not None:
            if (
                self.x != e["x"] or self.y != e["y"]
            ):  # only trigger if the eyes moved...
                self.x, self.y = e["x"], e["y"]
                # print(self.x, self.y)
                super().source("Overlay:0", **e)


try:
    from tobii_research import EyeTracker as _TobiiEyetracker, EYETRACKER_GAZE_DATA

    TOBII_RESEARCH_EXCEPTION = None
    TOBII_EYETRACKER_AVALIABLE = True
except ModuleNotFoundError as _TOBII_RESEARCH_EXCEPTION:
    TOBII_RESEARCH_EXCEPTION = _TOBII_RESEARCH_EXCEPTION
    TOBII_EYETRACKER_AVALIABLE = False

# TODO move this as input to the eyetracker class
EYETRACKER_ADDRESS_URI = "tet-tcp://172.28.195.1"


class EyeTracker(EyeTrackerBase):
    def __init__(self, root, filter=None, sample_rate=300, calibrate=True):
        super(EyeTracker, self).__init__(filter)
        self.daemon = True  # ??? TODO any issue with this closing down psychopy?
        print("USING TOBII EYETRACKER!")
        if not TOBII_EYETRACKER_AVALIABLE:
            raise TOBII_RESEARCH_EXCEPTION

        super().__init__()

        self.uri = EYETRACKER_ADDRESS_URI
        try:
            self._eyetracker = _TobiiEyetracker(self.uri)  # pylint: disable=E1101
            self._eyetracker.subscribe_to(
                EYETRACKER_GAZE_DATA,
                self._internal_callback,
                as_dictionary=True,
            )
        except Exception as exception:
            logging.exception("Tobii Eyetracker at uri %s failed to start.", self.uri)
            # TODO do we want to stop execution when this happens? maybe give an option to continue?
            raise exception
        logging.info("Tobii Eyetracker at uri %s created successfully.", self.uri)

        self.sample_rate = sample_rate
        self.tk_root = root

        # self.tk_root.bind("<Configure>", self.tk_update) #TODO some thought here, cannot bind multiple <Configure>..?

        # transform eye tracking coordinates to tk window coordinates
        self.tk_position = (self.tk_root.winfo_x(), self.tk_root.winfo_y())
        self.tk_size = (root.winfo_screenwidth(), self.tk_root.winfo_screenheight())

        self.closed = threading.Event()
        name = f"{EyeTracker.__name__}:{0}"
        self.register(name)

    def tk_update(self, _):
        self.tk_position = (
            self.tk_root.winfo_x(),
            self.tk_root.winfo_y(),
        )  # (event.x, event.y) using the event information has some issues?
        self.tk_size = (
            self.tk_root.winfo_screenwidth(),
            self.tk_root.winfo_screenheight(),
        )

    def _internal_callback(self, gaze_data):
        (x, y), _ = self._preprocess_gaze_data(gaze_data)
        # print(x, y)
        self.source(x=x, y=y)

    def _preprocess_gaze_data(self, gaze_data):
        self.tk_position = (self.tk_root.winfo_x(), self.tk_root.winfo_y())
        self.tk_size = (
            self.tk_root.winfo_screenwidth(),
            self.tk_root.winfo_screenheight(),
        )

        # Extract gaze data for left and right eye (assuming it returns coordinates in the interval [0, 1])
        left_x, left_y = gaze_data["left_gaze_point_on_display_area"]
        right_x, right_y = gaze_data["right_gaze_point_on_display_area"]
        # average left and right
        raw_ax = (left_x + right_x) / 2
        raw_ay = (left_y + right_y) / 2
        # Convert gaze data to screen coordinates
        ax, ay = int(raw_ax * self.tk_size[0]), int(raw_ay * self.tk_size[1])
        # Convert gaze data to window coordinates
        ax, ay = ax - self.tk_position[0], ay - self.tk_position[1]
        return (ax, ay), (raw_ax, raw_ay)

    def close(self):
        self.closed.set()


class EyeTrackerStub(EyeTrackerBase):
    """
    A stub EyeTracker class that uses the current mouse position as a stand in for gaze position,
    use for testing without eyetracking hardware.
    """

    def __init__(self, root, filter=None, sample_rate=300, **kwargs):
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
            sleep(1.0 / self.sample_rate)
            # self.source('Overlay:Overlay', label='move', dx=random.randint(0,10), dy=random.randint(0,10), timestamp=self.__time)
            # if self._p_mouse_x != self._n_mouse_x or self._p_mouse_y != self._n_mouse_y:
            # print(time(), self._n_mouse_x, self._n_mouse_y)
            self.source(x=self._n_mouse_x, y=self._n_mouse_y, timestamp=time())

            self._p_mouse_x = self._n_mouse_x
            self._p_mouse_y = self._n_mouse_y

    def close(self):
        """
        Force the thread to exit.
        """
        self.closed.set()


def eyetracker(
    root, filter=None, sample_rate=300, calibrate=True, stub=False, **kwargs
):
    """Creates a new Eyetracker (there should only ever be one).
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
            return EyeTracker(
                root, filter=filter, sample_rate=sample_rate, calibrate=calibrate
            )
        except Exception as e:
            LOGGER.error("Failed to initialise eyetracker")
            LOGGER.exception(e)

    LOGGER.debug("Using stub eyetracker (MOUSE COORDINATE)")
    return EyeTrackerStub(root, filter=filter, sample_rate=sample_rate)
