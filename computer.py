import queue
from clock import Clock
from components import *


class UpdateSequencer:
    clock : Clock = Clock()
    pendingUpdates : dict[int, list[UpdateEntry]] = dict()

    def __init__(s, controlMemory : ControlMemory, memory : Memory):
        s.controlMemory = controlMemory
        s.memory = Memory 
        s.controlMemory.loadMicrocode("malcodeoutput.txt")
        s.registers = []
        s.clockComponent = Component(1, "Clock")
        pass

    def addRegister(s, register : Component):
        s.registers.append(register)

    def Update(s):
        currTime : int = s.clock.getTime()
        if(currTime == 0): #descending signal
            #update control Memory
            entry = UpdateEntry(s.controlMemory, s.clockComponent, s.controlMemory.updateDelay)
            s.pendingUpdates[entry.timeIdx] = [entry]
        
        elif(currTime == s.clock.clockInterval): #ascending signal
            #update Registers
            s.pendingUpdates[currTime] = []
            for register in s.registers:
                s.pendingUpdates[currTime].append(UpdateEntry(register, s.clockComponent, currTime))
            
            s.pendingUpdates[currTime].append(UpdateEntry(s.memory, s.clockComponent, currTime))
            

        if(s.pendingUpdates.get(currTime) == None):
            s.pendingUpdates[currTime] = []
        updatesForNow = s.pendingUpdates[currTime]
        res =[]
        for update in updatesForNow:
            res.append([update.caller.label, update.component.label])
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
                foundDuplicate = False
                for pendingUpdate in s.pendingUpdates[updateTime]:
                    if(pendingUpdate.caller == newEntry.caller and pendingUpdate.component == newEntry.component):
                        foundDuplicate = True
                if(not foundDuplicate):
                    s.pendingUpdates[updateTime].append(newEntry)

        s.pendingUpdates[currTime].clear()
        s.clock.timeStep()
                
