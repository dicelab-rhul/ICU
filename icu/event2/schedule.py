import time
import asyncio
import pathlib
import ast
import re 

from typing import Union
from dataclasses import dataclass

from ..exception import ConfigurationError
from ..config.distribution import get_distribution_cls

__all__ = ("load_schedule",)

@dataclass()
class Const:
    value : Union[float, int, str]
    def __call__(self):
        return self.value
    
@dataclass()
class Collection:
    value : Union[list, tuple]
    def __init__(self, value : Union[list, tuple]):
        self.value = [_get_function(x) for x in value]
    def __call__(self):
        return [x() for x in self.value]
    def __iter__(self):
        for x in self.value:
            yield x()
    def cycle(self, repeat=None):
        if repeat is not None:
            for i in range(repeat):
                yield from self
        else:
            while True: # 
                yield from self
    
@dataclass()
class Map:
    value : dict
    def __init__(self, value : dict):
        self.value = {k:_get_function(v) for k,v in value.items()}
    def __call__(self):
        return {k:v() for k,v in self.value.items()}
    
# used to construct the above class and resolve any functions
def _get_function(x):
    if isinstance(x, str) and x.startswith("!"):
        name, args = re.findall("!(\w+)(\(.*\))", x)[0]
        args = [_get_function(z) for z in ast.literal_eval(args)] # recursively resolve functions if needed
        cls = get_distribution_cls(name)
        return cls(*args)
    elif isinstance(x, (list, tuple)):
        return Collection(x)
    elif isinstance(x, dict):
        return Map(x)
    elif isinstance(x, (int, float, str)):
        return Const(x)
    elif x is None:
        return Const(x)
    else:
        raise ConfigurationError(f"Invalid data type: {type(x)} encountered while parsing schedule.")

class Schedule:

    def __init__(self, schedule : Collection, repeat, event_type, data):
        super().__init__()
        assert isinstance(schedule, Collection)
        self.schedule = schedule
        self.repeat = repeat
        self.event_type = event_type
        self.data = data

    async def __call__(self, source):
        for interval in self.schedule.cycle(self.repeat()):
            await asyncio.sleep(interval)
            event_type, data = self.event_type(), self.data()
            source.source(event_type, data)

    def parse_schedule(schedule, event_type : Const, data : Map):
        if len(schedule) == 0:
            raise ConfigurationError(f"Invalid schedule {schedule} cannot be empty.")
        elif len(schedule) == 1: 
            if isinstance(schedule[0], (int, float, str)): # schedule once
                return Schedule(Collection([schedule[0]]), Const(1), event_type, data) 
            elif isinstance(schedule[0], (list, tuple)): # repeat forever task
                return Schedule (Collection(schedule[0]), Const(None), event_type, data)
            else:
                raise ConfigurationError(f"Invalid schedule {schedule}")
        elif len(schedule) == 2:
            if isinstance(schedule[0], (int, float, str)): # schedule once
                return Schedule(Collection(schedule), Const(1), event_type, data) 
            elif isinstance(schedule[0], (list, tuple)): # schedule multiple
                sch, repeat = schedule
                return Schedule(Collection(sch), _get_function(repeat), event_type, data)
        else:
            return Schedule(Collection(schedule), Const(1), event_type, data) # schedule once
        # unreachable? 
        raise ConfigurationError(f"Invalid schedule {schedule}, must be of the form [*interval], or [[*intervals], ?repeat]. See documentation for further details.")


def load_schedule2(file): # TODO each element is contained in a line... what about multi-line? 
    file = pathlib.Path(file).expanduser().resolve().absolute()
    schedules = []
    with open(str(file), 'r') as sfile:
        for line in sfile.readlines():
            line = line.strip()
            if len(line) == 0 or line.startswith("#"):
                continue
            literals = list(ast.literal_eval(line))
            event_type, data, schedule = literals
            if not isinstance(event_type, str):
                raise ConfigurationError(f"event type {event_type} must be a string, found type {type(event_type)}.")
            event_type = Const(event_type)
            data = Map(data) # parse the map
            schedule = Schedule.parse_schedule(schedule, event_type, data)
            schedules.append(schedule)
    return schedules

def load_schedule(file): # TODO each element is contained in a line... what about multi-line? 
    file = pathlib.Path(file).expanduser().resolve().absolute()
    schedules = []

    def get_schedule(line):
        literals = list(ast.literal_eval(line))
        event_type, data, schedule = literals
        if not isinstance(event_type, str):
            raise ConfigurationError(f"event type {event_type} must be a string, found type {type(event_type)}.")
        event_type = Const(event_type)
        data = Map(data) # parse the map
        return Schedule.parse_schedule(schedule, event_type, data)

    from pprint import pprint

    with open(str(file), 'r') as sfile:
        lines = [line.strip() for line in sfile.readlines()]
        lines = [line for line in lines if not len(line) == 0 and not line.startswith("#")]

        result = []
        current_line = ''
        for item in lines:
            if item.endswith("\\"):
                current_line += item[:-1].strip()  # Remove trailing "\\"
            else:
                current_line += item
                result.append(current_line)
                current_line = ''
            
        #for line in result:
        #    print(line)
        return [get_schedule(line) for line in result]
        
### OLD SCHEDULEING 

# class TaskRepeatable:

#     def __init__(self, fun, interval, repeat):
#         self.fun = fun
#         self.interval = interval
#         self.repeat = repeat

#     async def __call__(self):
#         if self.repeat is not None:
#             for _ in range(self.repeat):
#                 await asyncio.sleep(self.interval)
#                 await self.fun()
#         else:
#             while True:
#                 await asyncio.sleep(self.interval)
#                 await self.fun()

# class Scheduler:

#     def __init__(self):
#         pass 
#     def after(self, interval):
#         return self.every(interval, repeat=1)

#     def every(self, interval, repeat=None):
#         def decorator(task_func):
#             task = TaskRepeatable(task_func, interval, repeat)
#             return task
#         return decorator

    
# async def main():
#     scheduler = Scheduler()

#     @scheduler.after(2)
#     async def delayed_task():
#         print("Delayed task executed", time.strftime('%X'))

#     @scheduler.every(1)
#     async def periodic_task():
#         print("Periodic task executed", time.strftime('%X'))

#     print("START: ", time.strftime('%X'))
#     asyncio.create_task(delayed_task())
#     asyncio.create_task(periodic_task())

#     await asyncio.sleep(5)  # Run for 10 seconds
#     print("DONE: ", time.strftime('%X'))



# if __name__ == "__main__":
#     asyncio.run(main())
