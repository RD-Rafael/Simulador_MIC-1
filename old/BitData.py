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