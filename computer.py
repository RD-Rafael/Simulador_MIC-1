#ALL CLASSES HAVE TO IMPLEMENT UPDATE METHOD
#UPDATE METHOD UPDATES OBJECT STATE GIVEN INPUTS
#IF OBJECT A STATE CHANGES, OBJECT A HAS TO PROPAGATE UPDATE CALLS TO OBJECTS WHICH INPUT IS DEPENDENT ON OBJECT A STATE

class State:
    memory = [0,0,0,0,1,0,1]

class BitData: #registers, outputs, etc
    def __init__(self, numBits):
        self.bits = numBits*[0]
        self.enableInput = True 
        self.enableOutput = True 
        self.numBits = numBits

    def getInt(self):
        ans = 0
        bit = 1
        for i in range(self.numBits):
            idx = self.numBits - i - 1
            ans = ans + self.bits[idx]*bit
            bit = bit << 1
        return ans

    def setBits(self, newBits): #copy bits from newBits to self limiting it to numBits
        if(not isinstance(newBits, BitData)):
            raise Exception("Tried to set bits to a non BitData variable")
        if(not (self.numBits <= newBits.numBits)):
            raise Exception("Tried to set register bus bits to less than BitData length")
        for i in range(self.numBits):
            self.bits[i] = newBits.bits[i]
            
    def setBit(self, idx, bitValue):
        if(idx < 0 or idx >= self.numBits):
            raise Exception("Bit index out of range for BitData")
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
    pass
    
class Computer:
    state = State()
    reg = BitData(32)


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
        F0 = self.controlLines.bits[0]
        F1 = self.controlLines.bits[1]
        ENA = self.controlLines.bits[2]
        ENB = self.controlLines.bits[3]
        INVA = self.controlLines.bits[4]
        INC = self.controlLines.bits[5]
        A = BitData(self.busA.getLength()) 
        B = BitData(self.busB.getLength())
        if(ENA == 1):
            A = self.busA
        if(ENB == 1):
            B = self.busB
        if(INVA == 1):
            for i in range(A.getLength()):
                A.bits[i] = 1 if A.bits[i] == 0 else 0
        if(F0 == 1 and F1 == 1): #addition
            ans = A.getInt() + B.getInt()
            if(INC == 1):
                ans += 1
            self.output.setBitsInt(ans)
        
        
        
        

aluOutput = Bus(32)
ALUControlLines = Bus(6)
busA = Bus(32)
busB = Bus(32)

alu = ALU(busA, busB, ALUControlLines, aluOutput)

print(aluOutput.bits)
#F0 == F1 == 1 => addition
ALUControlLines.setBit(0, 1)
ALUControlLines.setBit(1, 1)


#enable A
ALUControlLines.setBit(2, 1)

#INC
ALUControlLines.setBit(5, 1)

#inv A
ALUControlLines.setBit(4, 1)

busA.setBitsInt(77)
alu.Update()
print(aluOutput.bits)
print(aluOutput.getIntSigned())

