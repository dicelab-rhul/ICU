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

* `screen_full (bool)` - full screen the ICU window (ignores other screen options). Default: False
* `screen_aspect (tuple)` - fix the aspect ratio of the ICU window. Default: None
* `screen_resizable (bool)` - can the ICU window be resized. Default: True.
* `screen_height (int)` - height of the ICU window. Default: 700.
* `screen_width (int)` - width of the ICU window. Default: 800.
* `screen_size (tuple)` - size of the ICU window. Default [800, 700].
* `screen_min_size (tuple)` - minimum size of the ICU window (ignores aspect ratio). Default: [100,100].
* `screen_max_size (tuple)` - maximum size of the ICU window (ignores aspect ratio). Default: [2000,2000].
* `screen_x (int)` - x position of the ICU window. Default: 0.
* `screen_y (int)` - y position of the ICU window. Default: 0.
* `screen_position (tuple)` - position of the ICU window. Default [0,0].


----------------------------------------- 

## Task Configuration
Tasks can be enabled/disabled using the `task` configuration options:
```
"task" : {
    "system" : true,
    "track" : false,
    "fuel" : false
}
```
The above configuration will disable both the tracking and fuel monitoring tasks, leaving the system monitoring task. All tasks are enabled by default. 

<hr>

## Task: Tracking

### Options
* `step` : distance in pixels moved by the tracking target after each (non-user action) event.
* `invert` : invert controls (true/false).

### Example (1) - Target
```
"Target:0" : { "step" : 2 }
```
In the above configuration, the target will move 2 pixels per `move` event and according to its movement schedule.

<hr>

## Task: Fuel Monitoring

### Options

The fuel monitoring task involves tanks and pumps, each have their own configuration options. Pumps move fuel between their associated tanks. 

#### Tank

Tanks: FuelTank:A, FuelTank:B, FuelTank:C, FuelTank:D, FuelTank:E, FuelTank:F

* `capacity` : the capacity of a tank.
* `fuel` : the initial amount of fuel in a tank.
* `burn_rate` : burn of fuel (units per second) of a main tank.
* `accept_position` : the ideal fuel level for a main tank [0-1].
* `accept_proportion` : the range of fuel values that are acceptable, centered around the ideal fuel value [0-1].

#### Pump

Pumps: Pump:AB, Pump:BA, Pump:FD, Pump:EA, Pump:CA, Pump:EC, Pump:DB, Pump:FB

* `flow_rate` : flow of fuel (units per second) for a pump.
* `event_rate` : frequency of transfer events for a pump.

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

## System Monitoring
### Options: 
* `size` : the size (number of possible slider positions) of a scale (default 11)
* `position` : the initial position of the slider (default 5) 

### Example (1) - Scale Options
```
"Scale:0" : {"size":11, "position":0},
```
In the above configuration, scale 0 will have 11 possible slider position and the slider will start at position 0 (at the top of the scale).

<hr>

## Overlay Configuration

ICU provides support for an overlay, including highlighting widgets, displaying warnings etc. The following options are available under `overlay`.
#### Options
* `transparent (bool)` : transparency value of a highlight box (true for transparent).
* `highlight_colour (bool)` : colour value of a highlight box.
* `highlight_thickness (int)` : thickness of the highlight box outline.
* `outline (bool)` : use an outline for the highlight box.
* `arrow (bool)` : TODO
* `arrow_colour (colour)` : TODO
* `arrow_scale (float)` : TODO

----------------------------------------- 

## Event Configuration
Internal ICU events can be triggered according to schedules defined in the configuration. There are four kinds of schedules that can be specified, single, multi, repeating, and custom. Schedules are specified in the `"schedule`" section of the `config.json` file, for example:
```
{ 
   "schedule":{
        "Scale:0" : 1000,
        "Scale:1" : 1500,
        "Scale:2": 2000,
        "Scale:3": 2500
   }
}

```
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
Takes the form `uniform(a,b)` where `a` and `b` are the lower and upper bounds (int > 0) of the domain, `"Scale:0" : "uniform(0, 1000)"`, will trigger an event at random intervals between 0 and 1 second.
#### Normal Distribution
Takes the form `normal(mu, sigma)` where `mu` and `sigma` are the mean and standard deviation of a Gaussian distribution, `"Scale:0" : "normal(1000,100)"`, will trigger events at random intervals centered around 1000ms. Note that negative sample values are treated as 0 (i.e. immediately trigger the event).

## Cosmetic Options

Many of the display properties of widgets in ICU can be configured, common options include:
* `background_colour` : set the background colour of a widget.
* `outline_colour`    : set the outline colour of a widget. (default black)
* `outline_thickness` : set the outline thickness of a widget (default 3)

All colour options may be specified as a string e.g. `"red"` (see the [full list](http://www.science.smith.edu/dftwiki/index.php/Color_Charts_for_TKinter)) or as a hexadecimal string e.g. `"#ff0000"`.

A number of widgets have specific cosmetic options, below is a comprehensive list.
* `"WarningLight:0" : {"on_colour":"blue", "off_colour":"white", "outline_colour":"green", "outline_thickness":10}`
* `"Scale:0" : {"background_colour":"blue", "outline_colour":"green", "outline_thickness":10, "slider_colour":"white"}`










