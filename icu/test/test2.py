import ICU.event as event


ec = event.new_event_class('warning_light_event', 'click') # state may be: True (on), False (off)

print(ec.labels)
print(ec)
print(ec('test', 0))