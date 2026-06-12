from computer import *
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import Image
from time import sleep

computer : Computer = Computer()
computer.Memory.loadProgram("macroprogram.txt")

mainWindow = tk.Tk()
font = ("Times New Roman", 20)
HIntLabel = ttk.Label(mainWindow, text = "", font = font)
HIntLabel.grid()

def createRegisterLabel(registersWindow, font, register: Component, bits: BitData, row : int):
    labelLabel : ttk.Label = ttk.Label(registersWindow, text=register.label, font=font, justify='left', anchor='w')
    labelLabel.grid(sticky='W', column=1, row=row)
    bitsLabel : ttk.Label = ttk.Label(registersWindow, text="", font=font, justify='left', anchor='w')
    bitsLabel.grid(sticky='W', column=2, row=row)
    ans = [bits, bitsLabel]
    return ans

def updateLabelsList(labels):
    for label in labels:
        bits = label[0]
        bitsLabel = label[1]
        lstr = ": "
        for i in range(bits.length):
            lstr += str(bits.bits[i])
        bitsLabel.configure(text=lstr)
registerLabels = []
debugLabels = []

def tksleep(t):
    ms = int(t*1)
    root = tk._get_default_root('sleep')
    var = tk.IntVar(root)
    root.after(ms, var.set, 1)
    root.wait_variable(var)

def update():
    computer.update()
    updateLabelsList(registerLabels)
    updateLabelsList(debugLabels)

def reset():
    computer.reset()
    computer.Memory.loadProgram("macroprogram.txt")

def nextCycle():
    root = tk._get_default_root('Running')
    runningConstantly = tk.BooleanVar(root)
    for i in range(52):
        computer.update()
        updateLabelsList(registerLabels)
        updateLabelsList(debugLabels)
        HIntLabel.configure(text=str(computer.Memory.byteAddress) + " " + str(computer.Memory.wordAddress))
    return
    while runningConstantly:
        tksleep(50)
        computer.update()
        updateLabelsList(registerLabels)
        updateLabelsList(debugLabels)
        HIntLabel.configure(text=str(computer.H.inBits.toInteger()))

def toggleRunningConstantly():
    root = tk._get_default_root('Running')
    runningConstantly = tk.BooleanVar(root)
    runningConstantly.set(not runningConstantly.get())
    nextCycle()

mainWindow.title( "main" )
ttk.Button(mainWindow, text="Quit", command=mainWindow.destroy).grid(column=1, row=0)

codeWindow = tk.Toplevel( mainWindow )
codeWindow.transient( mainWindow )
codeWindow.title( "Montador" )
codeWindow.minsize(600, 300)
codeWindowfrm = ttk.Frame(codeWindow, padding=10)
codeWindowfrm.grid()
CodeTextInput = scrolledtext.ScrolledText(codeWindowfrm, width = 25, height = 30, font = font)
CodeTextInput.grid(column=2, row=0)

simulationWindow = tk.Toplevel( mainWindow )
simulationWindow.transient( mainWindow )
simulationWindow.title( "Simulador" )
simulationWindow.minsize(600, 300)
simulationWindowfrm = ttk.Frame(simulationWindow, padding=10)
simulationWindowfrm.grid()
ttk.Button(simulationWindow, text="Update", command=update).grid(column=1,row=0)
ttk.Button(simulationWindow, text="next cycle", command=toggleRunningConstantly).grid(column=2,row=0)
ttk.Button(simulationWindow, text="reset", command=reset).grid(column=3,row=0)

registersWindow = tk.Toplevel( mainWindow )
registersWindow.transient( mainWindow )
registersWindow.title( "Registradores" )
registersWindow.minsize(600, 300)
ttk.Separator(registersWindow).grid(column=0, row=1)

registerLabels.append(createRegisterLabel(registersWindow, font, computer.MAR, computer.MAR.inBits, len(registerLabels)))
registerLabels.append(createRegisterLabel(registersWindow, font, computer.MDR, computer.MDR.inBits, len(registerLabels)))
registerLabels.append(createRegisterLabel(registersWindow, font, computer.PC, computer.PC.inBits, len(registerLabels)))
registerLabels.append(createRegisterLabel(registersWindow, font, computer.MBR, computer.MBR.inBits, len(registerLabels)))
registerLabels.append(createRegisterLabel(registersWindow, font, computer.SP, computer.SP.inBits, len(registerLabels)))
registerLabels.append(createRegisterLabel(registersWindow, font, computer.LV, computer.LV.inBits, len(registerLabels)))
registerLabels.append(createRegisterLabel(registersWindow, font, computer.CPP, computer.CPP.inBits, len(registerLabels)))
registerLabels.append(createRegisterLabel(registersWindow, font, computer.TOS, computer.TOS.inBits, len(registerLabels)))
registerLabels.append(createRegisterLabel(registersWindow, font, computer.OPC, computer.OPC.inBits, len(registerLabels)))
registerLabels.append(createRegisterLabel(registersWindow, font, computer.H, computer.H.inBits, len(registerLabels)))
registerLabels.append(createRegisterLabel(registersWindow, font, computer.MIR, computer.MIR.outBits, len(registerLabels)))
registerLabels.append(createRegisterLabel(registersWindow, font, computer.MPC, computer.MPC.outBits, len(registerLabels)))

debugWindow = tk.Toplevel( mainWindow )
debugWindow.transient( mainWindow )
debugWindow.title( "Registradores" )
debugWindow.minsize(600, 300)
ttk.Separator(debugWindow).grid(column=0, row=1)

debugLabels.append(createRegisterLabel(debugWindow, font, computer.Shifter, computer.Shifter.outBits, len(debugLabels)))
debugLabels.append(createRegisterLabel(debugWindow, font, computer.ALU, computer.ALU.outBits, len(debugLabels)))
debugLabels.append(createRegisterLabel(debugWindow, font, computer.ALUControlLine, computer.ALUControlLine.outBits, len(debugLabels)))
debugLabels.append(createRegisterLabel(debugWindow, font, computer.Memory, computer.Memory.PCBits, len(debugLabels)))
debugLabels.append(createRegisterLabel(debugWindow, font, computer.Memory, computer.Memory.MDRBits, len(debugLabels)))
debugLabels.append(createRegisterLabel(debugWindow, font, computer.Memory, computer.Memory.MDROutBits, len(debugLabels)))
debugLabels.append(createRegisterLabel(debugWindow, font, computer.MemoryControlLine, computer.MemoryControlLine.outBits, len(debugLabels)))
debugLabels.append(createRegisterLabel(debugWindow, font, computer.Abus, computer.Abus.outBits, len(debugLabels)))
debugLabels.append(createRegisterLabel(debugWindow, font, computer.Bbus, computer.Bbus.outBits, len(debugLabels)))
debugLabels.append(createRegisterLabel(debugWindow, font, computer.Cbus, computer.Cbus.outBits, len(debugLabels)))
debugLabels.append(createRegisterLabel(debugWindow, font, computer.Decoder, computer.Decoder.outBits, len(debugLabels)))
debugLabels.append(createRegisterLabel(debugWindow, font, computer.controlMemory, computer.controlMemory.outBits, len(debugLabels)))
debugLabels.append(createRegisterLabel(debugWindow, font, computer.controlMemory, computer.controlMemory.MPCBits, len(debugLabels)))

def closer( event ):
    mainWindow.destroy()

mainWindow.bind( "<Escape>", closer )
mainWindow.mainloop()

computer.update()