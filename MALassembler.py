from computer import BitData

class Instruction:
    def __init__(s, id):
        s.instructionId = id
        s.nextInstructionId : int = -1 #id of next instruction
        s.gotoLabels : list[str] = [] #can have 0, 1 or 2 labels (if 2, first one is if true and second one if false)
        s.adjacentBits = BitData(36) 
    def setLabels(s, l):
        s.gotoLabels = l
        
program : list[BitData] = []
for i in range(512):
    newBitData = BitData(36)
    program.append(newBitData)


with open("malcodeinput.txt") as f:
    """
    currInstructionAddress : int = 0
    instructionAddress : dict[int, int] = dict()
    availableInstructionPairs : list[list[int,int]] = []
    availableInstructionAddresses : list[int] = 512*[0]
    for i in range(255):
        availableInstructionPairs.append([i, i + 256])
    for i in range(512):
        availableInstructionAddresses.append(i)
    """
    instructionIdLine : dict[int, int] = dict()
    instructions : list[str] = []

    #first get labels and isolate instructions
    currentInstructionId = 0
    currentLine = 0
    labelInstructionId : dict[str, int] = dict()
    for line in f:
        strElems = line.strip().split(sep=":")
        instruction = ""

        if(line.strip() == ""):
            #do nothing
            pass
        elif(line.strip()[len(line.strip())-1] == ':'):
            #label by itself
            labelInstructionId[line[0]] = currentInstructionId
            continue
        elif(len(strElems) > 1):
            #inline label
            labelInstructionId[strElems[0]] = currentInstructionId
            instruction = strElems[1].strip()

        if instruction == "":
            instruction = line.strip()
        
        instructions.append(instruction)
        currentInstructionId+=1


    #interpret instruction actions
    currentInstructionId = 0
    instructionObjs : list[Instruction] = []

    for instruction in instructions:
        if(instruction == "MDR = TOS;wr"):
            pass
        instructionObj = Instruction(currentInstructionId)
        instructionParts : list[str] = instruction.split(';')
        foundGoto : bool = False
        labels = []
        for part in instructionParts:
            part = part.strip()
            if part.startswith("goto ("):
                foundGoto = True
                instructionObj.adjacentBits.bits[9] = 1 #JMPC
                labels =["MBR"]
                part = part.removeprefix("goto (")
                part = part.removesuffix(")")
                partParts = part.split(' ')
                if(len(partParts) > 1):
                    #MBR OR value -> set address
                    value = int(partParts[2])
                    valueBits = BitData(9)
                    valueBits._setBitsFromInt(value)
                    for i in range(9):
                        instructionObj.adjacentBits.bits[i] = valueBits.bits[i]
            elif part.startswith("goto"):
                foundGoto = True
                labels = [part.split(" ")[1].strip()]
                
                
            elif part.startswith("if (N)"):
                foundGoto = True
                instructionObj.adjacentBits.bits[10] = 1
                labels.append(part.split(' ')[3])
            elif part.startswith("if (Z)"):
                foundGoto = True
                instructionObj.adjacentBits.bits[11] = 1
                labels.append(part.split(' ')[3])
            elif part.startswith("else"):
                labels.append(part.split(' ')[2])
            elif part.startswith("wr"):
                instructionObj.adjacentBits.bits[29] = 1
            elif part.startswith("rd"):
                instructionObj.adjacentBits.bits[30] = 1
            elif part.startswith("fetch"):
                instructionObj.adjacentBits.bits[31] = 1
            else:
                # something = something
                if(part.endswith("<< 8")):
                    instructionObj.adjacentBits.bits[12] #SLL8
                    part = part.removesuffix("<< 8")
                    part = part.strip()
                
                #r1 = r2 = r3 = r4 op (H,-1) + (  , +1)
                operands = part.split('=')
                for i in range(len(operands)):
                    operands[i] = operands[i].strip()
                if(operands[0] == 'Z' or operands[0] == 'N'):
                    #only do operation with no write
                    pass
                else:
                    #identify operands
                    if (part.find("- 1") != -1):
                        #No H output, invert A port Bits
                        instructionObj.adjacentBits.bits[16] = 0 #ENA = 0
                        instructionObj.adjacentBits.bits[18] = 1 #INVA = 1
                    elif (part.find("+ 1") != -1):
                        #Enable INC
                        instructionObj.adjacentBits.bits[19] = 1 #INC = 1
                    for i in range(len(operands)-1):
                        operand = operands[i]
                        if(operand == "H"):
                            instructionObj.adjacentBits.bits[20] = 1 # enable H input
                        elif(operand == "OPC"):
                            instructionObj.adjacentBits.bits[21] = 1 
                        elif(operand == "TOS"):
                            instructionObj.adjacentBits.bits[22] = 1 
                        elif(operand == "CPP"):
                            instructionObj.adjacentBits.bits[23] = 1 
                        elif(operand == "LV"):
                            instructionObj.adjacentBits.bits[24] = 1 
                        elif(operand == "SP"):
                            instructionObj.adjacentBits.bits[25] = 1 
                        elif(operand == "PC"):
                            instructionObj.adjacentBits.bits[26] = 1 
                        elif(operand == "MDR"):
                            instructionObj.adjacentBits.bits[27] = 1 
                        elif(operand == "MAR"):
                            instructionObj.adjacentBits.bits[28] = 1
                
                #identify register to read from and operation to do
                operation = operands[len(operands)-1]
                operation = operation.replace(" + 1", "")
                operation = operation.replace(" - 1", "")
                operationParts = operation.split(" ")
                otherRegister = ""
                operationSign = ""
                if(len(operationParts) == 1):
                    otherRegister = operationParts[0].strip()
                else:
                    if(operationParts[0] != "H"):
                        otherRegister = operationParts[0].strip()
                    else:
                        otherRegister = operationParts[2].strip()
                    operationSign = operationParts[1].strip()
                decoderValue = 0
                match otherRegister:
                    case "MDR":
                        decoderValue = 0
                    case "PC":
                        decoderValue = 1
                    case "MBR":
                        decoderValue = 2
                    case "MBRU":
                        decoderValue = 3
                    case "SP":
                        decoderValue = 4
                    case "LV":
                        decoderValue = 5
                    case "CPP":
                        decoderValue = 6
                    case "TOS":
                        decoderValue = 7
                    case "OPC":
                        decoderValue = 8
                match operationSign:
                    case "+":
                        #00
                        instructionObj.adjacentBits.bits[14] = 0 
                        instructionObj.adjacentBits.bits[15] = 0 
                    case "-":
                        #00
                        instructionObj.adjacentBits.bits[14] = 0 
                        instructionObj.adjacentBits.bits[15] = 0 
                        instructionObj.adjacentBits.bits[18] = 1 #INVA = 1
                        instructionObj.adjacentBits.bits[19] = 1 #INC = 1
                    case "OR":
                        #01
                        instructionObj.adjacentBits.bits[14] = 0 
                        instructionObj.adjacentBits.bits[15] = 1 
                    case "AND":
                        #10
                        instructionObj.adjacentBits.bits[14] = 1 
                        instructionObj.adjacentBits.bits[15] = 0
                
                decoderBits = BitData(4)
                decoderBits._setBitsFromInt(decoderValue)
                for i in range(4):
                    instructionObj.adjacentBits.bits[32 + i] = decoderBits.bits[i]
                
        if not foundGoto:
            instructionObj.nextInstructionId = currentInstructionId + 1
        currentInstructionId+=1
        
        instructionObj.setLabels(labels)
        instructionObjs.append(instructionObj)


    #find out instructions that are coupled
    instructionPairs : list[list[int]] = []
    for ins in instructionObjs:
        if len(ins.gotoLabels) == 2:
            id1 = labelInstructionId[ins.gotoLabels[0]]
            id2 = labelInstructionId[ins.gotoLabels[1]]
            instructionPairs.append([id1, id2])

    #first instruction is in address 0
    instructionIdAddress : dict[int, int] = dict()
    instructionIdAddress[0] = 0
    #allocate addresses for instructionPairs
    nextAvailableAddress = 1
    for i in range(len(instructionPairs)):
        id1 = instructionPairs[i][0]
        id2 = instructionPairs[i][1]
        instructionIdAddress[id1] = nextAvailableAddress
        instructionIdAddress[id2] = nextAvailableAddress + 256
        nextAvailableAddress+=1
    
    #allocate addresses for other instructions
    for id in range(len(instructions)):
        if(instructionIdAddress.get(id) != None):
            continue
        instructionIdAddress[id] = nextAvailableAddress
        nextAvailableAddress+=1
    
    #set address bits for all instructions
    for i in range(len(instructionObjs)-1, 0, -1):
        ins = instructionObjs[i]
        if(len(ins.gotoLabels) > 0 and ins.gotoLabels[0] == "MBR"):
            continue

        nextAddr = 0
        if(len(ins.gotoLabels) > 0):
            nextAddr = instructionIdAddress[labelInstructionId[ins.gotoLabels[0]]]
        else:
            nextAddr = instructionIdAddress[i+1]

        nextAddrBits = BitData(9)
        nextAddrBits._setBitsFromInt(nextAddr)
        for j in range(9):
            ins.adjacentBits.bits[j] = nextAddrBits.bits[j]

    
    for i in range(len(instructions)):
        ins = instructionObjs[i]
        program[instructionIdAddress[i]].copyBits(ins.adjacentBits)
    

with open("malcodeoutput.txt", mode="w") as f:
    for bitData in program:
        s = ""
        for i in range(bitData.length):
            s += str(bitData.bits[i])
        s += "\n"
        f.write(s)
        

    


                



            
