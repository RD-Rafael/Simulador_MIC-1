import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import Image

mainWindow = tk.Tk()
mainWindow.title( "main" )
ttk.Button(mainWindow, text="Quit", command=mainWindow.destroy).grid(column=1, row=0)

codeWindow = tk.Toplevel( mainWindow )
codeWindow.transient( mainWindow )
codeWindow.title( "Montador" )
codeWindow.minsize(600, 300)
frm = ttk.Frame(codeWindow, padding=10)
frm.grid()
CodeTextInput = scrolledtext.ScrolledText(frm, width = 25, height = 30, font = ("Times New Roman", 20))
CodeTextInput.grid(column=2, row=0)

print(CodeTextInput.configure().keys())
print(CodeTextInput.configure()["font"])

def closer( event ):
    mainWindow.destroy()

mainWindow.bind( "<Escape>", closer )
mainWindow.mainloop()
