from computer import BitData

with open("ijvmcodeinput.txt") as f:
    f.readline()


with open("ijvmcodeoutput.txt", "w") as f:
    CPP = 0 # Address of constant set pointer (word) , first line
    LV = 0 # Address of local variable pointer (word), second line
    SP = 0 # Address of operands stack pointer (word), third line
    PC = 0 # Address of program counter pointer (byte), fourth line

    #write the 2048 bytes of memory