
from icu.event2 import EventSystem, SourceLocal, SinkLocal


es = EventSystem()

source = SourceLocal()
sink = SinkLocal(print)

es.add_source(source)
es.add_sink(sink)

source.source("A::B::C", dict(a=1))
source.source("A::C::C", dict(a=2))
source.source("A::D::E", dict(a=3))
source.source("A::D::F", dict(a=4))
source.source("A", dict(a=5))

sink.subscribe("A::*::C")

sink.subscribe("A::B")






es.pull_events()
es.publish()


