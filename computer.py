#ALL CLASSES HAVE TO IMPLEMENT UPDATE METHOD
#UPDATE METHOD UPDATES OBJECT STATE GIVEN INPUTS
#IF OBJECT A STATE CHANGES, OBJECT A HAS TO PROPAGATE UPDATE CALLS TO OBJECTS WHICH INPUT IS DEPENDENT ON OBJECT A STATE
class Sequencer:
    pass



class BitData: #registers, outputs, etc
    def __init__(self, numBits):
        self.bits = numBits*[0]
        self.enableInput = True 
        self.enableOutput = True 
        self.numBits = numBits

    def getBits(self):
        if(not self.enableOutput):
            return self.numBits*[0] 
        return self.bits
    
    def getBitsSection(self, idxStart, idxEnd):
        if(idxEnd - idxStart > self.numBits or (idxStart <= 0 or idxStart >= self.numBits) or (idxEnd <= 0 or idxEnd >= self.numBits)):
            raise Exception("tried to get bit section out of bounds in BitData")
        if(idxEnd < idxStart):
            raise Exception("invalid indexes for bit section in BitData")
        if(not self.enableOuput):
            return (idxEnd - idxStart)*[0]
        return self.bits[idxStart:idxEnd]

    
    def getBit(self, idx):
        if(idx < 0 or idx >= self.numBits):
            raise Exception("Bit index out of range for BitData")
        if(not self.enableOutput):
            return 0 
        return self.bits[idx]

    def getInt(self):
        if(not self.enableOutput):
            return 0
        ans = 0
        bit = 1
        for i in range(self.numBits):
            idx = self.numBits - i - 1
            ans = ans + self.bits[idx]*bit
            bit = bit << 1
        return ans

    def setBits(self, newBits): #copy bits from newBits to self limiting it to numBits
        if(not (isinstance(newBits, BitData) or isinstance(newBits, list))):
            raise Exception("Tried to set bits to a non BitData variable")
        newBitsLen = 0
        if(isinstance(newBits, BitData)):
            newBitsLen = BitData.getLength()
        else:
            newBitsLen = len(newBits)
        if(not (self.numBits <= newBitsLen)):
            raise Exception("Tried to set register bus bits to less than BitData length")
        if(not self.enableInput):
            return
        if(isinstance(newBits, BitData)):
            for i in range(self.numBits):
                self.bits[i] = newBits.bits[i]
        else:
            for i in range(self.numBits):
                self.bits[i] = newBits[i]
            
    def setBit(self, idx, bitValue):
        if(idx < 0 or idx >= self.numBits):
            raise Exception("Bit index out of range for BitData")
        if(not self.enableInput):
            return
        else:
            self.bits[idx] = bitValue

    def getIntSigned(self):
        ans = 0
        bit = 1
        for i in range(self.numBits-1):
            idx = self.numBits - i - 1
            ans = ans + self.bits[idx]*bit
            bit = bit << 1
        ans = ans - self.bits[0]*bit
        return ans

    def setBitsInt(self, num):
        bit = 1
        for i in range(self.numBits):
            check = num & bit
            self.bits[self.numBits - i - 1] = 1 if check > 0 else 0
            bit = bit << 1

    def getLength(self):
        return self.numBits

class Bus(BitData):
    def __init__(self, numBits):
        super().__init__(numBits)
        self.inputSources = []
    def addInput(self, bitData):
        #assumindo que bitData tem mesmo tamanho que o bus
        self.inputSources.append(bitData)
    def Update(self):
        self.bits = self.numBits*[0]
        for bitData in self.inputSources:
            for i in range(self.numBits):
                self.bits[i] = 1 if bitData.getBit(i) == 1 else self.bits[i]
        

class Register(BitData):
    def __init__(self, numBits):
        super().__init__(numBits)
        self.inputControlLine = None
        self.outputControlLine = None
    def setInputBus(self, bus):
        self.inputBus = bus

    def setInputControl(self, bus, idx):
        self.inputControlLine = bus
        self.inputControlIdx = idx

    def setOutputControl(self, bus, idx):
        self.outputControlLine = bus
        self.outputControlIdx = idx

    def Update(self):
        if(self.inputControlLine):
            self.enableInput = True if self.inputControlLine.getBit(self.inputControlIdx) == 1 else False
        if(self.outputControlLine):
            self.enableOuput = True if self.ouputControlLine.getBit(self.outputControlIdx) == 1 else False
        if(self.enableInput):
            self.setBits(self.inputBus.getBits())
    
 
    

class ALU:
    def __init__(self, busA, busB, controlLines, aluOutput):
        if(isinstance(busA, Bus) and isinstance(busB, Bus) and isinstance(controlLines, Bus) and isinstance(aluOutput,Bus)):
            if(busA.getLength() != 32 or busB.getLength() != 32 or controlLines.getLength() != 6 or aluOutput.getLength() != 32):
                raise Exception("Wrong bus lengths in ALU init")
            self.busA = busA
            self.busB = busB
            self.controlLines = controlLines #F0, F1, ENA, ENB, INVA, INC
            self.output = aluOutput
        else:
            raise Exception("ALU init used wrong variable types")

    def Update(self):
        F0 = self.controlLines.getBit(0)
        F1 = self.controlLines.getBit(1)
        ENA = self.controlLines.getBit(2)
        ENB = self.controlLines.getBit(3)
        INVA = self.controlLines.getBit(4)
        INC = self.controlLines.getBit(5)
        A = BitData(self.busA.getLength()) 
        B = BitData(self.busB.getLength())
        if(ENA == 1):
            A = self.busA
        if(ENB == 1):
            B = self.busB
        if(INVA == 1):
            for i in range(A.getLength()):
                if(A.getBit(i) == 0):
                    A.setBit(i, 1)
                else:
                    A.setBit(i, 0)
        if(F0 == 1 and F1 == 1): #addition
            ans = A.getInt() + B.getInt()
            if(INC == 1):
                ans += 1
            self.output.setBitsInt(ans)
        if(F0 == 0 and F1 == 0): #AND
            newOutput = BitData(A.getLength())
            for i in range(A.getLength()):
                newOutput.setBit(i, 1 if (A.getBit(i) == B.getBit(i) and A.getBit(i) == 1) else 0)
            self.output.setBits(newOutput)
        if(F0 == 0 and F1 == 0): #OR
            newOutput = BitData(A.getLength())
            for i in range(A.getLength()):
                newOutput.setBit(i, 1 if (A.getBit(i) == B.getBit(i) and A.getBit(i) == 0) else 0)
            self.output.setBits(newOutput)
        
        
        
class Computer:
    def __init__(self):
        self.aluOutput = Bus(32)
        self.ALUControlLines = Bus(6)

        self.busA = Bus(32)
        self.busB = Bus(32)
        self.busC = Bus(32)

        self.MAR = Register(32)
        self.MDR = Register(32)
        self.PC = Register(32)
        self.MBR = Register(8)
        self.SP = Register(32)
        self.LV = Register(32)
        self.CPP = Register(32)
        self.TOS = Register(32)
        self.OPC = Register(32)
        self.H = Register(32)

        self.MIR = Register(36)
        self.MPC = Register(9)




