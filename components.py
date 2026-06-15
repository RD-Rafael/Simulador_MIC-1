import queue
def xor(A: int, B : int):
    return not ( (A and B) or (not ((B) or (A))) )

class UpdateEntry:
    def __init__(s, component : Component, caller : Component, timeIdx : int, information : BitData):
        s.component = component
        s.caller = caller
        s.timeIdx = timeIdx
        s.information = information

class Component:
    def __init__(s, updateDelay : int, label :str):
        s.updateDelay = updateDelay
        s.label = label
        s.dependents : list[Component] = []

    def update(s, currentTime : int, entry: UpdateEntry) -> list[UpdateEntry]:
        caller = entry.caller
        #update stats

        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime, None))

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
    
    def _setBitsFromInt(s, value : int):
        for i in range(s.length):
            s.bits[i] = 1 if bool(value & (1 << (s.length) - i - 1)) else 0

class Bus(Component):
    def __init__(s, updateDelay: int, label: str, length :int):
        super().__init__(updateDelay, label)
        s.outBits = BitData(length)

    def update(s, currentTime : int, entry : UpdateEntry) -> list[UpdateEntry]:
        caller = entry.caller
        #assumindo que não haverá mais de um componente escrevendo no bus
        #update stats
        s.outBits.copyBits(caller.outBits)
        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime, None))
        return updateList

class Line(Component): # A bus that only takes a section of the input bits
    def __init__(s, updateDelay: int, label: str, length :int, offset :int):
        super().__init__(updateDelay, label)
        s.outBits = BitData(length)
        s.offset = offset
    def update(s, currentTime : int, entry: UpdateEntry) -> list[UpdateEntry]:
        caller = entry.caller
        #assumindo que não haverá mais de um componente escrevendo no bus
        #update stats
        s.outBits.copyBitSection(caller.outBits, s.offset)
        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        currentOutBits = BitData(s.outBits.length)
        currentOutBits.copyBits(s.outBits)
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime, currentOutBits))
        return updateList

class RWRegister(Component): #Read & write register
    def __init__(s, updateDelay: int, label: str, length :int):
        super().__init__(updateDelay, label)
        s.comingBits = BitData(length)
        s.inBits = BitData(length)
        s.outBits = BitData(length)
        s.enableInput: bool = False
        s.enableOutput: bool = False
    def update(s, currentTime : int, entry: UpdateEntry) -> list[UpdateEntry]:
        caller = entry.caller
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
                    return []
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
            case __:
                return []
                
        if(not s.enableOutput):
            return []

        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime, None))
        return updateList

class FlipFlop(Component):
    def __init__(s, updateDelay: int, label: str):
        super().__init__(updateDelay, label)
        s.outBits = BitData(1)
        s.inBits = BitData(1)

    def update(s, currentTime : int, entry: UpdateEntry) -> list[UpdateEntry]:
        caller = entry.caller
        #update stats
        if(caller.label == "Clock"):
            s.outBits.copyBits(s.inBits)
        else:
            s.inBits.copyBits(caller.outBits)
            return []

        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime, None))
        return updateList

class HighBit(Component):
    def __init__(s, updateDelay: int):
        super().__init__(updateDelay, "HighBit")
        s.outBits = BitData(1)
        s.JAMNZBits = BitData(2)
        s.NFFBit = BitData(1)
        s.ZFFBit = BitData(1)

    def update(s, currentTime : int, entry: UpdateEntry) -> list[UpdateEntry]:
        caller = entry.caller
        #update stats
        match caller.label:
            case "NFF":
                s.NFFBit.copyBits(caller.outBits)
            case "ZFF":
                s.ZFFBit.copyBits(caller.outBits)
            case "JAMNZ line":
                s.JAMNZBits.copyBits(caller.outBits)

        N = s.NFFBit.bits[0]
        Z = s.ZFFBit.bits[0]
        JAMN = s.JAMNZBits.bits[0]
        JAMZ = s.JAMNZBits.bits[1]

        F = 1 if (JAMZ and Z) or (JAMN and N) else 0
        s.outBits.bits[0] = F

        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime, None))
        return updateList

