"""
    This module bridges the Tobii (pro) eyetracking API with the ICU event system.
"""

import logging
from typing import List
from screeninfo import get_monitors

from icu.utils.exception import EventTypeError

from ..event2.event import SinkBase, SourceLocal
from ..ui.commands import (
    UI_INPUT_EYETRACKING,
    UI_WINDOW_WINDOWMOVED,
    UI_WINDOW_WINDOWRESIZED,
)
from ..ui.draw import draw_circle
from ..ui.utils.math import Point

try:
    from tobii_research import EyeTracker as _TobiiEyetracker, EYETRACKER_GAZE_DATA

    TOBII_RESEARCH_EXCEPTION = None
    TOBII_EYETRACKER_AVALIABLE = True
except ModuleNotFoundError as _TOBII_RESEARCH_EXCEPTION:
    TOBII_RESEARCH_EXCEPTION = _TOBII_RESEARCH_EXCEPTION
    TOBII_EYETRACKER_AVALIABLE = False


class TobiiEyetracker(SourceLocal, SinkBase):
    """
    This class bridges the Tobii (pro) eyetracking API with the ICU event system.
    """

    def __init__(self, uri: str, **kwargs):
        """Constructor.

        Raises
        ------
        Exception : (ModuleNotFoundError)
            If the `tobii_research` module could not be found.
        """
        # the module was not found, but someone is trying to create an instance of this class!
        if not TOBII_EYETRACKER_AVALIABLE:
            raise TOBII_RESEARCH_EXCEPTION

        SinkBase.__init__(self)
        SourceLocal.__init__(self)
        self.uri = uri
        try:
            self._eyetracker = _TobiiEyetracker(uri)  # pylint: disable=E1101
            self._eyetracker.subscribe_to(
                EYETRACKER_GAZE_DATA,
                self._internal_callback,
                as_dictionary=True,
            )
        except Exception as exception:
            logging.exception("Eyetracker %s failed to start.", self.uri)
            # TODO do we want to stop execution when this happens? maybe give an option to continue?
            raise exception
        logging.info("Eyetracker %s created successfully.", self.uri)

        monitor = get_monitors()
        assert len(monitor) == 1
        monitor = monitor[0]
        self._screen_size = Point(monitor.width, monitor.height)
        logging.info(
            "Eyetracker %s obtained screen size: %s", self.uri, self._screen_size.get()
        )

        # these should be set before processing eye events?
        self._window_position = Point(0, 0)
        # size of the current icu window.
        self._window_size = Point(1, 1)
        # position of the eyes on the window in window coordinates. (0,0) = window top left, (window_width, window_height) = window bottom right.
        self.eye_position = Point(0, 0)
        # position of the eyes on the screen (0,0) = top left, (1,1) = bottom right.
        self.eye_position_raw = Point(0, 0)
        # flag for whether the eye position is within the window bounds.
        self.in_window_bounds = False

    def get_subscriptions(self) -> List[str]:
        """This [Sink] subscribes to only the [UI_WINDOW_WINDOWMOVED] and [UI_WINDOW_WINDOWRESIZED] event types. These ensure that the eye coordinates are relative to the ICU window.

        Returns:
            List[str]: subscriptions
        """
        # `subscribe` and `unsubscribe` should not be used...
        return [UI_WINDOW_WINDOWMOVED, UI_WINDOW_WINDOWRESIZED]

    def sink(self, event):
        if event.type == UI_WINDOW_WINDOWMOVED:
            self._window_position = Point(event.data["x"], event.data["y"])
        elif event.type == UI_WINDOW_WINDOWRESIZED:
            self._window_size = Point(event.data["width"], event.data["height"])
        else:
            raise EventTypeError(self, event.type)

    def _internal_callback(self, gaze_data):
        # internal callback that processes the gaze data and adds some additional information - such as whether the eye event was in the bounds of the ICU window.
        self.eye_position, self.eye_position_raw = self._preprocess_gaze_data(gaze_data)

        self.in_window_bounds = (
            0 <= self.eye_position.x <= self._window_size.x
            and 0 <= self.eye_position.y <= self._window_size.y
        )
        self.source(
            UI_INPUT_EYETRACKING,
            dict(
                x_raw=self.eye_position_raw.x,
                y_raw=self.eye_position_raw.y,
                x=self.eye_position.x,
                y=self.eye_position.y,
                in_window_bounds=self.in_window_bounds,
            ),
        )

    def _preprocess_gaze_data(self, gaze_data):
        # Extract gaze data for left and right eye (assuming it returns coordinates in the interval [0, 1])
        left_x, left_y = gaze_data["left_gaze_point_on_display_area"]
        right_x, right_y = gaze_data["right_gaze_point_on_display_area"]
        # average left and right
        raw_ax = (left_x + right_x) / 2
        raw_ay = (left_y + right_y) / 2
        # Convert gaze data to screen coordinates
        ax, ay = int(raw_ax * self._screen_size.x), int(raw_ay * self._screen_size.y)
        # Convert gaze data to window coordinates
        ax, ay = ax - self._window_position.x, ay - self._window_position.y
        return Point(ax, ay), Point(raw_ax, raw_ay)

    def draw_debug(self, canvas):
        draw_circle(canvas, self.eye_position.get(), 20, "red")

    def subscribe(self, subscription):
        raise NotImplementedError(
            f"This method should only be called internally by {TobiiEyetracker}"
        )

    def unsubscribe(self, subscription):
        raise NotImplementedError(
            f"This method should only be called internally by {TobiiEyetracker}"
        )
