"""
    Contains the base class for eye trackers. This class should be extended to gather events from a physical eyetracker. See [icu.eyetracking.tobii] for a working example.
"""
from typing import List
from screeninfo import get_monitors

from ..utils.exception import EventTypeError

from ..event2.event import SinkBase, SourceLocal
from ..ui.commands import (
    UI_INPUT_EYETRACKING,
    UI_WINDOW_WINDOWMOVED,
    UI_WINDOW_WINDOWRESIZED,
)
from ..ui.draw import draw_circle
from ..ui.utils.math import Point

from .. import logging


class Eyetracker(SourceLocal, SinkBase):
    """Base class for an eye tracker. This class keeps track of useful fields such as the current window position and size (via the ICU event system). It also provide some useful utility methods."""

    def __init__(self):
        SinkBase.__init__(self)
        SourceLocal.__init__(self)

        monitor = get_monitors()
        assert len(monitor) == 1
        monitor = monitor[0]
        self._screen_size = Point(monitor.width, monitor.height)
        logging.info(
            f"Eyetracker %s obtained screen size: %s", self.id, self._screen_size.get()
        )
        # these should be set before processing eye events?
        self._window_position = None
        # size of the current icu window.
        self._window_size = None
        # position of the eyes on the window in window coordinates. (0,0) = window top left, (window_width, window_height) = window bottom right.
        self.eye_position = Point(0, 0)
        # position of the eyes on the screen (0,0) = top left, (1,1) = bottom right.
        self.eye_position_raw = Point(0, 0)

        # flag for whether the eye position is within the window bounds.
        self.in_window_bounds = False

    def source_eyetracking(self):
        """A helper method for generating an eyetracking event (calls [super().source]).

        The event will contain the various fields of this [Eyetracker] including:
        - [eye_position] : position of the eyes on the window in window coordinates. (0,0) = window top left, (window_width, window_height) = window bottom right.
        - [eye_position_raw] : position of the eyes on the screen (0,0) = top left, (1,1) = bottom right.
        - [in_window_bounds] : flag for whether the [eye_position] is within the current window bounds. The window bounds are determined by listening to events of the following types: [UI_WINDOW_WINDOWMOVED], [UI_WINDOW_WINDOWRESIZED]

        These fields are stored as event data as follows :
        - [eye_position] -> [event.data['x'], event.data['y']]
        - [eye_position_raw] -> [event.data['x_raw'], event.data['y_raw']]
        - [in_window_bounds] -> event.data['in_window_bounds']
        """
        super().source(
            UI_INPUT_EYETRACKING,
            dict(
                x_raw=self.eye_position_raw.x,
                y_raw=self.eye_position_raw.y,
                x=self.eye_position.x,
                y=self.eye_position.y,
                in_window_bounds=self.is_in_window_bounds(self.eye_position),
            ),
        )

    def is_in_window_bounds(self, eye_position: Point):
        """Checks whether the given [eye_position] is within the bounds of the current window.

        Args:
            eye_position (Point): eye position

        Returns:
            bool: whether the given [eye_position] is within the bounds of the current window.
        """
        return (
            0 <= eye_position.x <= self._window_size.x
            and 0 <= eye_position.y <= self._window_size.y
        )

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

    def draw_debug(self, canvas):
        """
            Draw the current eye position.
        Args:
            canvas: to draw to
        """
        draw_circle(canvas, self.eye_position.get(), 20, "red")

    def subscribe(self, subscription):
        raise ValueError(
            f"This method should only be called internally by {Eyetracker}"
        )

    def unsubscribe(self, subscription):
        raise ValueError(
            f"This method should only be called internally by {Eyetracker}"
        )
