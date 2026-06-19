from computer import *
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from IJVMassembler import assembleIJVM

def runSimulator():
    output = []
    computer : Computer = Computer()
    computer.loadProgram("ijvmcodeoutput.txt")
    computer.updateSequencer.pendingUpdates[0] = [UpdateEntry(computer.MBR, computer.Memory, 0, computer.Memory.MBROutBits)]

    mainWindow = tk.Tk()
    runningConstantly = tk.BooleanVar(mainWindow, value=False)
    UserExited = tk.BooleanVar(value=False)
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

    OUTText = None
    def updateOUTWindow():
        OUTText.config(state="normal")
        
        OUTText.delete("1.0", tk.END)
        outputText = ""
        for num in output:
            outputText += str(num)
            outputText += '\n'
        OUTText.insert(tk.END, outputText)
        
        OUTText.config(state="disabled")

    registerLabels = []
    debugLabels = []
    memoryDebugLabels = []

    def tksleep(t):
        ms = int(t*1)
        root = tk._get_default_root('sleep')
        var = tk.IntVar(root)
        root.after(ms, var.set, 1)
        root.wait_variable(var)

    def update():
        currOut = computer.update()
        if(currOut != None):
            output.append(currOut)
        updateLabelsList(registerLabels)
        updateLabelsList(debugLabels)
        updateLabelsList(memoryDebugLabels)
        updateOUTWindow()

    def toggleRunningConstantly():
        currentState = runningConstantly.get()
        runningConstantly.set(not currentState)
        while(runningConstantly.get()):
            tksleep(1)
            update()

    def closeMainWindow( event ):
        mainWindow.destroy()

    def closer( event ):
        UserExited.set(True)
        closeMainWindow(event)
        return True

    mainWindow.title( "main" )
    mainWindow.geometry("400x30+800+560")
    ttk.Button(mainWindow, text="Fechar", command=lambda: closer(None)).grid(column=1, row=0)

    codeWindow = tk.Toplevel( mainWindow )
    codeWindow.transient( mainWindow )
    codeWindow.title( "Montador" )
    codeWindow.minsize(490, 300)
    codeWindow.geometry("350x470+600+0")
    codeWindowfrm = ttk.Frame(codeWindow, padding=10)
    codeWindowfrm.grid()
    CodeTextInput = scrolledtext.ScrolledText(codeWindowfrm, width = 25, height = 14, font = font)
    with open("currentMacrocode.txt", "r") as Fin:
        CodeTextInput.insert(tk.END, Fin.read())
    CodeTextInput.grid(column=2, row=0)
    
    def updateMacrocode():
        currentMacrocode = CodeTextInput.get("1.0", "end-1c")
        with open("currentMacrocode.txt", "w") as Fout:
            #print(currentMacrocode)
            Fout.write(currentMacrocode)
        try:
            assembleIJVM("currentMacrocode.txt")
        except Exception as e:
            print(e)
            print("Wrong macrocode syntax")
        else:
           closeMainWindow(None) 

    ttk.Button(codeWindow, text="Montar código", command=updateMacrocode).grid(column=2,row=0, sticky='S')

    simulationWindow = tk.Toplevel( mainWindow )
    simulationWindow.transient( mainWindow )
    simulationWindow.title( "Simulador" )
    simulationWindow.geometry("400x30+800+500")
    simulationWindowfrm = ttk.Frame(simulationWindow, padding=10)
    simulationWindowfrm.grid()
    ttk.Button(simulationWindow, text="próximo timestep", command=update).grid(column=1,row=0)
    ttk.Button(simulationWindow, text="play/pause", command=toggleRunningConstantly).grid(column=2,row=0)

    registersWindow = tk.Toplevel( mainWindow )
    registersWindow.transient( mainWindow )
    registersWindow.title( "Registradores" )
    registersWindow.minsize(600, 300)
    registersWindow.geometry("600x470+0+0")
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
    debugWindow.title( "Componentes" )
    debugWindow.minsize(600, 300)
    debugWindow.geometry("800x500+0+500")
    ttk.Separator(debugWindow).grid(column=0, row=1)

    debugLabels.append(createRegisterLabel(debugWindow, font, computer.Shifter, computer.Shifter.outBits, len(debugLabels)))
    debugLabels.append(createRegisterLabel(debugWindow, font, computer.ShifterControlLine, computer.ShifterControlLine.outBits, len(debugLabels)))
    debugLabels.append(createRegisterLabel(debugWindow, font, computer.ALU, computer.ALU.outBits, len(debugLabels)))
    debugLabels.append(createRegisterLabel(debugWindow, font, computer.ALUControlLine, computer.ALUControlLine.outBits, len(debugLabels)))
    debugLabels.append(createRegisterLabel(debugWindow, font, computer.Abus, computer.Abus.outBits, len(debugLabels)))
    debugLabels.append(createRegisterLabel(debugWindow, font, computer.Bbus, computer.Bbus.outBits, len(debugLabels)))
    debugLabels.append(createRegisterLabel(debugWindow, font, computer.Cbus, computer.Cbus.outBits, len(debugLabels)))
    debugLabels.append(createRegisterLabel(debugWindow, font, computer.Decoder, computer.Decoder.outBits, len(debugLabels)))
    debugLabels.append(createRegisterLabel(debugWindow, font, computer.controlMemory, computer.controlMemory.outBits, len(debugLabels)))
    debugLabels.append(createRegisterLabel(debugWindow, font, computer.controlMemory, computer.controlMemory.MPCBits, len(debugLabels)))
    debugLabels.append(createRegisterLabel(debugWindow, font, computer.NFF, computer.NFF.outBits, len(debugLabels)))
    debugLabels.append(createRegisterLabel(debugWindow, font, computer.ZFF, computer.ZFF.outBits, len(debugLabels)))
    debugLabels.append(createRegisterLabel(debugWindow, font, computer.HighBit, computer.HighBit.outBits, len(debugLabels)))


    OUTWindow = tk.Toplevel( mainWindow )
    OUTWindow.transient( mainWindow )
    OUTWindow.title( "OUT" )
    OUTWindow.minsize(100, 100)
    OUTWindow.geometry("380x470+1090+0")
    ttk.Separator(OUTWindow).grid(column=0, row=1)
    OUTText = scrolledtext.ScrolledText(OUTWindow, width = 25, height = 14, font = font)
    OUTText.grid(column=2, row=0)
    OUTText.config(state="disabled")





    mainWindow.bind( "<Escape>", closer )
    mainWindow.mainloop()

    computer.update()
    return UserExited.get()