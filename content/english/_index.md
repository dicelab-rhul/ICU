---
title: "Integrated Cognitive User assistance (ICU)"
description: ""
draft: false
bg_image: ""
---

# Project

## Aims 
The aim of this project is to provide user assistance in the multi-tasking example scenario based on the MATBII task space developed by NASA.  The attentional workspace of the user is monitored through their interactions and eye movements by and the underlying agent architecture which in turn is able to deploy highlights and gaze contingent arrows to guide the user’s attention.

<br/>  

## Implementation

### [ICU](https://github.com/dicelab-rhul/ICU)
                        
An implementation of MATBII in Python 3.6+ with additional user assistance features. ICU is implemented as an event system that is easy to interface with. Interface meta data and all internal events are exposed via a simple event-based python API. ICU includes support for various kinds of user input - mouse, keyboard, joy stick, eye tracking.

### [ICUa](https://github.com/dicelab-rhul/ICUA)
   
[ICUa](https://github.com/dicelab-rhul/ICUA) is [ICU](https://github.com/dicelab-rhul/ICU) extended with agents implemented in [PyStarWorlds](https://github.com/dicelab-rhul/pystarworlds), an agent environment that supports Python agent applications.  The agents access the ICU display and provide feedback in the form of highlights and arrows according to simple logic based on eye tracking, keyboard, mouse and joystick inputs. 


<br/>

## Funding 

This project is supported by a [Human-Like Computing EPSRC Network+ ](http://hlc.doc.ic.ac.uk/) kickstart grant

<br/>  

## Demos

### EMAS 2021
      
{{< youtube _jvFMK-z8ps >}}

## Papers


S. Durant, B. Wilkins, C. Woods, E. Uliana and K. Stathis. 2021. _Attention Guidance Agents for the MATBII cockpit task._ Engineering Multi-Agent Systems. EMAS 2021. 