class ALU(Component):
    def __init__(s, updateDelay: int):
        super().__init__(updateDelay, "ALU")
        s.BitsA = BitData(32) 
        s.BitsB = BitData(32)
        s.inA = BitData(32)
        s.inB = BitData(32)
        s.outBits = BitData(32)
        s.F0 = 0
        s.F1 = 0
        s.ENA = 0
        s.ENB = 0
        s.INVA = 0
        s.INC = 0

    def update(s, currentTime : int, entry : UpdateEntry) -> list[UpdateEntry]:
        caller = entry.caller
        #update stats
        match caller.label:
            case "A bus":
                s.BitsA.copyBits(caller.outBits)
                pass
            case "B bus":
                s.BitsB.copyBits(caller.outBits)
                pass
            case "ALU control line":
                s.F0 = caller.outBits.bits[0]
                s.F1 = caller.outBits.bits[1]
                s.ENA = caller.outBits.bits[2]
                s.ENB = caller.outBits.bits[3]
                s.INVA = caller.outBits.bits[4]
                s.INC = caller.outBits.bits[5]

        F0 = s.F0
        F1 = s.F1
        ENA = s.ENA
        ENB = s.ENB
        INVA = s.INVA
        INC = s.INC
        if(ENA):
            s.inA.copyBits(s.BitsA)
        else:
            s.inA.clear()

        if(ENB):
            s.inB.copyBits(s.BitsB)
        else:
            s.inB.clear()
        
        if(INVA):
            for i in range(s.inA.length):
                s.inA.bits[i] = 0 if s.inA.bits[i] else 1
        
        if(F0 == 0 and F1 == 0):
            #soma
            carry = INC
            for i in range(s.inA.length):
                idx = s.inA.length - i -1
                bitA = s.inA.bits[idx]
                bitB = s.inB.bits[idx]
                S = 1 if xor(xor(bitA, bitB), carry) else 0
                carry = 1 if (bitA and bitB) or (xor(bitA, bitB) and (carry)) else 0
                s.outBits.bits[idx] = S
        if(F0 == 0 and F1 == 1):
            #OR
            for idx in range(s.inA.length):
                bitA = s.inA.bits[idx]
                bitB = s.inB.bits[idx]
                s.outBits.bits[idx] = 1 if bitA or bitB else 0
        if(F0 == 1 and F1 == 0):
            #AND
            for idx in range(s.inA.length):
                bitA = s.inA.bits[idx]
                bitB = s.inB.bits[idx]
                s.outBits.bits[idx] = 1 if bitA and bitB else 0




                

        #CALCULAR OUTBITS NOVAMENTE
        #############

        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime, None))
        return updateList

class Shifter(Component):
    def __init__(s, updateDelay: int):
        super().__init__(updateDelay, "Shifter")
        s.controlBits = BitData(2) 
        s.inBits = BitData(32)
        s.outBits = BitData(32) 

    def update(s, currentTime : int, entry : UpdateEntry) -> list[UpdateEntry]:
        caller = entry.caller
        #update stats
        match caller.label:
            case "ALU":
                s.inBits.copyBits(caller.outBits)
                pass
            case "Shifter control line":
                s.controlBits.copyBits(caller.outBits)
                s.sll8 = s.controlBits.bits[0]
                s.sra1 = s.controlBits.bits[1]
                pass

        #CALCULAR OUTBITS NOVAMENTE
        s.outBits.clear()
        if(s.sll8 == 1):
            for i in range(s.outBits.length-8):
                s.outBits.bits[i] = s.inBits.bits[i+8]
        elif(s.sra1 == 1):
            s.outBits.bits[0] = s.inBits.bits[0]
            for i in range(1, s.outBits.length-1):
                s.outBits.bits[i+1] = s.inBits.bits[i-1]
        else:
            s.outBits.copyBits(s.inBits)
        #############

        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime, None))
        return updateList

