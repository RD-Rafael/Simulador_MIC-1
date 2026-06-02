
class UpdateEntry:
    def __init__(s, component : Component, caller : Component, timeIdx : int):
        s.component = component
        s.caller = caller
        s.timeIdx = timeIdx


class Component:
    updateDelay : int
    dependents : list[Component] = []
    label : str = ""
    def __init__(s, updateDelay : int, label :str):
        s.updateDelay = updateDelay
        s.label = label

    def update(s, currentTime : int, caller : Component) -> list[UpdateEntry]:
        #update stats

        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime))

    def addDependent(s, dependent : Component):
        s.dependents.append(dependent)

class BitData():
    def __init__(s, length: int):
        s.length = length
        s.bits : list[int] = [0]*length

    def copyBits(s, bitData : BitData):
        if(bitData.length != s.length):
            raise Exception("bitDatas have different sizes when copying")
        for i in range(s.length):
            s.bits[i] = bitData.bits[i]

    def copyBitSection(s, bitData : BitData, offset: int):
        if(bitData.length - offset < s.length):
            raise Exception("bitData doesnt have enough bits to copy")
        for i in range(s.length):
            s.bits[i] = bitData.bits[i+offset]
    
    def clear(s):
        for i in range(s.length):
            s.bits[i] = 0
    
    def toInteger(s) -> int:
        bit : int = 1
        ans : int = 0
        for i in range(s.length):
            if (s.bits[s.length - i - 1]  == 1):
                ans += bit
            bit = bit << 1
        return ans

class Bus(Component):
    def __init__(s, updateDelay: int, label: str, length :int):
        super.__init__(updateDelay, label)
        s.outBits = BitData(length)

    def update(s, currentTime : int, caller : Component) -> list[UpdateEntry]:
        #assumindo que não haverá mais de um componente escrevendo no bus
        #update stats
        s.outBits.copyBits(caller.outBits)
        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime))

class Line(Component): # A bus that only takes a section of the input bits
    def __init__(s, updateDelay: int, label: str, length :int, offset :int):
        super.__init__(updateDelay, label)
        s.outBits = BitData(length)
        s.offset = offset
    def update(s, currentTime : int, caller : Component) -> list[UpdateEntry]:
        #assumindo que não haverá mais de um componente escrevendo no bus
        #update stats
        s.outBits.copyBitSection(caller.outBits, s.offset)
        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime))

class RWRegister(Component): #Read & write register
    def __init__(s, updateDelay: int, label: str, length :int):
        super.__init__(updateDelay, label)
        s.comingBits = BitData(length)
        s.inBits = BitData(length)
        s.outBits = BitData(length)
        s.enableInput: bool = False
        s.enableOutput: bool = False
    def update(s, currentTime : int, caller : Component) -> list[UpdateEntry]:
        #update stats
        match caller.label:
            case "enable input":
                if caller.outBits.bits[0] == 0:
                    s.enableInput = False
                    return
                else:
                    s.enableInput = True
                    return
            case "enable output":
                if caller.outBits.bits[0] == 0:
                    s.enableOutput = False
                    s.outBits.clear()
                else:
                    s.enableOutput = True
                    s.outBits.copyBits(s.inBits)
            case "C bus":
                s.comingBits.copyBits(caller.outBits)
            case "Clock":
                if (s.enableInput):
                    s.inBits.copyBits(s.comingBits)
                    if (s.enableOutput):
                        s.outBits.copyBits(s.inBits)
                    else:
                        return
                else:
                    return

        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime))


class FlipFlop(Component):
    def __init__(s, updateDelay: int, label: str, inputBitIdx : int):
        super.__init__(updateDelay, label)
        s.outBits = BitData(1)
        s.inBits = BitData(1)
        s.inputBitIdx = inputBitIdx

    def update(s, currentTime : int, caller : Component) -> list[UpdateEntry]:
        #update stats
        if(caller.label == "Clock"):
            s.outBits.copyBits(s.inBits)
        else:
            s.inBits.copyBits(caller.outBits)
            return

        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime))



class ALU(Component):
    def __init__(s, updateDelay: int):
        super.__init__(updateDelay, "ALU")
        s.BitsA = BitData(32) 
        s.BitsB = BitData(32) 
        s.outBits = BitData(32) 

    def update(s, currentTime : int, caller : Component) -> list[UpdateEntry]:
        #update stats
        match caller.label:
            case "A bus":
                s.BitsA.copyBits(caller.outBits)
                pass
            case "B bus":
                s.BitsB.copyBits(caller.outBits)
                pass
            case "ALU control line":
                #changes operation
                pass

        #CALCULAR OUTBITS NOVAMENTE
        #############

        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime))


class controlMemory(Component):
    def __init__(s, updateDelay: int, MPCRegister : Component):
        super.__init__(updateDelay, "Control Memory")
        s.bits = BitData(512*36)
        s.outBits = BitData(36)
        s.currentAddress = BitData(9)
        s.MPCregister = MPCRegister

    def update(s, currentTime : int, caller : Component) -> list[UpdateEntry]:
        #update stats
        match caller.label:
            case "Clock":
                s.currentAddress.copyBits(s.MPCRegister.outBits)
                addressInteger : int = s.currentAddress.toInteger()
                s.outBits.copyBitSection(s.bits, addressInteger)
                pass
            case _:
                raise Exception("controlMemory's caller is not the Clock")
                return

        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime))
