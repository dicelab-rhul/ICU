---
title: "Getting Started"
description: ""
draft: false
weight: 1
bg_image: ""
toc : true
---

 <a href="{{<ref download.md >}}" class="btn btn-main"> Download & Install </a>



You can verify your installation by running ICU with the following command:
```
python3 -m ICU
```

This will run the system with the default configuration.

--------------------

## Options

To see all available command line options: `python3 -m icu -help`

--------------------

## Specifying a Configuration file

ICU uses a configuration file to allow users to modified many aspects of the system. The configuration file can be specified with the `-c` option.
```
python -m icu -c config.json
```
For details on configuring ICU see [Configuration]({{< ref "configuration" >}}) below.

--------------------



# Tasks

There are three main tasks for participants in the ICU system designed to test participants attention and task mangagment skills. The tasks are based on a subset of the original MATBII tasks with some slight variations. Each task is described in detail below.


--------------------

<div class="row" style="margin:0px">

<figure style="float:right; margin:20px">
<img src="../images/documentation/system-l.png">
</figure>

## Task: System Monitoring 

### Monitoring Warning Lights

Participants are tasked with keeping warning light (1) in the on state (green)  by clicking when it turns off (grey). At the same time, the second warning light (2) should be kept off (grey) by clicking when it turns on (red). Warning Lights are [configurable]({{< ref "configuration#system-monitoring" >}}). 

### Monitoring Scales

Participants are tasked with keeping the slider in the middle of the 4 sliders each scale (3). The slider will move up or down at pre-set time intervals. Clicking on the slider will reset it to the middle position as can be seen in the right most scale. Scales are [configurable]({{< ref "configuration#system-monitoring" >}}). 

</div>


--------------------


<div class="row" style="margin:0px">


## Task: Fuel Monitoring

### Fuel Tanks

Participants are tasked with keeping the fuel level of the two main tanks (1) within a given range by interacting with the necessary pumps. The fuel in the main, and auxillary tanks (2) will deplete over time. Two of the tanks (3) contain unlimited fuel and can always be used to refill the others. The acceptable fuel range is indicated by the light blue box at each main tank. The main fuel tank values will turn red when the fuel level is out of the acceptable range. Fuel tanks are [configurable]({{< ref "configuration#fuel-monitoring" >}}). 

### Pumps

The eight pumps (4) are used to move fuel between their associated tanks. With the aim of keeping the main tank fuel levels within the acceptable range, participants should attempt to transfer fuel from the infinite tanks to the main tanks. Clicking on a pump will toggle on/off (green/grey). Pumps periodically fail (red), become unusable and stop pumping fuel, after a set period they will be repaired and become useable again starting in the off state. Pumps are [configurable]({{< ref "configuration#fuel-monitoring" >}}).

<figure style="margin:20px; text-align:center;">
<img src="../images/documentation/fuel-l.png">
</figure>

</div>

--------------------


<div class="row" style="margin:0px">

<figure style="float:right; margin:20px;">
<img src="../images/documentation/tracking-l.png">
</figure>

## Task: Tracking

Participants are tasked with keeping the target (1) in the central box (2) using the keyboard or joy stick. The target will slowly drift away from the central box over time.

The target is [configurable]({{< ref "configuration#tracking" >}}). 

</div>






