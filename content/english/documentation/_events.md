# EYETRACKING


event(<eye tracker>, Overlay:0, label=<label>, x=<x>, y=<y>)

# GENERATOR

event(TargetEventGenerator, Target:0, label=move, dx=<dx>, dy=<dy>)
event(PumpEventGenerator, <Pump:i>, label=<repair/fail>)
event(WarningLightEventGenerator, <WarningLight:i>, label=switch)
event(ScaleEventGenerator, <Scale:i>, label=slide, slide=<slide>)

# GLOBAL

event(<FuelTank:i>, Global, label=burn, value=<value>)
event(<FuelTank:i>, Global, label=fuel, acceptable=True/False)

event(<Pump:ij>, Global, label=transfer, value=<value>)

event(Target:0, Global, label=move, dx=<dx>, dy=<dy>,  x=<x>, y=<y>)

event(Highlight:<Component:i>, Global, label=highlight, value=True/False)
event(Canvas, <Component:i>), label=click, x=<x>, y=<y>)
event(Keyhandler, Target:0, label=key, key=<key>, keycode=<keycode>, action=<hold/release>)