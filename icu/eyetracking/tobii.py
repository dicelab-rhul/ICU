"""
    This module bridges the Tobii (pro) eyetracking API with the ICU event system.
"""

import logging
from .eyetracker import Eyetracker
from ..ui.utils.math import Point

try:
    from tobii_research import EyeTracker as _TobiiEyetracker, EYETRACKER_GAZE_DATA

    TOBII_RESEARCH_EXCEPTION = None
    TOBII_EYETRACKER_AVALIABLE = True
except ModuleNotFoundError as _TOBII_RESEARCH_EXCEPTION:
    TOBII_RESEARCH_EXCEPTION = _TOBII_RESEARCH_EXCEPTION
    TOBII_EYETRACKER_AVALIABLE = False


class TobiiEyetracker(Eyetracker):
    """This class bridges the Tobii (pro) eyetracking API with the ICU event system."""

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

        super().__init__()

        self.uri = uri
        try:
            self._eyetracker = _TobiiEyetracker(uri)  # pylint: disable=E1101
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

    def _internal_callback(self, gaze_data):
        # internal callback that processes the gaze data and adds some additional information - such as whether the eye event was in the bounds of the ICU window.
        self.eye_position, self.eye_position_raw = self._preprocess_gaze_data(gaze_data)
        self.source_eyetracking()

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
