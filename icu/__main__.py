
import time
import math
import argparse
from datetime import datetime
import random

from .ui import start
from .event2 import load_schedule, EventSystem, SourceLocal, SinkLocal, SourceRemote, SinkRemote
from .event2.utils import ConditionalTimer

from .config import DEFAULT_CONFIGURATION
from .logging import EventLogger

import asyncio

DEFAULT_LOGPATH = "./logs"
DEFAULT_CONFIG = "./config.yaml"
DEFAULT_WAIT = 0.01 # simulation speed...

def start_ui(event_system):
     # this is a remote source that will receive UI events from the UI 
    ui_remote_source = SourceRemote()
    event_system.add_source(ui_remote_source)
    # this is a remote sink that will supply command events to the UI
    # subscriptions will be set remotely in the UI
    ui_remote_sink = SinkRemote()
    ui_remote_sink.subscribe("ICU::*")
    event_system.add_sink(ui_remote_sink)
    ui_process = start(ui_remote_source, ui_remote_sink, DEFAULT_CONFIGURATION) # TODO we dont want to provide the full default configuration!?
    # wait for the ui_process to finish setup before starting the event system
    return ui_process

async def run(event_system):
    ui_process = start_ui(event_system)
    # main loop
    while ui_process.is_alive():
        await asyncio.sleep(DEFAULT_WAIT)
        event_system.pull_events()
        event_system.publish()
    event_system.close()
    ui_process.join()

def start_logger(event_system,logpath, logfile):
    logger = EventLogger(path=logpath, file=logfile)
    logger.subscribe("*")
    event_system.add_sink(logger)
    return logger

def start_local_source(event_system):
    # this is the local source that will produce events for the UI
    icu_event_source = SourceLocal()
    event_system.add_source(icu_event_source)
    return icu_event_source



async def main(cmdargs):

    event_system = EventSystem()
    logger = start_logger(event_system, cmdargs.logpath, cmdargs.log)
    source = start_local_source(event_system)


    printer = SinkLocal(print)
    printer.subscribe("UI::*")
    event_system.add_sink(printer)
   
    schedule = load_schedule("./icu/example_schedule.sch")
    for sch in schedule:
        asyncio.create_task(sch(source))

    await asyncio.create_task(run(event_system))

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Process log files.")
    parser.add_argument("--logpath", help="Location for the event log file. This may be overriden by the --logfile option.", default=DEFAULT_LOGPATH)
    parser.add_argument("--log", help="Path to the event log file. If specified this will override the --logpath option.", default=None)
    parser.add_argument("--config", help="Path to the config file.", default=DEFAULT_CONFIG)
    
    args = parser.parse_args()

    print(args)

    asyncio.run(main(args))



# @scheduler.after(2)
# async def delayed_task():
#     source.source("DELAYED", data=dict(a=1))
#  @scheduler.every(1)
#     async def periodic_task():
#         source.source("ICU::SYSTEMTASK::WARNINGLIGHT2::SET_PROPERTY", data=dict(state=random.randint(0,1)))
# asyncio.create_task(delayed_task())
# asyncio.create_task(periodic_task())
