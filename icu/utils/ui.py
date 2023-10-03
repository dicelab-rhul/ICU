from screeninfo import get_monitors


class _WindowInfo:
    MONITORS = get_monitors()
    MONITOR = MONITORS[0]

    @property
    def screen_size(self):
        return (WindowInfo.MONITOR.width, WindowInfo.MONITOR.height)


WindowInfo = _WindowInfo()

__all__ = ("WindowInfo",)
