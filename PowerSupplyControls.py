import sys,os
sys.path.append(os.path.dirname(__file__))
import plx_gpib_ethernet

class gpibControl:
    def __init__(self, host, addr):
        self.gpib = plx_gpib_ethernet.PrologixGPIBEthernet(host=host)
        self.gpib.connect()
        self.addr=addr

    def close(self):
        self.gpib.close()

    def connect(self):
        self.gpib.connect()

    def reconnect(self):
        self.gpib.reconnect()

    def disconnect(self):
        self.gpib.disconnect()

    def select(self):
        if not self.addr is None:
            self.gpib.select(self.addr)

    def ID(self):
        self.select()
        return self.gpib.query("*IDN?")[:-1]

    def testQuery(self,q):
        self.select()
        return self.gpib.query(q)[:-1]


class Agilent3648A(gpibControl):
    def __init__(self, host, addr):
        gpibControl.__init__(self, host, addr)
        #check we have the correct ID for Agilent 3648A
        modelID=self.ID()
        expectedModel='Agilent Technologies,E3648A,0,1.7-5.0-1.0'
        assert modelID==expectedModel, f"Incorrect Model for Addr {addr}\nRead:     {modelID}\nExpected: {expectedModel}"

    def IsOn(self):
        self.select()
        return self.gpib.query("OUTP:STAT?")[:-1]

    def TurnOn(self):
        self.select()
        self.gpib.write("OUTP ON")

    def TurnOff(self):
        self.select()
        self.gpib.write("OUTP OFF")

    def ReadPower(self, output=1):
        self.select()
        v=self.gpib.query(f"INST:SEL OUT{output}\nMEAS:VOLT?")[:-1]
        i=self.gpib.query(f"INST:SEL OUT{output}\nMEAS:CURR?")[:-1]
        p=self.gpib.query("OUTP:STAT?")[:-1]
        return int(p), float(v),float(i)

    def ReadPower_1(self):
        return self.ReadPower(1)

    def ReadPower_2(self):
        return self.ReadPower(2)

    def ReadLimits(self, output=1):
        self.select()
        v=self.gpib.query(f"INST:SEL OUT{output}\nVOLT?")[:-1]
        i=self.gpib.query(f"INST:SEL OUT{output}\nCURR?")[:-1]
        return float(v),float(i)

    def ReadLimits_1(self):
        return self.ReadLimits(1)

    def ReadLimits_2(self):
        return self.ReadLimits(2)

    def SetLimits(self, voltage, current, output=1):
        self.select()
        self.gpib.write(f"INST:SEL OUT{output}\nVOLT {voltage}")
        self.gpib.write(f"INST:SEL OUT{output}\nCURR {current}")

    def SetLimits_1(self,v=1.2,i=0.6):
        self.SetLimits(output=1, voltage=v, current=i)

    def SetLimits_2(self,v=1.2,i=0.6):
        self.SetLimits(output=2, voltage=v, current=i)


class Agilent3642A(gpibControl):
    def __init__(self, host, addr):
        gpibControl.__init__(self, host, addr)
        #check we have the correct ID for Agilent 3642AA
        modelID=self.ID()
        expectedModel='Agilent Technologies,E3642A,0,1.6-5.0-1.0'
        assert modelID==expectedModel, f"Incorrect Model for Addr {addr}\nRead:     {modelID}\nExpected: {expectedModel}"

    def IsOn(self):
        self.select()
        return self.gpib.query("OUTP:STAT?")[:-1]

    def TurnOn(self):
        self.select()
        self.gpib.write("OUTP ON")

    def TurnOff(self):
        self.select()
        self.gpib.write("OUTP OFF")

    def ReadPower(self):
        self.select()
        v=self.gpib.query(f"MEAS:VOLT?")[:-1]
        i=self.gpib.query(f"MEAS:CURR?")[:-1]
        p=self.gpib.query("OUTP:STAT?")[:-1]
        return int(p), float(v),float(i)

    def ReadLimits(self):
        self.select()
        v=self.gpib.query(f"VOLT?")[:-1]
        i=self.gpib.query(f"CURR?")[:-1]
        return float(v),float(i)

    def SetLimits(self, voltage, current):
        self.select()
        self.gpib.write(f"VOLT {voltage}")
        self.gpib.write(f"CURR {current}")


