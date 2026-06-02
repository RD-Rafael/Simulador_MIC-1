import queue
from clock import Clock
from components import *


class UpdateSequencer:
    clock : Clock = Clock()
    pendingUpdates : dict[int, list[UpdateEntry]] = dict()

    def __init__(s):
        pass

    def Update(s):
        currTime : int = s.clock.getTime()
        updatesForNow = s.pendingUpdates[currTime]
        for entry in updatesForNow:
            newUpdates : list[UpdateEntry] = entry.component.update(currTime, entry.caller)
            for newEntry in newUpdates:
                s.pendingUpdates[currTime + newEntry.component.updateDelay].append(newEntry)

        s.pendingUpdates[currTime] = []
        s.clock.timeStep()
                