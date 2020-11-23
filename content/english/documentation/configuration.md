---
title: "Configuration"
description: ""
draft: false
weight: 2
bg_image: ""
toc : true
---

Many aspects of the ICU can be configured in the `config.json` file. 

## General Configuration

* `screen_width (int, float)` : window width.
* `screen_height (int, float)` : window height.
* `screen_size ` : window size. Default: (800, 700).
* `screen_x (int, float)` : window x position.
* `screen_y (int, float)` : window y position.
* `screen_position ` : window position. Default: (0, 0).
* `screen_full (bool)` : window full screen ?. Default: False.
* `screen_resizable (bool)` : window resizable ?. Default: True.
* `screen_aspect ` : window aspect ratio.
* `screen_min_size ` : minimum window size. Default: (100, 100).
* `screen_max_size ` : maximum window size. Default: (2000, 2000).
* `background_colour (str)` : cosmetic, window background colour. Default: grey.

----------------------------------------- 

## Task Configuration
Tasks can be enabled/disabled using the `task` configuration options:
* `system (bool)` : enable/disable tracking task.
* `track (bool)` : enable/disable system task.
* `fuel (bool)` : enable/disable fuel task.

The above configuration will disable both the tracking and fuel monitoring tasks, leaving the system monitoring task. All tasks are enabled by default. 

<hr>

## Task: Tracking {#tracking}

* `schedule ` : event schedule. Target drift, each event moves the target by `step` amount. Default: schedule: `[[100]]`.
* `step (int, float)` : distance (pixels) the Target moves on each event. Default: 2.
* `invert (bool)` : invert controls for tracking. Default: False.

### Example (1) - Target
```
"Target:0" : { "step" : 2 }
```

In the above configuration, the target will move 2 pixels per `move` event and according to its movement `schedule`.

<hr>

## Task: Fuel Monitoring {#fuel-monitoring}

The fuel monitoring task involves tanks and pumps, each have their own configuration options. Pumps move fuel between their associated tanks. 

### Tank

Tanks: FuelTank:A, FuelTank:B, FuelTank:C, FuelTank:D, FuelTank:E, FuelTank:F

* `burn_rate (int, float)` : rate at which fuel is burnt units/second.
* `accept_position (int, float)` : position of the acceptable level of fuel (for a main tank).
* `accept_proportion (int, float)` : proportion of acceptability of fuel (for a main tank), fuel levels within the range: position +- proportion are acceptable..
* `capacity (int, float)` : capacity of the tank.
* `fuel (int, float)` : initial fuel level.
* `fuel_colour (str)` : cosmetic, colour of the fuel.
* `background_colour (str)` : cosmetic, background colour of the tank.
* `outline_colour (str)` : cosmetic, outline colour of the tank.
* `outline_thickness (int)` : cosmetic, outline thickness of the tank.

### Pump

Pumps: Pump:AB, Pump:BA, Pump:FD, Pump:EA, Pump:CA, Pump:EC, Pump:DB, Pump:FB

* `schedule ` : event schedule. Each event causes the pump to fail/repair (repeating every two events). Default: schedule: `[[uniform(1000,20000)]]`.
* `flow_rate (int)` : transfer rate of fuel from one tank to another (units/second). Default: 100.
* `event_rate (int)` : number of events to trigger /second. Default: 10.
* `scale (float)` : cosmetic, the display scale of the pump.

### Example (1) - Tank Options
```
"FuelTank:A" : {"capacity":2000, "fuel":1000, "burn_rate":10}
```
In the above configuration, tank A will have a maximum capacity of 2000 units of fuel and start with 1000 units of fuel and burn 10 units of fuel per second. Note that only the main tanks (`FuelTank:A` and `FuelTank:B`) can burn fuel.

### Example (2) - Pump Options
```
"Pump:AB" : { "flow_rate": 10, "event_rate": 1}
```
For the above configuration for pump AB, 1 `transfer` event is triggered every second, each event transferring 10 units of fuel from tank A to tank B. Increasing the event rate to 10 would have the effect of 10 events being triggered (uniformly over a 1 second) with each event transferring 1 unit of fuel. Note that higher event rates lead to a smoother fuel animation but at the cost of many more events being generated.

<hr>

## Task: System Monitoring {#system-monitoring}

### Warning Light

Warning Lights: WarningLight:0, WarningLight:1

* `schedule ` : event schedule. Each event switches the light to the undesired state (off for WarningLight:0 and on for WarningLight:1). Default: schedule: `[[uniform(1000,10000)]]`.
* `grace (int, float)` : grace period (the time after which the light may turn on/off after a user has clicked). Default: 2.
* `key (str)` : key-binding shortcut, may be used instead of clicking. Default: 0/1.
* `state (int)` : initial state (on or off). Default: <K>.
* `on_colour (str)` : cosmetic, colour of the on state.
* `off_colour (str)` : cosmetic, colour of the off state.
* `outline_colour (str)` : cosmetic, colour of the outline.
* `outline_thickness (int)` : cosmetic, thickness of the outline.

### Example (1) - Warning Light Options
```
"WarningLight:0" : {"grace":1, "state":0}
```
In the above configuration, the warning light will start in state 0 (off) and will wait at least 1 second before turning back to an undesired state (according to its `schedule`).

### Scale

Scales: Scale:0, Scale:1, Scale:2, Scale:3, ... 

