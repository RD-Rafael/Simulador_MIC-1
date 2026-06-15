from components import debug

class Clock:
    pulseWidth : int = 24
    clockInterval : int = 52 #full Cycle = pulseWidth + clockInterval
    currentTime : int = 0 #0: descending Pulse

    def __init__(s):
        pass

    def getTime(s) -> int:
        if(debug and s.currentTime == 0):
            print("=======!!")
            print("descendingPulse")
            print("=======!!")
        elif(debug and s.currentTime == s.clockInterval):
            print("=======!!")
            print("ascendingPulse")
            print("=======!!")
        return s.currentTime
    
    def timeStep(s):
        s.currentTime += 1
        if(s.currentTime == s.clockInterval + s.pulseWidth):
            s.currentTime = 0