class Computer:
    def __init__(s):
        s.controlMemory = ControlMemory(6)
        s.updateSequencer = UpdateSequencer(s.controlMemory, None)

        s.ALU = ALU(5)
        s.Shifter = Shifter(5)
        s.NLine = Line(1, "N line", 1, 0)
        s.ZLine = Line(1, "Z line", 1, 0)
        s.NFF = FlipFlop(1, "NFF")
        s.ZFF = FlipFlop(1, "ZFF")
        s.HighBit = HighBit(1)
        
        s.MIR = MIR(2)
        s.MAR = MAR(5)
        s.ORUnit = ORUnit(1)
        s.MBR = MBR(5, s.ORUnit)
        s.MPC = MPC(5)
        s.MDR = MDR(5, None)
        s.PC = PC(5)
        
        s.Memory = Memory(1, s.MBR, s.MDR)
        s.MDR.Memory = s.Memory
        s.updateSequencer.memory = s.Memory
        #MIR lines
        s.AddrLine = Line(1, "Addr line", 9, 0)
        s.JMPCLine = Line(1, "JMPC line", 1, 9)
        s.JAMNZLine = Line(1, "JAMNZ line", 2, 10)
        s.ShifterControlLine = Line(2, "Shifter control line", 2, 12)
        s.ALUControlLine = Line(1, "ALU control line", 6, 14)
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

        s.Decoder = Decoder(2)
        #NAO SEI SE ESTÁ NA ORDEM CERTA
        s.MDREnableOutput = Line(1, "enable output", 1, 0)
        s.PCEnableOutput = Line(1, "enable output", 1, 1)
        s.MBREnableOutput1 = Line(1, "enable output1", 1, 2) #MBR
        s.MBREnableOutput2 = Line(1, "enable output2", 1, 3) #MBRU
        s.SPEnableOutput = Line(1, "enable output", 1, 4)
        s.LVEnableOutput = Line(1, "enable output", 1, 5)
        s.CPPEnableOutput = Line(1, "enable output", 1, 6)
        s.TOSEnableOutput = Line(1, "enable output", 1, 7)
        s.OPCEnableOutput = Line(1, "enable output", 1, 8)

        s.Abus = Bus(2, "A bus", 32)
        s.Bbus = Bus(2, "B bus", 32)
        s.Cbus = Bus(2, "C bus", 32)
        s.MPCBus = Bus(2, "MPC bus", 9)

        s.SP = RWRegister(5, "SP", 32)
        s.LV = RWRegister(5, "LV", 32)
        s.CPP = RWRegister(5, "CPP", 32)
        s.TOS = RWRegister(5, "TOS", 32)
        s.OPC = RWRegister(5, "OPC", 32)
        s.H = H(5)


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
        s.PCEnableInput.addDependent(s.PC)
        s.MDREnableInput.addDependent(s.MDR)
        s.MAREnableInput.addDependent(s.MAR)
        s.MemoryControlLine.addDependent(s.Memory)
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
        s.MDREnableOutput.addDependent(s.MDR)
        s.PCEnableOutput.addDependent(s.PC)
        s.MBREnableOutput1.addDependent(s.MBR)
        s.MBREnableOutput2.addDependent(s.MBR)
        s.SPEnableOutput.addDependent(s.SP)
        s.LVEnableOutput.addDependent(s.LV)
        s.CPPEnableOutput.addDependent(s.CPP)
        s.TOSEnableOutput.addDependent(s.TOS)
        s.OPCEnableOutput.addDependent(s.OPC)

        s.Abus.addDependent(s.ALU)
        s.Bbus.addDependent(s.ALU)
        s.Cbus.addDependent(s.MAR)
        s.Cbus.addDependent(s.MDR)
        s.Cbus.addDependent(s.PC)
        s.Cbus.addDependent(s.MBR)
        s.Cbus.addDependent(s.SP)
        s.Cbus.addDependent(s.LV)
        s.Cbus.addDependent(s.CPP)
        s.Cbus.addDependent(s.TOS)
        s.Cbus.addDependent(s.OPC)
        s.Cbus.addDependent(s.H)

        s.MDR.addDependent(s.Bbus)
        s.PC.addDependent(s.Bbus)
        s.SP.addDependent(s.Bbus)
        s.LV.addDependent(s.Bbus)
        s.CPP.addDependent(s.Bbus)
        s.TOS.addDependent(s.Bbus)
        s.OPC.addDependent(s.Bbus)
        s.H.addDependent(s.Abus)

        s.MAR.addDependent(s.Memory)
        s.PC.addDependent(s.Memory)
        s.Memory.addDependent(s.MDR)
        s.Memory.addDependent(s.MBR)

        s.updateSequencer.addRegister(s.MAR)
        s.updateSequencer.addRegister(s.MDR)
        s.updateSequencer.addRegister(s.PC)
        s.updateSequencer.addRegister(s.MBR)
        s.updateSequencer.addRegister(s.SP)
        s.updateSequencer.addRegister(s.LV)
        s.updateSequencer.addRegister(s.CPP)
        s.updateSequencer.addRegister(s.TOS)
        s.updateSequencer.addRegister(s.OPC)
        s.updateSequencer.addRegister(s.H)
        s.reset()

    def reset(s):
        s.SP.inBits._setBitsFromInt(128)
        s.Abus.outBits.clear()
        s.AddrLine.outBits.clear()
        s.ALUControlLine.outBits.clear()
        s.Bbus.outBits.clear()
        s.BDecoderLine.outBits.clear()
        s.Cbus.outBits.clear()
        s.controlMemory.outBits.clear()
        s.CPPEnableInput.outBits.clear()
        s.CPPEnableOutput.outBits.clear()
        s.Decoder.outBits.clear()
        s.HEnableInput.outBits.clear()
        s.HighBit.outBits.clear()
        s.JAMNZLine.outBits.clear()
        s.JMPCLine.outBits.clear()
        s.LVEnableInput.outBits.clear()
        s.LVEnableOutput.outBits.clear()
        s.MAREnableInput.outBits.clear()
        s.MBREnableOutput1.outBits.clear()
        s.MBREnableOutput2.outBits.clear()
        s.MDREnableInput.outBits.clear()
        s.MDREnableOutput.outBits.clear()
        s.MemoryControlLine.outBits.clear()
        s.MPCBus.outBits.clear()
        s.NLine.outBits.clear()
        s.OPCEnableInput.outBits.clear()
        s.OPCEnableOutput.outBits.clear()
        s.ORUnit.outBits.clear()
        s.PCEnableInput.outBits.clear()
        s.PCEnableOutput.outBits.clear()
        s.Shifter.outBits.clear()
        s.ShifterControlLine.outBits.clear()
        s.SPEnableInput.outBits.clear()
        s.SPEnableOutput.outBits.clear()
        s.TOSEnableInput.outBits.clear()
        s.TOSEnableOutput.outBits.clear()
        s.ZLine.outBits.clear()
        s.ALU.outBits.clear()
        s.CPP.inBits.clear()
        s.H.inBits.clear()
        s.LV.inBits.clear()
        s.MAR.inBits.clear()
        s.MBR.inBits.clear()
        s.MDR.inBits.clear()
        s.MIR.outBits.clear()
        s.MPC.outBits.clear()
        s.OPC.inBits.clear()
        s.PC.inBits.clear()
        s.SP.inBits.clear()
        s.TOS.inBits.clear()
        s.ZFF.inBits.clear()
        s.updateSequencer.clock.currentTime = 0
        s.updateSequencer.pendingUpdates.clear()



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



    