class ORUnit(Component):
    def __init__(s, updateDelay :int):
        super().__init__(updateDelay, "ORUnit")
        s.JMPCValue = 0 
        s.nextAddrBits = BitData(9)
        s.MBRBits = BitData(8)
        s.outBits = BitData(9)
    
    def update(s, currentTime: int, entry : UpdateEntry) -> list[UpdateEntry]:
        caller = entry.caller
        #update stats
        match caller.label:
            case "JMPC line":
                s.JMPCValue = caller.outBits.bits[0]
                pass
            case "MBR":
                s.MBRBits.copyBits(entry.information)
                pass
            case "Addr line":
                s.nextAddrBits.copyBits(caller.outBits)
                pass

        #CALCULAR OUTBITS NOVAMENTE
        if s.JMPCValue:
            s.outBits.bits[0] = s.nextAddrBits.bits[0]
            for i in range(8):
                s.outBits.bits[i+1] = s.MBRBits.bits[i] or s.nextAddrBits.bits[i+1]
        else:
            s.outBits.copyBits(s.nextAddrBits)
        #############

        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        currentOutBits = BitData(s.outBits.length)
        currentOutBits.copyBits(s.outBits)
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime, currentOutBits))
        return updateList

class MPC(Component):
    def __init__(s, updateDelay: int):
        super().__init__(updateDelay, "MPC")
        s.addrBits = BitData(9)
        s.HighBit = BitData(1)
        s.outBits = BitData(9) 

    def update(s, currentTime : int, entry: UpdateEntry) -> list[UpdateEntry]:
        caller = entry.caller
        #update stats
        match caller.label:
            case "ORUnit":
                for i in range(9):
                    s.addrBits.bits[i] = caller.outBits.bits[i]
                pass
            case "HighBit":
                s.HighBit.bits[0] = caller.outBits.bits[0]
                pass

        s.outBits.bits[0] = 1 if s.HighBit.bits[0] or s.addrBits.bits[0] else 0
        for i in range(8):
            s.outBits.bits[i+1] = s.addrBits.bits[i+1]

        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime, None))
        return updateList

class ControlMemory(Component):
    def __init__(s, updateDelay: int):
        super().__init__(updateDelay, "Control Memory")
        s.bits = BitData(512*36)
        s.MPCBits = BitData(9)
        s.outBits = BitData(36)
        s.currentAddress = BitData(9)
    
    def loadMicrocode(s, codeFileName : str):
        with open(codeFileName) as f:
            for i in range(512):
                line = f.readline()
                for j in range(36):
                    s.bits.bits[i*36 + j] = int(line[j])

    def update(s, currentTime : int, entry : UpdateEntry) -> list[UpdateEntry]:
        caller = entry.caller
        #update stats
        match caller.label:
            case "Clock":
                s.currentAddress.copyBits(s.MPCBits)
                addressInteger : int = s.currentAddress.toInteger()*36
                s.outBits.copyBitSection(s.bits, addressInteger)
                #print(s.outBits.bits)
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
            updateList.append(UpdateEntry(dependent, s, currentTime, None))
        return updateList

class MIR(Component):
    def __init__(s, updateDelay: int):
        super().__init__(updateDelay, "MIR")
        s.outBits = BitData(36) 

    def update(s, currentTime : int, entry = UpdateEntry) -> list[UpdateEntry]:
        caller = entry.caller
        #update stats
        s.outBits.copyBits(caller.outBits)

        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime, None))
        return updateList

class Decoder(Component):
    def __init__(s, updateDelay: int):
        super().__init__(updateDelay, "Decoder")
        s.inBits = BitData(4)
        s.outBits = BitData(9)
    

    def update(s, currentTime : int, entry: UpdateEntry) -> list[UpdateEntry]:
        caller = entry.caller
        #update stats
        s.inBits.copyBits(caller.outBits)

        s.outBits.clear()
        s.outBits.bits[s.inBits.toInteger()] = 1

        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime, None))
        return updateList

class MBR(Component):
    def __init__(s, updateDelay: int, orUnit: ORUnit):
        super().__init__(updateDelay, "MBR")
        s.inBits = BitData(8) 
        s.outBits = BitData(32) 
        s.output1 = False
        s.output2 = False
        s.ORUnit = orUnit

    def update(s, currentTime : int, entry : UpdateEntry) -> list[UpdateEntry]:
        caller = entry.caller
        #update stats
        updateList : list[UpdateEntry] = []
        match caller.label:
            case "enable output1":
                if(caller.outBits.bits[0] == 0):
                    s.output1 = False
                else:
                    s.output1 = True
            case "enable output2":
                if(caller.outBits.bits[0] == 0):
                    s.output2 = False
                else:
                    s.output2 = True
            case "Memory":
                pass

        currentInBits = BitData(s.inBits.length)
        currentInBits.copyBits(s.inBits)
        updateList.append(UpdateEntry(s.ORUnit, s, currentTime, currentInBits))
        if(not (s.output1 or s.output2)):
            s.outBits.clear()
            return updateList
        else:
            if(s.output1):
                for i in range(24):
                    s.outBits.bits[i] = s.inBits.bits[0]
            else:
                s.outBits.clear()

            for i in range(8):
                s.outBits.bits[i+24] = s.inBits.bits[i]
            pass

        currentInBits = BitData(s.inBits.length)
        currentInBits.copyBits(s.inBits)
        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime, currentInBits))
        return updateList

