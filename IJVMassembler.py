from computer import BitData

instructionToOpcode : dict[str, int]
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


with open("ijvmcodeinput.txt") as f:
    f.readline()


with open("ijvmcodeoutput.txt", "w") as f:
    CPP = 0 # Address of constant set pointer (word) , first line
    LV = 0 # Address of local variable pointer (word), second line
    SP = 0 # Address of operands stack pointer (word), third line
    PC = 0 # Address of program counter pointer (byte), fourth line

    #write the 2048 bytes of memory