class Agilent3633A(gpibControl):
    def __init__(self, host, addr):
        gpibControl.__init__(self, host, addr)
        #check we have the correct ID for Agilent 3633A
        modelID=self.ID()
        expectedModel='HEWLETT-PACKARD,E3633A,0,1.7-5.0-1.0'
        assert modelID==expectedModel, f"Incorrect Model for Addr {addr}\nRead:     {modelID}\nExpected: {expectedModel}"

    def IsOn(self):
        self.select()
        return self.gpib.query("OUTP:STAT?")[:-1]

    def TurnOn(self):
        self.select()
        self.gpib.write("OUTP ON")

    def TurnOff(self):
        self.select()
        self.gpib.write("OUTP OFF")

    def ReadPower(self):
        self.select()
        v=self.gpib.query(f"MEAS:VOLT?")[:-1]
        i=self.gpib.query(f"MEAS:CURR?")[:-1]
        p=self.gpib.query("OUTP:STAT?")[:-1]
        return int(p), float(v),float(i)

    def ReadLimits(self):
        self.select()
        v=self.gpib.query(f"VOLT?")[:-1]
        i=self.gpib.query(f"CURR?")[:-1]
        return float(v),float(i)

    def SetLimits(self, voltage, current):
        self.select()
        self.gpib.write(f"VOLT {voltage}")
        self.gpib.write(f"CURR {current}")



class ObelixSupplies(gpibControl):
    def select_addr(self, addr):
        self.gpib.select(addr)

    def SetVoltage(self, voltage):
        self.select_addr(6)

        if float(voltage)<=1.5 and float(voltage) >= 0.9:
            self.gpib.write(f"V {voltage}")
            return True
        else:
            print(f'Selected voltage ({voltage}) outside of defined safe range 0.9-1.5')
            return False

    def SetLimits(self, voltage, current=0.6):
        self.select_addr(6)

        if float(voltage)<=1.5 and float(voltage) >= 0.9:
            self.gpib.write(f"V {voltage}")
            self.gpib.write(f"I {current}")
            return True
        else:
            print(f'Selected voltage ({voltage}) outside of defined safe range 0.9-1.5')
            return False

    def ASICOn(self,voltage=None):
        self.select_addr(6)
        x=self.gpib.query('++addr')

        if voltage is None:
            is_set=self.SetVoltage(1.2)
        else:
            is_set=self.SetVoltage(float(voltage))

        if is_set:
            self.gpib.write("I 0.6")
            self.gpib.write("OP 1")

    def ASICOff(self):
        self.select_addr(6)
#        x=self.gpib.query('++addr')
        self.gpib.write("OP 0")

    def ReadPower(self):
        self.select_addr(6)
        # x=self.gpib.query('++addr')
        # output=self.gpib.query("OP 0?")
        output=1
        v=self.gpib.query("VO?")
        v=float(v[:-2])
        i=self.readCurrent()
        return output,v,i

    def ConfigRTD(self):
        self.select_addr(14)
        self.gpib.write('*RST')
        self.gpib.write("FUNC 'FRES'")
        self.gpib.write("FRES:RANG 1E3")

    def readRTD(self):
        self.select_addr(14)
        resistance=float(self.gpib.query(":READ?"))
#        resistance=float(self.gpib.read()[:-1])
        temperature=((resistance/1000)-1)/0.00385
        return temperature, resistance

    def ConfigReadCurrent(self):
        self.select_addr(14)
        self.gpib.write("*RST")
        self.gpib.write("FUNC 'CURR:DC'")
        self.gpib.write("CURR:RANGE 1.")

    def readCurrent(self):
        self.select_addr(14)
        current=float(self.gpib.query(":READ?"))
        return current

knownModelTypes=['Agilent Technologies,E3648A,0,1.7-5.0-1.0',
                 'Agilent Technologies,E3642A,0,1.6-5.0-1.0',
                 'HEWLETT-PACKARD,E3633A,0,1.7-5.0-1.0']

def getPowerSupply(ip, addr):
    ps=gpibControl(ip,addr)
    model=ps.ID()
    ps.disconnect()
    ps.close()

    assert model in knownModelTypes

    if model=='Agilent Technologies,E3648A,0,1.7-5.0-1.0':
        return Agilent3648A(ip,addr)
    if model=='Agilent Technologies,E3642A,0,1.6-5.0-1.0':
        return Agilent3642A(ip,addr)
    if model=='HEWLETT-PACKARD,E3633A,0,1.7-5.0-1.0':
        return Agilent3633A(ip,addr)