* `schedule ` : event schedule. Each events moves the slider up/down 1 place.. Default: schedule: `[[uniform(1000,10000)]]`.
* `key (str)` : key-binding shortcut, may be used instead of clicking. Default: <K>.
* `size (int)` : size of the scale (number of positions that the slider may be in). Default: 11.
* `position (int)` : initial position of the slider. Default: 5.
* `background_colour (str)` : cosmetic, background colour of the scale.
* `outline_colour (str)` : cosmetic, outline colour of the scale (and slider).
* `outline_thickness (int)` : cosmetic, outline thickness of the scale (and slider).
* `slider_colour (str)` : cosmetic, colour of the slider.


### Example (2) - Scale Options
```
"Scale:0" : {"size":11, "position":0},
```
In the above configuration, scale 0 will have 11 possible slider position and the slider will start at position 0 (at the top of the scale).

<hr>



## Input Configuration

Different types of input can be configured with the following options: 

* `mouse (bool)` : enable/disable mouse input. Default: True.
* `keyboard (bool)` : enable/disable keyboard input. Default: True.
* `joystick (bool)` : enable/disable joystick input. Default: False.

Input also contains a group of options for eye tracking.

### Eye Tracking Configuration

* `enabled (bool)` : enable eye tracking (requires a device to be connected).
* `calibrate (bool)` : calibrate the eye-tracker.
* `sample_rate (int)` : sample rate for the eye-tracker (if configurable on the device).
* `stub (bool)` : use the mouse as a stub for an eye tracking device, functions exactly as an eyetracker (useful for testing).

### Example (1) - Input

```
"input" : { "mouse" : true, 
            "eyetracker" : {
                "enabled" : false,
                "stub" : false }} 
```

The above configuration will enable the mouse as an input method, and completely disable the eye tracking. 

## Overlay Configuration

ICU provides support for an overlay, including highlighting widgets, displaying warnings etc. The following options are available under `overlay`.

* `enable (bool)` : enable/disable overlay (highlighting, arrows etc). Default: True.
* `arrow (bool)` : (IN PROGRESS) enable/disable arrows. Default: True.
* `transparent (bool)` : transparent highlights ?. Default: True.
* `outline (bool)` : outlined highlights ?. Default: True.
* `highlight_thickness (int)` : cosmetic, highlight outline thickness.
* `highlight_colour (str)` : cosmetic, highlight colour.
* `arrow_colour (colour)` : (IN PROGRESS) cosmetic, colour of the arrow
* `arrow_scale (float)` : (IN PROGRESS) cosmetic, scale of the arrow

----------------------------------------- 

## Event Configuration

Internal ICU events can be triggered according to schedules that are defined in the configuration. There are four kinds of schedules that can be specified, single, multi, repeating, and custom. Schedules are specified in the `schedule` option of each component. 

### Single-Event Schedule

A single event schedule is specified simply as an integer, `"Scale:0" : 1000` will cause an event to happen 1000ms after ICU begins.

```
t: 0 ------ 1000 ------ 2000 ------ 3000 ---
e: ---------- | ---------------------------- 
```

### Multi-Event Schedule

Multiple events can be schedules using a list of integer values, specified with square brackets `[ ]`, `"Scale:0" : [1000, 2000]` will trigger an event at 1000ms then wait 2000ms before triggering a second event.

```
t: 0 ------ 1000 ------ 2000 ------ 3000 ---
e: ---------- | --------------------- | ---- 
```

### Repeating-Event Schedule

Events schedules can be repeated by enclosing a list in a second pair of square brackets, `"Scale:0" : [[500, 1000]]`.

```
t: 0 ------- 1000 ------- 2000 ------- 3000 ---
e: ---- | ---------- | ---- | ---------- | ---- 
```

### Custom-Event Schedule

More complex schedules can be specified programmatically by subclassing `icu.config.Distribution`, subclasses will automatically be registered with the config module. Custom schedule are specified in `config.json` as `<name>(<arg1>, <arg2>, ...,<argn>)` where `<name>` is the class name and `<argi>` is an argument for the `__init__` method. Arguments should be parsed by the class. The method `sample(self) -> int` should be defined, which when called returns the time to wait before triggering the next event. 

Some common distributions have been defined for convenience.

#### Uniform Distribution
Takes the form `uniform(a,b)` where `a` and `b` are the lower and upper bounds (int > 0) of the domain, `uniform(0, 1000)`, will trigger an event after a random time in the interval 0-1 seconds.
#### Normal Distribution
Takes the form `normal(mu, sigma)` where `mu` and `sigma` are the mean and standard deviation of a Gaussian distribution, `normal(1000,100)`, will trigger an event at a random time centered around 1000ms. Note that negative sample values are treated as 0 (i.e. immediately trigger the event).

Custom-Event Schedules can be combined with multi or repeating schedules as follows: 

### Example (1) - Pump Scheduling

```
"Pump:AB" : { "schedule": [["uniform(0,10000)",1000]] }
```

In the above, the pump will fail randomly at a time between 0-10 seconds, then wait 1 second before being repaired, and repeat.

-------------------------------

## Cosmetic Options

Many of the display properties of widgets in ICU can be configured, common options include:
* `background_colour` : set the background colour of a widget.
* `outline_colour`    : set the outline colour of a widget. (default black)
* `outline_thickness` : set the outline thickness of a widget (default 3)

All colour options may be specified as a string e.g. `"red"` (see the [full list](http://www.science.smith.edu/dftwiki/index.php/Color_Charts_for_TKinter)) or as a hexadecimal string e.g. `"#ff0000"`.

A number of widgets have specific cosmetic options (see above).










