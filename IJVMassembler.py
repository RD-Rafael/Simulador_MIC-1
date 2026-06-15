from computer import BitData
hexValues : dict[chr, int] = dict()
hexValues['0'] = 0
hexValues['1'] = 1
hexValues['2'] = 2
hexValues['3'] = 3
hexValues['4'] = 4
hexValues['5'] = 5
hexValues['6'] = 6
hexValues['7'] = 7
hexValues['8'] = 8
hexValues['9'] = 9
hexValues['a'] = 10
hexValues['b'] = 11
hexValues['c'] = 12
hexValues['d'] = 13
hexValues['e'] = 14
hexValues['f'] = 15

def hexToInt(hex: str) -> int:
    hex = hex.removeprefix("0x")
    ans = 0
    for i in range(len(hex)):
        ans += hexValues[hex[i]]*(16**(len(hex)-i-1))
    return ans


instructionToOpcode : dict[str, int] = dict()
instructionToOpcode["NOP"] = 6
instructionToOpcode["IADD"] = 7
instructionToOpcode["ISUB"] = 10
instructionToOpcode["IAND"] = 13
instructionToOpcode["IOR"] = 16
instructionToOpcode["DUP"] = 19
instructionToOpcode["POP"] = 21 
instructionToOpcode["SWAP"] = 24
instructionToOpcode["BIPUSH"] = 30
instructionToOpcode["ILOAD"] = 4
instructionToOpcode["ISTORE"] = 5
instructionToOpcode["WIDE"] = 42
instructionToOpcode["LDC_W"] = 50
instructionToOpcode["IINC"] = 54
instructionToOpcode["GOTO"] = 60
instructionToOpcode["IFLT"] = 66
instructionToOpcode["IFEQ"] = 70
instructionToOpcode["IF_ICMPEQ"] = 74
instructionToOpcode["INVOKEVIRTUAL"] = 82
instructionToOpcode["IRETURN"] = 104


constantAddress : dict[str, int] = dict()
constantValue : dict[int, int] = dict()

labelAddress : dict[str, int] = dict()

methodAddress: dict[str, int] = dict()
methodLocalVariables : dict[str, dict[str, int]] = dict()

def writeIntByte(outF, value : int, byteCount : int):
    lineToWrite = " "*8*byteCount
    for i in range(8*byteCount):
        lineToWrite.bits[i] = str(1 if bool(value & (1 << (lineToWrite.length) - i - 1)) else 0)
        outF.writeLine(lineToWrite)

def writeInstruction(currentMethod : str, instructionStr : str, outF):
    instructionParts = instructionStr.strip().split()
    using2ByteAddr = False
    i = 0

    if(instructionParts[0] == "WIDE"):
        writeIntByte(outF, instructionToOpcode["WIDE"], 1)
        using2ByteAddr = True
        i+=1

    opcode = instructionParts[i]
    i+=1
    writeIntByte(outF, instructionToOpcode[opcode], 1)

    #If instruction has N/A operands, thats it
    if(
        opcode == "DUP" or
        opcode == "IADD" or
        opcode == "IAND" or
        opcode == "IOR" or
        opcode == "IRETURN" or
        opcode == "ISUB" or
        opcode == "NOP" or
        opcode == "POP" or
        opcode == "SWAP"
    ):
        return
    
    #If instruction requires label than write 2byte label address
    if(
        opcode == "GOTO" or
        opcode == "IFEQ" or
        opcode == "IFLT" or
        opcode == "IF_ICMPEQ"
    ):
        label = instructionParts[i+1]
        writeIntByte(outF, labelAddress[label], 2)
        return
    
    #if instruction requires variable names
    if(
        opcode == "IINC" or
        opcode == "ILOAD" or
        opcode == "ISTORE"
    ):
        variableName = instructionParts[i+1]
        writeIntByte(outF, methodLocalVariables[currentMethod][variableName], 2 if using2ByteAddr else 1)
        if(opcode == "IINC"):
            writeIntByte(outF, hexToInt(instructionParts[i+2]), 1)
        return
    
    if(opcode == "INVOKEVIRUTAL"):#requires method name, write 2byte mehtod address
        methodName = instructionParts[i+1]
        writeIntByte(outF, methodAddress[methodName], 2)
        return
    print(opcode)




    


with open("ijvmcodeoutput.txt", "w") as outF:
    CPP = 0 # Address of constant set (word) , first line
    LV = 0 # Address of local variable set (word), second line
    with open("IJVM.txt") as f:
        constantAddress["main"] = 0
        constantValue[constantAddress["main"]] = 0
        #look for constant area
        gettingConstants = False
        for line in f:
            if(line.startswith(".constant")):
                gettingConstants = True
                continue
            elif(line.startswith(".end-constant")):
                break

            if(gettingConstants):
                line = line.strip().split(' ')
                constantAddress[line[0]] = len(constantAddress.keys())
                constantValue[constantAddress[line[0]]] = hexToInt(line[1].strip())
            
        #treat main first
        inMain = False
        currentMethodByte = 0
        #find labels in main
        for line in f:
            if(line.startswith(".main")):
                inMain = True
                continue
            elif(line.startswith(".end-main")):
                break
            if(inMain):
                writeInstruction("main", line, outF)
                pass




        

            


        


