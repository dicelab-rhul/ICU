## ICU - TODO full name...

An striped down implementation of [MATBII](https://matb.larc.nasa.gov/) in Python 3.7+. ICU is written in pure python (no external dependancies) and so is easy to install (TODO: pip install icu).

ICU implemented as an event system that is easy to interface with.

### MORE INFORMATION ON THE WAY.




### config.json

A configuration file 'config.json' to set up various aspects of the system. 

#### General Options

* screen_width : (int, float) width of the ICU window
* screen_height : (int, float) height of the ICU window
* screen_x : (int, float) x position of the ICU window
* screen_y : (int, float) y position of the ICU window
* screen_full : (bool) fullscreen or not (overrides other screen config)

#### Event Scheduling

##### Options

* schedule_warning_light : (int, list, str) schedule for warning lights SystemMonitorWidget
* schedule_scale : (int, list, str) schedule for scale(s) in SystemMonitorWidget
* schedule_tracking : (int, list, str) schedule for target movement in TrackingWidget

##### Schedules

A schedule can be specified in three ways:

###### Constant (int, float)


###### 



