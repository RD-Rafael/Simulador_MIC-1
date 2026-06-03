
class UpdateEntry:
    def __init__(s, component : Component, caller : Component, timeIdx : int):
        s.component = component
        s.caller = caller
        s.timeIdx = timeIdx


class Component:
    def __init__(s, updateDelay : int, label :str):
        s.updateDelay = updateDelay
        s.label = label
        s.dependents : list[Component] = []

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
        super().__init__(updateDelay, label)
        s.outBits = BitData(length)

    def update(s, currentTime : int, caller : Component) -> list[UpdateEntry]:
        #assumindo que não haverá mais de um componente escrevendo no bus
        #update stats
        s.outBits.copyBits(caller.outBits)
        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime))
        return updateList

class Line(Component): # A bus that only takes a section of the input bits
    def __init__(s, updateDelay: int, label: str, length :int, offset :int):
        super().__init__(updateDelay, label)
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
        return updateList

class RWRegister(Component): #Read & write register
    def __init__(s, updateDelay: int, label: str, length :int):
        super().__init__(updateDelay, label)
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
                    return []
                else:
                    s.enableInput = True
                    return []
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
                        return []
                else:
                    return []

        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime))
        return updateList


class FlipFlop(Component):
    def __init__(s, updateDelay: int, label: str):
        super().__init__(updateDelay, label)
        s.outBits = BitData(1)
        s.inBits = BitData(1)

    def update(s, currentTime : int, caller : Component) -> list[UpdateEntry]:
        #update stats
        if(caller.label == "Clock"):
            s.outBits.copyBits(s.inBits)
        else:
            s.inBits.copyBits(caller.outBits)
            return []

        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime))
        return updateList

class HighBit(Component):
    def __init__(s, updateDelay: int):
        super().__init__(updateDelay, "HighBit")
        s.outBits = BitData(1)
        s.JAMNZBits = BitData(2)
        s.NFFBit = BitData(1)
        s.ZFFBit = BitData(1)

    def update(s, currentTime : int, caller : Component) -> list[UpdateEntry]:
        #update stats
        match caller.label:
            case "NFF":
                s.NFFBit.copyBits(caller.outBits)
            case "ZFF":
                s.ZFFBit.copyBits(caller.outBits)
            case "JAMNZ line":
                s.JAMNZBits.copyBits(caller.outBits)

        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime))
        return updateList

class ALU(Component):
    def __init__(s, updateDelay: int):
        super().__init__(updateDelay, "ALU")
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
        return updateList

class Shifter(Component):
    def __init__(s, updateDelay: int):
        super().__init__(updateDelay, "Shifter")
        s.controlBits = BitData(2) 
        s.inBits = BitData(32)
        s.outBits = BitData(32) 

    def update(s, currentTime : int, caller : Component) -> list[UpdateEntry]:
        #update stats
        match caller.label:
            case "ALU":
                s.inBits.copyBits(caller.outBits)
                pass
            case "Shifter control line":
                s.controlBits.copyBits(caller.outBits)
                pass

        #CALCULAR OUTBITS NOVAMENTE
        s.outBits.copyBits(s.inBits)
        #############

        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime))
        return updateList


class ORUnit(Component):
    def __init__(s, updateDelay :int):
        super().__init__(updateDelay, "ORUnit")
        s.JMPCValue = 0 
        s.nextAddrBits = BitData(9)
        s.MBRBits = BitData(8)
        s.outBits = BitData(9)
    
    def update(s, currentTime: int, caller : Component) -> list[UpdateEntry]:
        #update stats
        match caller.label:
            case "JMPC line":
                s.JMPCValue = caller.outBits.bits[0]
                pass
            case "MBR":
                s.MBRBits.copyBits(caller.inBits)
                pass
            case "Addr line":
                s.nextAddrBits.copyBits(caller.outBits)
                pass

        #CALCULAR OUTBITS NOVAMENTE
        if s.JMPCValue:
            s.outBits.bits[0] = s.nextAddrBits[0]
            for i in range(8):
                s.outBits[i+1] = s.MBRBits[i+1] or s.nextAddrBits[i+1]
        else:
            s.outBits.copyBits(s.nextAddrBits)
        #############

        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime))
        return updateList


class MPC(Component):
    def __init__(s, updateDelay: int):
        super().__init__(updateDelay, "MPC")
        s.outBits = BitData(9) 

    def update(s, currentTime : int, caller : Component) -> list[UpdateEntry]:
        #update stats
        match caller.label:
            case "ORUnit":
                for i in range(8):
                    s.outBits.bits[i+1] = caller.outBits.bits[i]
                pass
            case "HighBit":
                s.outBits.bits[0] = caller.outBits.bits[0] or s.outBits.bits[0]
                
                pass

        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime))
        return updateList

class ControlMemory(Component):
    def __init__(s, updateDelay: int):
        super().__init__(updateDelay, "MIR")
        s.bits = BitData(512*36)
        s.MPCBits = BitData(9)
        s.outBits = BitData(36)
        s.currentAddress = BitData(9)

    def update(s, currentTime : int, caller : Component) -> list[UpdateEntry]:
        #update stats
        match caller.label:
            case "Clock":
                s.currentAddress.copyBits(s.MPCBits)
                addressInteger : int = s.currentAddress.toInteger()
                s.outBits.copyBitSection(s.bits, addressInteger)
                pass
            case "MPC bus":
                s.MPCBits.copyBits(caller.outBits)
                return []
            case _:
                raise Exception("controlMemory's caller is not the Clock or MPC bus")
                return []

        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime))
        return updateList

class MIR(Component):
    def __init__(s, updateDelay: int):
        super().__init__(updateDelay, "MIR")
        s.outBits = BitData(36) 

    def update(s, currentTime : int, caller : Component) -> list[UpdateEntry]:
        #update stats
        s.outBits.copyBits(caller.outBits)

        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime))
        return updateList

class Decoder(Component):
    def __init__(s, updateDelay: int):
        super().__init__(updateDelay, "Decoder")
        s.inBits = BitData(4)
        s.outBits = BitData(9)
    

    def update(s, currentTime : int, caller : Component) -> list[UpdateEntry]:
        #update stats
        s.inBits.copyBits(caller.outBits)

        s.outBits.clear()
        s.outBits.bits[s.inBits.toInteger()] = 1

        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime))
        return updateList


class MBR(Component):
    def __init__(s, updateDelay: int):
        super().__init__(updateDelay, "MBR")
        s.inBits = BitData(8) 
        s.outBits = BitData(32) 

    def update(s, currentTime : int, caller : Component) -> list[UpdateEntry]:
        #update stats
        #dependendo do enable output o outBits muda
        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime))
        return updateList

class H(Component): #H register
    def __init__(s, updateDelay: int):
        super().__init__(updateDelay, "H")
        s.comingBits = BitData(32)
        s.inBits = BitData(32)
        s.outBits = BitData(32)
        s.enableInput: bool = False
        s.enableOutput: bool = True
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
        return updateList


class Memory(Component):
    def __init__(s, updateDelay: int):
        super().__init__(updateDelay, "Memory")
        s.memoryBits = BitData(2048*32)
        #tamanhos provisórios
        s.MARBits = BitData(10)
        s.MDRBits = BitData(32)
        s.PCBits = BitData(32)

    def update(s, currentTime : int, caller : Component) -> list[UpdateEntry]:
        #update stats
        match caller.label:
            case "Clock":
                pass
            case "MAR":
                pass
            case "MBR":
                pass
            case "PC":
                pass

        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime))
        return updateList