class H(Component): #H register
    def __init__(s, updateDelay: int):
        super().__init__(updateDelay, "H")
        s.comingBits = BitData(32)
        s.inBits = BitData(32)
        s.outBits = BitData(32)
        s.enableInput: bool = False
        s.enableOutput: bool = True
    def update(s, currentTime : int, entry : UpdateEntry) -> list[UpdateEntry]:
        caller = entry.caller
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
                return
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
            updateList.append(UpdateEntry(dependent, s, currentTime, None))
        return updateList

class Memory(Component):
    def __init__(s, updateDelay: int, mbr : MBR, mdr : MDR):
        #updateDelay for memory is how many full cycles, not just timesteps
        super().__init__(updateDelay, "Memory")
        s.memoryBits = BitData((3000)*32)
        s.fetchQueue = [[]*s.updateDelay]
        s.readQueue = [[]*s.updateDelay]
        s.writeQueue = [[]*s.updateDelay]
        s.MDR = mdr
        s.MBR = mbr
        s.MBROutBits = BitData(8)

    def update(s, currentTime : int, entry : UpdateEntry) -> list[UpdateEntry]:
        caller = entry.caller
        updateList : list[UpdateEntry] = []
        
        match caller.label:
            case "Clock":
                #if operations not queued before clock update, then assume there was no operation
                if(len(s.fetchQueue) < s.updateDelay):
                    s.fetchQueue.append([])
                if(len(s.readQueue) < s.updateDelay):
                    s.readQueue.append([])
                if(len(s.writeQueue) < s.updateDelay):
                    s.writeQueue.append([])
                
                print(s.readQueue)
                print(s.fetchQueue)
                print(s.writeQueue)

                fetchOp = s.fetchQueue[0]
                readOp = s.readQueue[0]
                writeOp = s.writeQueue[0]
                s.fetchQueue.pop(0)
                s.readQueue.pop(0)
                s.writeQueue.pop(0)
                if(len(fetchOp)>0):
                    byteAddr = fetchOp[0]
                    s.MBR.inBits.copyBitSection(s.memoryBits, byteAddr*8)
                    #s.MBR.outBits.copyBitSection(s.memoryBits, byteAddr*8)
                if(len(readOp)>0):
                    wordAddr = readOp[0]*4
                    s.MDR.inBits.copyBitSection(s.memoryBits, wordAddr*8)
                    s.MDR.outBits.copyBitSection(s.memoryBits, wordAddr*8)
                    #s.MDR.update(currentTime, UpdateEntry(s.MDR, s, currentTime, None))
                if(len(writeOp)>0):
                    bitData = writeOp[0]
                    wordAddr = writeOp[1]*4
                    for i in range(bitData.length):
                        s.memoryBits.bits[wordAddr*8 + i] = bitData.bits[i]
                

        return updateList
    
    def queueFetch(s, byteAddr):
        s.fetchQueue.append([byteAddr])

    def queueRead(s, wordAddr):
        s.readQueue.append([wordAddr])

    def queueWrite(s, bitData, wordAddr):
        s.writeQueue.append([bitData, wordAddr])

    def loadProgram(s, fileName: str):
        bitIdx = 0
        with open(fileName) as f:
            for line in f:
                #print(line)
                for char in line:
                    if(char == '\n'):
                        continue
                    s.memoryBits.bits[bitIdx] = int(char)
                    bitIdx+=1

        #Só atualizando direto aqui porque é o início do programa
        byteAddr = 0
        s.MBR.inBits.copyBitSection(s.memoryBits, byteAddr*8)
        s.MBR.outBits.copyBitSection(s.memoryBits, byteAddr*8)
        
        s.MBR.update(0, UpdateEntry(s.MBR, s, 0, None))
        with open("memoryDump.txt", "w") as f:
            for i in range(s.memoryBits.length):
                if(i%32 == 0):
                    f.write("\n")
                elif(i%8==0):
                    f.write("  ")
                elif(i%4 == 0):
                    f.write(" ")
                
                f.write(str(s.memoryBits.bits[i]))
                
                        
