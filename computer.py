import queue
from clock import Clock
from components import *


class UpdateSequencer:
    clock : Clock = Clock()
    pendingUpdates : dict[int, list[UpdateEntry]] = dict()

    def __init__(s, controlMemory : ControlMemory):
        s.controlMemory = controlMemory
        s.registers = []
        s.clockComponent = Component(1, "Clock")
        pass

    def addRegister(s, register : Component):
        s.registers.append(register)

    def Update(s):
        currTime : int = s.clock.getTime()
        if(currTime == 0): #descending signal
            #update control Memory
            entry = UpdateEntry(s.controlMemory, s.clockComponent, 0)
            s.pendingUpdates[0] = [entry]
        
        elif(currTime == s.clock.clockInterval): #ascending signal
            #update Registers
            s.pendingUpdates[currTime] = []
            for register in s.registers:
                s.pendingUpdates[currTime].append(UpdateEntry(register, s.clockComponent, currTime))

        updatesForNow = s.pendingUpdates[currTime]
        res =[]
        for update in updatesForNow:
            res.append(update.component.label)
        print(res)
        for entry in updatesForNow:
            #print("updating " + entry.component.label + "...")
            newUpdates : list[UpdateEntry] = entry.component.update(currTime, entry.caller)
            if newUpdates == None:
                continue
            for newEntry in newUpdates:
                updateTime : int = (currTime + newEntry.component.updateDelay)%(s.clock.clockInterval + s.clock.pulseWidth)
                if s.pendingUpdates.get(updateTime) == None:
                    s.pendingUpdates[updateTime] = []
                s.pendingUpdates[updateTime].append(newEntry)

        s.pendingUpdates[currTime].clear()
        s.clock.timeStep()
                
