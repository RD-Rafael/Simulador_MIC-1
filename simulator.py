from computer import *
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import Image

computer : Computer = Computer()

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

def update():
    computer.update()
    updateLabelsList(registerLabels)
    updateLabelsList(debugLabels)
mainWindow = tk.Tk()
font = ("Times New Roman", 20)

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

registersWindow = tk.Toplevel( mainWindow )
registersWindow.transient( mainWindow )
registersWindow.title( "Registradores" )
registersWindow.minsize(600, 300)
ttk.Separator(registersWindow).grid(column=0, row=1)

registerLabels.append(createRegisterLabel(registersWindow, font, computer.MAR, computer.MAR.outBits, len(registerLabels)))
registerLabels.append(createRegisterLabel(registersWindow, font, computer.MDR, computer.MDR.outBits, len(registerLabels)))
registerLabels.append(createRegisterLabel(registersWindow, font, computer.PC, computer.PC.outBits, len(registerLabels)))
registerLabels.append(createRegisterLabel(registersWindow, font, computer.MBR, computer.MBR.inBits, len(registerLabels)))
registerLabels.append(createRegisterLabel(registersWindow, font, computer.SP, computer.SP.outBits, len(registerLabels)))
registerLabels.append(createRegisterLabel(registersWindow, font, computer.LV, computer.LV.outBits, len(registerLabels)))
registerLabels.append(createRegisterLabel(registersWindow, font, computer.CPP, computer.CPP.outBits, len(registerLabels)))
registerLabels.append(createRegisterLabel(registersWindow, font, computer.TOS, computer.TOS.outBits, len(registerLabels)))
registerLabels.append(createRegisterLabel(registersWindow, font, computer.OPC, computer.OPC.outBits, len(registerLabels)))
registerLabels.append(createRegisterLabel(registersWindow, font, computer.H, computer.H.outBits, len(registerLabels)))
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
debugLabels.append(createRegisterLabel(debugWindow, font, computer.MemoryControlLine, computer.MemoryControlLine.outBits, len(debugLabels)))
debugLabels.append(createRegisterLabel(debugWindow, font, computer.Abus, computer.Abus.outBits, len(debugLabels)))
debugLabels.append(createRegisterLabel(debugWindow, font, computer.Bbus, computer.Bbus.outBits, len(debugLabels)))
debugLabels.append(createRegisterLabel(debugWindow, font, computer.Decoder, computer.Decoder.outBits, len(debugLabels)))
debugLabels.append(createRegisterLabel(debugWindow, font, computer.controlMemory, computer.controlMemory.outBits, len(debugLabels)))
debugLabels.append(createRegisterLabel(debugWindow, font, computer.controlMemory, computer.controlMemory.MPCBits, len(debugLabels)))



print(CodeTextInput.configure().keys())
print(CodeTextInput.configure()["font"])

def closer( event ):
    mainWindow.destroy()

mainWindow.bind( "<Escape>", closer )
mainWindow.mainloop()

computer.update()