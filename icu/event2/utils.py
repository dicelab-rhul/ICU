import time

class ConditionalTimer:
    def __init__(self, interval):
        self.interval = interval
        self.last_execution = time.time()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def should_execute(self):
        current_time = time.time()
        if current_time - self.last_execution >= self.interval:
            self.last_execution = current_time
            return True
        return False