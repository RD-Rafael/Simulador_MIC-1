from computer import *
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import Image

computer : Computer = Computer()
def update():
    computer.update()
    SPlabel.configure(text="SP" + str(computer.SP.outBits.toInteger()))
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
registersWindowfrm = ttk.Frame(registersWindow, padding=10)
ttk.Separator(registersWindow).grid(column=0, row=1)
SPlabel : ttk.Label = ttk.Label(registersWindow, text="SP", font=font)
SPlabel.grid(column=1,row=0)

registersWindowfrm.grid()

print(CodeTextInput.configure().keys())
print(CodeTextInput.configure()["font"])

def closer( event ):
    mainWindow.destroy()

mainWindow.bind( "<Escape>", closer )
mainWindow.mainloop()

computer.update()