
class Clock:
    pulseWidth : int = 10
    clockInterval : int = 20 #full Cycle = pulseWidth + clockInterval
    currentTime : int = 0 #0: descending Pulse

    def __init__(s):
        pass

    def getTime(s) -> int:
        return s.currentTime
    
    def timeStep(s):
        s.currentTime += 1
        if(s.currentTime == s.clockInterval + s.pulseWidth):
            s.currentTime = 0