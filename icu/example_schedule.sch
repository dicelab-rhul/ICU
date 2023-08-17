

# example of setting initial properties (multi-line requires a `\`)
"ICU::TRACKINGTASK::TARGET::SET_PROPERTY", { "set" : {  \
                                                "scale" : (1,1), \
                                                "position" : (100,100) } \ 
                                            }, [0]




# Schedule for the tracking task that will make the target move around
"ICU::TRACKINGTASK::TARGET::SET_PROPERTY", { "response" : False, "set" : { "+position" : ("!uniform(-5,5)", "!uniform(-5,5)") }}, [[0.1]]

# Schedule for the WARNINGLIGHT1 
"ICU::SYSTEMTASK::WARNINGLIGHT1::SET_PROPERTY", { "response" : False, "set" : {"+state" : 1 }}, [[1]]

# Schedule for the WARNINGLIGHT2 
"ICU::SYSTEMTASK::WARNINGLIGHT2::SET_PROPERTY", { "response" : False, "set" : {"+state" : 1 }}, [[1]]

# Schedule for SLIDER1
"ICU::SYSTEMTASK::SLIDER1::SET_PROPERTY", { "response" : False, "set" : {"+state" : "!uniform(-1,1)" }}, [[1]]

# Schedule for SLIDER2
"ICU::SYSTEMTASK::SLIDER2::SET_PROPERTY", { "response" : False, "set" : {"+state" : "!uniform(-1,1)" }}, [[1]]

# Schedule for SLIDER3
"ICU::SYSTEMTASK::SLIDER3::SET_PROPERTY", { "response" : False, "set" : {"+state" : "!uniform(-1,1)" }}, [[1]]

# Schedule for SLIDER4
"ICU::SYSTEMTASK::SLIDER4::SET_PROPERTY", { "response" : False, "set" : {"+state" : "!uniform(-1,1)" }}, [[1]]


# "ICU::TRACKINGTASK::TARGET::SET_PROPERTY", { "scale" : ("!uniform(0.5,2.0)", "!uniform(0.5,2.0)") }, [[1]]                                      



# "ICU::TRACKINGTASK::GET_PROPERTY", { "child_addresses" : None }, [1]
# "ICU::SYSTEMTASK::GET_PROPERTY", { "child_addresses" : None }, [1]

#"ICU::SYSTEMTASK::WARNINGLIGHT2::SET_PROPERTY", { "set" : { "state" : "!uniform(0,1)" }}, [1] # execute once after 1 second,
#"ICU::SYSTEMTASK::WARNINGLIGHT2::SET_PROPERTY", { "set" : { "state" : "!uniform(0,1)" }}, [1,0.5] # execute once after 1 second then again 0.5 seconds later
#"ICU::SYSTEMTASK::WARNINGLIGHT2::SET_PROPERTY", { "set" : { "state" : "!uniform(0,1)" }}, [[0.1,0.2]] # execute once after 1 second then again 0.5 seconds later
#"ICU::SYSTEMTASK::WARNINGLIGHT2::SET_PROPERTY", { "set" : { "state" : "!uniform(0,1)" }}, [[0.1],10] # repeat 10 times, 0.1 second intervals
#"ICU::SYSTEMTASK::WARNINGLIGHT2::SET_PROPERTY", { "set" : { "state" : "!uniform(0,1)" }}, [[0.1,0.2],5] # repeat 5 times, at 0.1 and 0.2 second intervals (i.e. execute at 1s, 3s, 4s, 6s, ...)
#"ICU::SYSTEMTASK::WARNINGLIGHT2::SET_PROPERTY", { "set" : { "state" : "!uniform(0,1)" }}, [[0.2]] # repeat forever every 0.2 seconds
#"ICU::SYSTEMTASK::WARNINGLIGHT2::SET_PROPERTY", { "set" : { "state" : "!uniform(0,1)" }}, [["!uniform(0,0.5)"]]




#"ICU::TRACKINGTASK::TARGET::SET_PROPERTY", { "line_width" : 10 }, [1]

