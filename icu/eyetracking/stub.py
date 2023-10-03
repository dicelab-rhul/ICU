""" This module contains a stub eyetracker which may be used for testing when no eyetracker is available. """

import asyncio
import pynput

from ..utils.math import Point
from .eyetracker import Eyetracker


class StubEyetracker(Eyetracker):
    """Stub eye tracker that may be used for testing. It captures mouse movement treating it as if it was eye movement.
    Note that for this stub to work properly, an [asyncio] event loop must be running. A new task is created here that
    produces eye tracking events at a given rate, this will not work if control is not given back to [asyncio]. For
    an example see [icu/test/test_stub_eyetracking.py]."""

    def __init__(self, sample_rate=30):
        super().__init__()
        self._sample_interval = 1 / sample_rate
        # get the initial mouse position
        asyncio.create_task(self._sampler())
        self._mouse_position = Point(*pynput.mouse.Controller().position)
        self._mouse_listener = pynput.mouse.Listener(
            on_move=self._mouse_position_callback
        )
        self._mouse_listener.start()

    def _mouse_position_callback(self, x, y):
        """This method is the callback for the [pynput.mouse.listener]. It receives mouse positions ([x], [y]).

        Args:
            x (float): mouse x position
            y (float): mouse y position
        """
        self._mouse_position = Point(x, y)

    def _internal_callback(self) -> None:
        """This method is periodically called to update the eye position fields based on the current mouse position/window properties."""
        # set the raw eye position
        self.eye_position_raw = Point(
            self._mouse_position[0] / self._screen_size[0],
            self._mouse_position[1] / self._screen_size[1],
        )
        # set the window-relative eye position
        self.eye_position = Point(
            self._mouse_position[0] - self._window_position[0],
            self._mouse_position[1] - self._window_position[1],
        )

    async def _sampler(self):
        """Is called by the [asyncio] event loop, this periodically emits eye tracking events at the given sample rate."""
        while True:
            if self._window_position is not None and self._window_size is not None:
                self._internal_callback()
                self.source_eyetracking()
            await asyncio.sleep(self._sample_interval)
            # await asyncio.sleep(0)