class MAR(Component):
    def __init__(s, updateDelay: int):
        super().__init__(updateDelay, "MAR")
        s.comingBits = BitData(32) 
        s.inBits = BitData(32) 
        s.outBits = BitData(32) 
        s.enableOutput : bool = False 
        s.enableInput : bool = False

    def update(s, currentTime : int, entry : UpdateEntry) -> list[UpdateEntry]:
        caller = entry.caller
        match caller.label:
            case "enable output":
                if caller.outBits.bits[0] == 0:
                    s.enableOutput = False
                    s.outBits.clear()
                else:
                    s.enableOutput = True
                    s.outBits.copyBits(s.inBits)
            case "enable input":
                if caller.outBits.bits[0] == 0:
                    s.enableInput = False
                else:
                    s.enableInput = True
                    s.inBits.copyBits(s.comingBits)
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
            updateList.append(UpdateEntry(dependent, s, currentTime, s.inBits))
        return updateList

class MDR(Component):
    def __init__(s, updateDelay: int, memory : Memory):
        super().__init__(updateDelay, "MDR")
        s.comingBits = BitData(32) 
        s.inBits = BitData(32) 
        s.outBits = BitData(32) 
        s.enableOutput : bool = False 
        s.enableInput : bool = False
        s.Memory = memory

    def update(s, currentTime : int, entry : UpdateEntry) -> list[UpdateEntry]:
        caller = entry.caller
        memoryUpdated = False
        match caller.label:
            case "enable input":
                if caller.outBits.bits[0] == 0:
                    s.enableInput = False
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
                return []
            case "Clock":
                if (s.enableInput):
                    s.inBits.copyBits(s.comingBits)
                    if (s.enableOutput):
                        s.outBits.copyBits(s.inBits)
                    else:
                        return []
                else:
                    return []
            case "Memory":
                pass

        currentInBits = BitData(s.inBits.length)
        currentInBits.copyBits(s.inBits)

        if (not s.enableOutput):
            if(not memoryUpdated):
                return [UpdateEntry(s.Memory, s, currentTime, currentInBits)]
            else: 
                return []

        print("Updating bus B because of: ",caller.label)
        updateList : list[UpdateEntry] = []
        if (not memoryUpdated):
            updateList.append(UpdateEntry(s.Memory, s, currentTime, currentInBits))

        for dependent in s.dependents:
            updateList.append(UpdateEntry(dependent, s, currentTime, currentInBits))
        return updateList

class PC(Component):
    def __init__(s, updateDelay: int):
        super().__init__(updateDelay, "PC")
        s.comingBits = BitData(32) 
        s.inBits = BitData(32) 
        s.outBits = BitData(32) 
        s.enableOutput : bool = False 
        s.enableInput : bool = False
        s.Memory = None

    def update(s, currentTime : int, entry : UpdateEntry) -> list[UpdateEntry]:
        caller = entry.caller
        match caller.label:
            case "enable input":
                if caller.outBits.bits[0] == 0:
                    s.enableInput = False
                else:
                    s.enableInput = True
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
                        currentBits = BitData(s.inBits.length)
                        currentBits.copyBits(s.inBits)
                        return [UpdateEntry(s.Memory,s, currentTime, currentBits)]
                else:
                    return []
            case "Memory":
                s.inBits.copyBits(entry.information)
                pass

        #if here only update B bus if output is enabled
        if (not s.enableOutput):
            return []

        #enqueue updates for dependents
        updateList : list[UpdateEntry] = []
        for dependent in s.dependents:
            currentBits = BitData(s.inBits.length)
            currentBits.copyBits(s.inBits)
            updateList.append(UpdateEntry(dependent, s, currentTime, currentBits))
            #print(currentBits.bits)
        return updateList