class Computer:
    def __init__(s):
        s.controlMemory = ControlMemory(1)
        s.Memory = Memory(1)
        s.updateSequencer = UpdateSequencer(s.controlMemory)

        s.ALU = ALU(1)
        s.Shifter = Shifter(1)
        s.NLine = Line(1, "N line", 1, 0)
        s.ZLine = Line(1, "Z line", 1, 0)
        s.NFF = FlipFlop(1, "NFF")
        s.ZFF = FlipFlop(1, "ZFF")
        s.HighBit = HighBit(1)
        
        s.MBR = MBR(1)
        s.MPC = MPC(1)
        s.MIR = MIR(1)
        #MIR lines
        s.AddrLine = Line(1, "Addr line", 9, 0)
        s.JMPCLine = Line(1, "JMPC line", 1, 9)
        s.JAMNZLine = Line(1, "JAMNZ line", 2, 10)
        s.ShifterControlLine = Line(2, "Shifter control line", 2, 12)
        s.ALUControlLine = Line(6, "ALU control line", 6, 14)
        s.HEnableInput = Line(1, "enable input", 1, 20)
        s.OPCEnableInput = Line(1, "enable input", 1, 21)
        s.TOSEnableInput = Line(1, "enable input", 1, 22)
        s.CPPEnableInput = Line(1, "enable input", 1, 23)
        s.LVEnableInput = Line(1, "enable input", 1, 24)
        s.SPEnableInput = Line(1, "enable input", 1, 25)
        s.PCEnableInput = Line(1, "enable input", 1, 26)
        s.MDREnableInput = Line(1, "enable input", 1, 27)
        s.MAREnableInput = Line(1, "enable input", 1, 28)
        s.MemoryControlLine = Line(1, "Memory control line", 3, 29)
        s.BDecoderLine = Line(1, "B decoder line", 4, 32)

        s.ORUnit = ORUnit(1)
        s.Decoder = Decoder(1)
        #NAO SEI SE ESTÁ NA ORDEM CERTA
        s.MDREnableOutput = Line(1, "enable output", 1, 0)
        s.PCEnableOutput = Line(1, "enable output", 1, 1)
        s.MBREnableOutput1 = Line(1, "enable output1", 1, 2)
        s.MBREnableOutput2 = Line(1, "enable output2", 1, 3)
        s.SPEnableOutput = Line(1, "enable output", 1, 4)
        s.LVEnableOutput = Line(1, "enable output", 1, 5)
        s.CPPEnableOutput = Line(1, "enable output", 1, 6)
        s.TOSEnableOutput = Line(1, "enable output", 1, 7)
        s.OPCEnableOutput = Line(1, "enable output", 1, 8)

        s.Abus = Bus(1, "A bus", 32)
        s.Bbus = Bus(1, "B bus", 32)
        s.Cbus = Bus(1, "C bus", 32)
        s.MPCBus = Bus(1, "MPC bus", 9)

        s.SP = RWRegister(1, "SP", 32)
        s.LV = RWRegister(1, "LV", 32)
        s.CPP = RWRegister(1, "CPP", 32)
        s.TOS = RWRegister(1, "TOS", 32)
        s.OPC = RWRegister(1, "OPC", 32)
        s.H = H(1)


        s.controlMemory.addDependent(s.MIR)
        s.ALU.addDependent(s.Shifter)
        s.Shifter.addDependent(s.Cbus)
        s.NLine.addDependent(s.NFF)
        s.ZLine.addDependent(s.ZFF)
        s.NFF.addDependent(s.HighBit)
        s.ZFF.addDependent(s.HighBit)
        s.HighBit.addDependent(s.MPC)

        s.MBR.addDependent(s.ORUnit)
        s.MBR.addDependent(s.Bbus)
        s.MPC.addDependent(s.MPCBus)
        s.MPCBus.addDependent(s.controlMemory)


        s.MIR.addDependent(s.AddrLine)
        s.MIR.addDependent(s.JMPCLine)
        s.MIR.addDependent(s.JAMNZLine)
        s.MIR.addDependent(s.ShifterControlLine)
        s.MIR.addDependent(s.ALUControlLine)

        s.MIR.addDependent(s.MAREnableInput)
        s.MIR.addDependent(s.MDREnableInput)
        s.MIR.addDependent(s.PCEnableInput)
        s.MIR.addDependent(s.SPEnableInput)
        s.MIR.addDependent(s.LVEnableInput)
        s.MIR.addDependent(s.CPPEnableInput)
        s.MIR.addDependent(s.TOSEnableInput)
        s.MIR.addDependent(s.OPCEnableInput)
        s.MIR.addDependent(s.HEnableInput)

        s.MIR.addDependent(s.MemoryControlLine)
        s.MIR.addDependent(s.BDecoderLine)
        
        s.AddrLine.addDependent(s.ORUnit)
        s.JMPCLine.addDependent(s.ORUnit)
        s.JAMNZLine.addDependent(s.HighBit)
        s.ShifterControlLine.addDependent(s.Shifter)
        s.ALUControlLine.addDependent(s.ALU)
        s.HEnableInput.addDependent(s.H)
        s.OPCEnableInput.addDependent(s.OPC)
        s.TOSEnableInput.addDependent(s.TOS)
        s.CPPEnableInput.addDependent(s.CPP)
        s.LVEnableInput.addDependent(s.LV)
        s.SPEnableInput.addDependent(s.SP)
        #s.PCEnableInput.addDependent(s.PC)
        #s.MDREnableInput.addDependent(s.MDR)
        #s.MAREnableInput.addDependent(s.MAR)
        #s.MemoryControlLine.addDependent(s.Memory) ???
        s.BDecoderLine.addDependent(s.Decoder)

        s.ORUnit.addDependent(s.MPC)
        s.Decoder.addDependent(s.MDREnableOutput)
        s.Decoder.addDependent(s.PCEnableOutput)
        s.Decoder.addDependent(s.MBREnableOutput1)
        s.Decoder.addDependent(s.MBREnableOutput2)
        s.Decoder.addDependent(s.SPEnableOutput)
        s.Decoder.addDependent(s.LVEnableOutput)
        s.Decoder.addDependent(s.CPPEnableOutput)
        s.Decoder.addDependent(s.TOSEnableOutput)
        s.Decoder.addDependent(s.OPCEnableOutput)
        #s.MDREnableOutput.addDependent(s.MDR)
        #s.PCEnableOutput.addDependent(s.PC)
        s.MBREnableOutput1.addDependent(s.MBR)
        s.MBREnableOutput2.addDependent(s.MBR)
        s.SPEnableOutput.addDependent(s.SP)
        s.LVEnableOutput.addDependent(s.LV)
        s.CPPEnableOutput.addDependent(s.CPP)
        s.TOSEnableOutput.addDependent(s.TOS)
        s.OPCEnableOutput.addDependent(s.OPC)

        s.Abus.addDependent(s.ALU)
        s.Bbus.addDependent(s.ALU)
        #s.Cbus.addDependent(s.MAR)
        #s.Cbus.addDependent(s.MDR)
        #s.Cbus.addDependent(s.PC)
        s.Cbus.addDependent(s.MBR)
        s.Cbus.addDependent(s.SP)
        s.Cbus.addDependent(s.LV)
        s.Cbus.addDependent(s.CPP)
        s.Cbus.addDependent(s.TOS)
        s.Cbus.addDependent(s.OPC)
        s.Cbus.addDependent(s.H)

        #s.MDR.addDependent(s.Bbus)
        #s.PC.addDependent(s.Bbus)
        s.SP.addDependent(s.Bbus)
        s.LV.addDependent(s.Bbus)
        s.CPP.addDependent(s.Bbus)
        s.TOS.addDependent(s.Bbus)
        s.OPC.addDependent(s.Bbus)
        s.H.addDependent(s.Abus)

        #s.MAR.addDependent(s.Memory)
        #s.MDR.addDependent(s.Memory)
        #s.PC.addDependent(s.Memory)
        #s.Memory.addDependent(s.MDR)
        #s.Memory.addDependent(s.MBR)

#       s.updateSequencer.addRegister(s.MAR)
#       s.updateSequencer.addRegister(s.MDR)
#       s.updateSequencer.addRegister(s.PC)
        s.updateSequencer.addRegister(s.MBR)
        s.updateSequencer.addRegister(s.SP)
        s.updateSequencer.addRegister(s.LV)
        s.updateSequencer.addRegister(s.CPP)
        s.updateSequencer.addRegister(s.TOS)
        s.updateSequencer.addRegister(s.OPC)
        s.updateSequencer.addRegister(s.H)



    def update(s):
        s.updateSequencer.Update()
        """
        res = list(map(s.updateSequencer.pendingUpdates.get, s.updateSequencer.pendingUpdates.keys()))
        res1 = []
        for ist in res:
            res1.append([])
            for elem in ist:
                res1[len(res1)-1].append(elem.component.label)
        print(res1)
        """


computer : Computer = Computer()
for i in range(computer.updateSequencer.clock.clockInterval + computer.updateSequencer.clock.pulseWidth+3):
    computer.update()

    