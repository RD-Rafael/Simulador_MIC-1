def assembleIJVM(fileName):
    maxMemoryByteCount = (300000)*4


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
    hexValues['A'] = 10
    hexValues['B'] = 11
    hexValues['C'] = 12
    hexValues['D'] = 13
    hexValues['E'] = 14
    hexValues['F'] = 15

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
    instructionToOpcode["IFEQ"] = 71
    instructionToOpcode["IF_ICMPEQ"] = 76
    instructionToOpcode["INVOKEVIRTUAL"] = 85
    instructionToOpcode["IRETURN"] = 107
    instructionToOpcode["OUT"] = 255 


    constantAddress : dict[str, int] = dict()
    constantValue : dict[int, int] = dict()

    labelAddress : dict[str, int] = dict()

    methodAddress: dict[str, int] = dict()
    methodLocalVariables : dict[str, dict[str, int]] = dict()

    lines = []
    def writeIntByte(outF, value : int, byteCount : int):
        lineToWrite = ""
        isNeg = False
        if(value < 0):
            isNeg = True
            value = -(value+1)

        bits = []
        for i in range(8*byteCount):
            bits.append(1 if bool(value & (1 << 8*byteCount - i - 1)) else 0)
        for i in range(8*byteCount):
            if(isNeg):
                bits[i] = 0 if bits[i] == 1 else 1
            lineToWrite += str(bits[i])
            
            
        lineToWrite += "\n"
        lines.append(lineToWrite)
        #outF.write(lineToWrite)
        return byteCount

    def writeInstruction(currentMethod : str, instructionStr : str, outF, currentMethodByte : int):
        if(instructionStr.strip() == ''):
            return
        bitsWritten = 0

        instructionParts = instructionStr.strip().split()
        using2ByteAddr = False
        i = 0

        if(instructionParts[0] == "WIDE"):
            bitsWritten += writeIntByte(outF, instructionToOpcode["WIDE"], 1)
            using2ByteAddr = True
            i+=1

        opcode = instructionParts[i]
        i+=1
        bitsWritten += writeIntByte(outF, instructionToOpcode[opcode], 1)

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
            opcode == "SWAP"or
            opcode == "OUT"
        ):
            return bitsWritten
        
        #If instruction requires label than write 2byte offset to label address
        if(
            opcode == "GOTO" or
            opcode == "IFEQ" or
            opcode == "IFLT" or
            opcode == "IF_ICMPEQ"
        ):
            label = instructionParts[i]

            offset = labelAddress[label] - currentMethodByte

            bitsWritten += writeIntByte(outF, offset, 2)
            return bitsWritten
        
        #if instruction requires variable names
        if(
            opcode == "IINC" or
            opcode == "ILOAD" or
            opcode == "ISTORE"
        ):
            variableName = instructionParts[i]
            if methodLocalVariables.get(currentMethod) == None:
                methodLocalVariables[currentMethod] = dict()
            bitsWritten += writeIntByte(outF, methodLocalVariables[currentMethod][variableName], 2 if using2ByteAddr else 1)
            if(opcode == "IINC"):
                bitsWritten += writeIntByte(outF, hexToInt(instructionParts[i+1]), 1)
            return bitsWritten
        
        #if instruction requires constant name
        if(opcode == "LDC_W"):
            constantName = instructionParts[i]
            bitsWritten += writeIntByte(outF, constantAddress[constantName], 2)
            return bitsWritten

        #if instruction requires just a byte
        if(opcode == "BIPUSH"):
            byte = instructionParts[i]
            bitsWritten += writeIntByte(outF, hexToInt(byte), 1)
            return bitsWritten

        if(opcode == "INVOKEVIRTUAL"):#requires method name, write 2byte mehtod address
            methodName = instructionParts[i]
            bitsWritten += writeIntByte(outF, constantAddress[methodName], 2)
            return bitsWritten
        #print(opcode)
        return 0

    def byteCountInLine(line : str):
        if(line.strip() == ""):
            return 0
        bitsWritten = 0

        instructionParts = line.strip().split()
        using2ByteAddr = False
        i = 0

        if(instructionParts[0] == "WIDE"):
            bitsWritten += 1
            using2ByteAddr = True
            i+=1

        opcode = instructionParts[i]
        i+=1
        bitsWritten += 1

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
            opcode == "SWAP" or
            opcode == "OUT"
        ):
            return bitsWritten
        
        if(
            opcode == "GOTO" or
            opcode == "IFEQ" or
            opcode == "IFLT" or
            opcode == "IF_ICMPEQ"
        ):
            bitsWritten += 2
            return bitsWritten
        
        #if instruction requires variable names
        if(
            opcode == "IINC" or
            opcode == "ILOAD" or
            opcode == "ISTORE"
        ):
            bitsWritten += 2 if using2ByteAddr else 1
            if(opcode == "IINC"):
                bitsWritten += 1
            return bitsWritten
        
        #if instruction requires constant name
        if(opcode == "LDC_W"):
            bitsWritten += 2
            return bitsWritten

        #if instruction requires just a byte
        if(opcode == "BIPUSH"):
            bitsWritten += 1
            return bitsWritten
        
        if(opcode == "INVOKEVIRTUAL"):#requires method name, write 2byte mehtod address
            bitsWritten += 2
            return bitsWritten
        #print(opcode)

        

    currentConstantByte = 0
    LV = 0 # Address of local variable set (word), second line
    with open("ijvmcodeoutput.txt", "w") as outF:
        CPP = 0 # Address of constant set (word) , first line
        with open(fileName) as f:
            constantAddress["main"] = 0
            constantValue[constantAddress["main"]] = 0
            currentConstantByte += 1

            
            #look for constant area
            gettingConstants = False
            for line in f:
                if(line.strip() == ""):
                    continue
                if(line.startswith(".constant")):
                    gettingConstants = True
                    continue
                elif(line.startswith(".end-constant")):
                    break

                if(gettingConstants):
                    line = line.strip().split(' ')
                    constantAddress[line[0]] = currentConstantByte
                    constantValue[constantAddress[line[0]]] = hexToInt(line[1].strip())
                    currentConstantByte += 1
            f.seek(0,0)
                
            #main is first in method area
            inMain = False
            inVar = False
            currentMethodByte = 0
            #identify methods and their addresses

            ##identify main function length
            for line in f:
                if(line.strip() == ""):
                    continue
                if(line.startswith(".main")):
                    inMain = True
                    continue
                elif(line.startswith(".end-main")):
                    break
                elif(inMain):
                    if(line.startswith(".var")):
                        inVar = True
                        continue
                    if(line.startswith(".end-var")):
                        inVar = False
                        continue
                    if(inVar):
                        continue

                    currentMethodByte += byteCountInLine(line.split(':')[len(line.split(':'))-1].strip())
            f.seek(0,0)

            ##iterate through Methods
            currentMethod = ""
            inMethod = False
            inVar = False
            for line in f:
                if(line.strip() == ""):
                    continue
                if(line.startswith(".method")):
                    if(inMethod):
                        raise Exception("method definition inside a method definition")
                    inMethod = True
                    currentMethod = line.split(' ')[1].strip()

                    constantAddress[currentMethod] = currentConstantByte 
                    constantValue[currentConstantByte] = currentMethodByte
                    currentConstantByte += 1

                    currentMethodByte += 4 #2byte for param count
                    continue
                elif(line.startswith(".end-method")):
                    inMethod = False
                    break
                elif(inMethod):
                    if(line.startswith(".var")):
                        inVar = True
                        continue
                    if(line.startswith(".end-var")):
                        inVar = False
                        continue
                    if(inVar):
                        continue

                    currentMethodByte += byteCountInLine(line.split(':')[len(line.split(':'))-1].strip())
            f.seek(0,0)
            
            #print(constantAddress)
            #print(constantValue)

            #find labels in main and their addresses
            #percebi q esse e o próximo é igual os últimos 2 e talvez de pra tirar os ultimos 2
            inMain = False
            inVar = False
            currentMethodByte = 0
            for line in f:
                if(line.strip() == ""):
                    continue
                if(line.startswith(".main")):
                    inMain = True
                    continue
                elif(line.startswith(".end-main")):
                    break
                elif(inMain):
                    if(line.startswith(".var")):
                        inVar = True
                        continue
                    if(line.startswith(".end-var")):
                        inVar = False
                        continue
                    if(inVar):
                        continue

                    if(len(line.split(':'))>1):
                        label = line.split(':')[0].strip()
                        labelAddress[label] = currentMethodByte
                    currentMethodByte += byteCountInLine(line.split(':')[len(line.split(':'))-1].strip())
            f.seek(0,0)

            
            #for each method identify its labels and their addresses
            currentMethod = ""
            inMethod = False
            inVar = False
            for line in f:
                if(line.strip() == ""):
                    continue
                if(line.startswith(".method")):
                    if(inMethod):
                        raise Exception("method definition inside a method definition")
                    inMethod = True
                    currentMethod = line.split(' ')[1].strip()

                    currentMethodByte += 4 #2 byte for param count
                    continue
                elif(line.startswith(".end-method")):
                    inMethod = False
                    break
                elif(inMethod):
                    if(line.startswith(".var")):
                        inVar = True
                        continue
                    if(line.startswith(".end-var")):
                        inVar = False
                        continue
                    if(inVar):
                        continue

                    if(len(line.split(':'))>1):
                        label = line.split(':')[0].strip()
                        labelAddress[label] = currentMethodByte
                    currentMethodByte += byteCountInLine(line.split(':')[len(line.split(':'))-1].strip())
            f.seek(0,0)


            #find variables names in main
            inMain = False
            inVar = False
            currentVariableIndex = 0
            for line in f:
                if(line.strip() == ""):
                    continue
                if(line.startswith(".main")):
                    inMain = True
                    continue
                elif(line.startswith(".end-main")):
                    break
                elif(inMain):
                    if(line.startswith(".var")):
                        inVar = True
                        continue
                    if(line.startswith(".end-var")):
                        inVar = False
                        continue
                    if(inVar):
                        varName = line.split(' ')[0].strip()
                        if(methodLocalVariables.get("main") == None):
                            methodLocalVariables["main"] = dict()
                        methodLocalVariables["main"][varName] = currentVariableIndex
                        currentVariableIndex +=1
            f.seek(0,0)



            #for each method find its local variables and decide addresses
            currentMethod = ""
            inMethod = False
            currentVariableIndex = 0
            inVar = False
            for line in f:
                if(line.strip() == ""):
                    continue
                if(line.startswith(".method")):
                    if(inMethod):
                        raise Exception("method definition inside a method definition")
                    inMethod = True
                    currentMethod = line.split(' ')[1].strip()

                    params = line.split(' ')[2].strip().removeprefix('(').removesuffix(')').strip().split(',')
                    paramCount = (0 if params[0] == "" else len(params))

                    if(params[0] == ""):
                        continue

                    for param in params:
                        if(methodLocalVariables.get(currentMethod) == None):
                            methodLocalVariables[currentMethod] = dict()
                        methodLocalVariables[currentMethod][param.strip()] = currentVariableIndex
                        currentVariableIndex += 1

                    continue
                elif(line.startswith(".end-method")):
                    inMethod = False
                    break
                elif(inMethod):
                    if(line.startswith(".var")):
                        inVar = True
                        continue
                    if(line.startswith(".end-var")):
                        inVar = False
                        continue
                    if(inVar):
                        varName = line.split(' ')[0].strip()
                        if(methodLocalVariables.get(currentMethod) == None):
                            methodLocalVariables[currentMethod] = dict()
                        methodLocalVariables[currentMethod][varName] = currentVariableIndex
                        currentVariableIndex +=1
            f.seek(0,0)

            #write main method instructions
            inMain = False
            inVar = False
            currentMethodByte = 0

            for line in f:
                if(line.strip() == ""):
                    continue
                if(line.startswith(".main")):
                    inMain = True
                    continue
                elif(line.startswith(".end-main")):
                    break
                if(inMain):
                    if(line.startswith(".var")):
                        inVar = True
                        continue
                    if(line.startswith(".end-var")):
                        inVar = False
                        continue
                    if(inVar):
                        continue
                    currentMethodByte += writeInstruction("main", line.split(':')[len(line.split(':'))-1].strip(), outF, currentMethodByte)
            f.seek(0,0)

            ##iterate through Methods
            currentMethod = ""
            inMethod = False
            inVar = False
            for line in f:
                if(line.strip() == ""):
                    continue
                if(line.startswith(".method")):
                    if(inMethod):
                        raise Exception("method definition inside a method definition")
                    inMethod = True
                    currentMethod = line.split(' ')[1].strip()

                    params = line.split(' ')[2].strip().removeprefix('(').removesuffix(')').strip().split(',')
                    paramCount = (0 if params[0] == "" else len(params))

                    writeIntByte(outF, paramCount, 2)
                    
                    localCount = len(methodLocalVariables.get(currentMethod, {})) - paramCount
                    writeIntByte(outF, localCount, 2)
                    
                    currentMethodByte += 4 

                    continue
                elif(line.startswith(".end-method")):
                    inMethod = False
                    break
                elif(inMethod):
                    if(line.startswith(".var")):
                        inVar = True
                        continue
                    if(line.startswith(".end-var")):
                        inVar = False
                        continue
                    if(inVar):
                        continue

                    currentMethodByte += writeInstruction(currentMethod, line.split(':')[len(line.split(':'))-1].strip(), outF, currentMethodByte)
            f.seek(0,0)

            padding_needed = (4 - (currentMethodByte % 4)) % 4
            for i in range(padding_needed):
                writeIntByte(outF, 0, 1)
            currentMethodByte += padding_needed
            CPP = int(currentMethodByte / 4) # CPP is a word address
            
            #write constants
            for i in range(len(constantAddress.keys())):
                idx = i
                writeIntByte(outF, int(float(constantValue[idx])), 4)
            
            LV = CPP + len(constantAddress.keys())

    #print(lines)
    if(True):
        with open("ijvmcodeoutput.txt", "w") as outF:
            writeIntByte(outF, CPP, 4)
            writeIntByte(outF, LV, 4)
            outF.writelines(lines)

assembleIJVM("currentMacrocode.txt")

                


            


