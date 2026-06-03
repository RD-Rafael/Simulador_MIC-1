#ALL CLASSES HAVE TO IMPLEMENT UPDATE METHOD
#UPDATE METHOD UPDATES OBJECT STATE GIVEN INPUTS
#IF OBJECT A STATE CHANGES, OBJECT A HAS TO PROPAGATE UPDATE CALLS TO OBJECTS WHICH INPUT IS DEPENDENT ON OBJECT A STATE
import old.BitData as BitData

class Bus(BitData):
    def __init__(self, numBits):
        super()().__init__(numBits)
        self.inputSources = []
    def addInput(self, bitData, start):
        #assumindo que bitData tem mesmo tamanho que o bus
        self.inputSources.append([bitData, start])
    def Update(self):
        self.bits = self.numBits*[0]
        for entry in self.inputSources:
            bitData = entry[0]
            start = entry[1]
            for i in range(start, start + self.numBits):
                self.bits[i] = 1 if bitData.getBit(i) == 1 else self.bits[i]
        

class Register(BitData):
    def __init__(self, numBits):
        super()().__init__(numBits)
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
            self.enableOutput = True if self.ouputControlLine.getBit(self.outputControlIdx) == 1 else False
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
        
class Shifter(BitData):
    def __init__(self, numBits, controlLines, aluBus):
        super().__init__(numBits)
        self.controlLines = controlLines
        self.ALUbus = aluBus
    
    def Update(self):
        SLL8 = self.controlLines.getBit(0)
        SRA1 = self.controlLines.getBit(1)
        #descobrir oq tem q fazer
        self.setBits(self.ALUbus)

class Memory(BitData):
    
 
        
class Computer:
    def __init__(s):

        s.busA = Bus(32)
        s.busB = Bus(32)
        s.busC = Bus(32)

        s.MAR = Register(32)
        s.MDR = Register(32)
        s.PC = Register(32)
        s.MBR = Register(8)
        s.SP = Register(32)
        s.LV = Register(32)
        s.CPP = Register(32)
        s.TOS = Register(32)
        s.OPC = Register(32)
        s.H = Register(32)

        s.MIR = Register(36)
        s.MPC = Register(9)

        s.aluOutput = Bus(32)
        s.ALUControlLines = Bus(6)
        s.ALUControlLines.addInput(s.MIR, 5)
        s.alu = ALU(s.busA, s.busB, s.ALUControlLines, s.aluOutput)

        s.shifterControlLines = Bus(2)
        s.shifterControlLines.addInput(s.MIR, 3)
        s.shifter = Shifter(32, s.shifterControlLines, s.aluOutput)

        s.busB.addInput(s.MDR, 0)
        s.busB.addInput(s.PC, 0)
        s.busB.addInput(s.MBR, 0)
        s.busB.addInput(s.SP, 0)
        s.busB.addInput(s.LV, 0)
        s.busB.addInput(s.CPP, 0)
        s.busB.addInput(s.TOS, 0)
        s.busB.addInput(s.OPC, 0)





