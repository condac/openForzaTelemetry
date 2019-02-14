from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty,\
    ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
import socket
import struct
import select

localPort = 20002
bufferSize = 1024

class PongPaddle(Widget):
    score = NumericProperty(0)

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            bounced = Vector(-1 * vx, vy)
            vel = bounced * 1.1
            ball.velocity = vel.x, vel.y + offset


class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

class BestGear(Widget):
    speedArray = []
    for i in range(500):
        data = {}
        data["gear"] = 0
        data["acc"] = 0.0
        speedArray.append(data)

    gear = 2

    def giveData(self,inGear, inSpeed, inAcc):
        speed = int(inSpeed*3.6)
        compare = float(self.speedArray[speed]["acc"])
        if (compare < inAcc) :
            self.speedArray[speed]["acc"] = inAcc
            self.speedArray[speed]["gear"] = inGear

        return
    def getBest(self,inSpeed, inGear):
        speed = int(inSpeed*3.6)
        out = self.speedArray[speed]["gear"]
        return out
    def getBestStr(self,inSpeed, inGear):
        out = str(inGear)+"("+str(self.getBest(inSpeed, inGear))+")"
        return out

class FuelDTE(Widget):
    fuel_DTE_last = 1.0
    fuel_DTE_lastlap = 0
    out = "Firstlap"

    def getDTE(self,dataDict):
        if (dataDict["LapNumber"]["value"]> self.fuel_DTE_lastlap) :
            fuelDelta = self.fuel_DTE_last - dataDict["Fuel"]["value"]
            self.out = float(int((dataDict["Fuel"]["value"] / fuelDelta)*10))/10
            self.fuel_DTE_last = dataDict["Fuel"]["value"]
            self.fuel_DTE_lastlap = dataDict["LapNumber"]["value"]
        if (self.fuel_DTE_last<dataDict["Fuel"]["value"]) :
            print("refueled")
            self.out = "Refueled"
            self.fuel_DTE_last = 1.0
            self.fuel_DTE_lastlap = dataDict["LapNumber"]["value"]
        return self.out

class Boost(Widget):
    boost = NumericProperty(0)
    def setBoost(self,dataDict):
        self.boost = round(dataDict["Boost"]["value"] / 14.504, 2)
        return
    def getBoost(self):

        return self.boost
class BoostGauge(Widget):
    angle = NumericProperty(0)
    def setBoost(self,dataDict):
        self.angle = (dataDict["Boost"]["value"] *-6.0)+175
        return
    def getBoost(self):

        return self.angle

class RevLimit(Widget):
    r = NumericProperty(0)
    g = NumericProperty(0)
    b = NumericProperty(0)
    def setRevLimit(self,input, width):
        self.parent.rpmobject.revLimitPercent = input/  self.parent.width
        print("rpm limit",self.parent.rpmobject.revLimitPercent )

class Bar(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    r = NumericProperty(0)
    g = NumericProperty(0)
    b = NumericProperty(0)
    prevRPM = 0
    prevPower = 0
    revLimitPercent = 0.8

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos
    def setColor(self,inR,inG,inB):
        self.r = inR
        self.g = inG
        self.b = inB
    def calcShiftLight(self, dataDict, inGearRec) :

        result = False
        inRpm = dataDict["CurrentEngineRpm"]["value"]
        inPower = dataDict["Power"]["value"]
        inGear = dataDict["Gear"]["value"]
        maxRpm = dataDict["EngineMaxRpm"]["value"]
        #currentRpm = dataDict["CurrentEngineRpm"]["value"]
        #currentPower = dataDict["Power"]["value"]

        #if (self.prevRPM < inRpm) :
        #    if (self.prevPower > inPower) :
#
        #        result = True

        self.prevRPM = inRpm
        self.prevPower = inPower
        if (inRpm>(maxRpm*self.revLimitPercent)  ):
            result = True

        if (result):
            self.setColor(1,0,0)

        else:
            if (inGear > inGearRec):
                #print(inGear,inGearRec)
                self.setColor(0,1,0)
            else:
                self.setColor(1,1,1)
        return result

class PongGame(Widget):
    rpmobject = ObjectProperty(None)
    gearobject = ObjectProperty(None)
    fuelDTEobject = ObjectProperty(None)
    boostObject = ObjectProperty(None)
    boostGaugeObject = ObjectProperty(None)
    rpm_color = (1,1,1)
    rpmMax = ObjectProperty(None)
    text1 = ObjectProperty(None)
    value1 = 1
    x1 = ObjectProperty(None)
    revlimitObject = ObjectProperty(None)


    tire_temp_fl = ObjectProperty(None)
    tire_temp_fr = ObjectProperty(None)
    tire_temp_rl = ObjectProperty(None)
    tire_temp_rr = ObjectProperty(None)

    fuel = ObjectProperty(None)

    fuel_DTE = ObjectProperty(None)


    bestgear = ObjectProperty(None)
    ip = ObjectProperty(None)
    bestLap = ObjectProperty(None)
    lastLap = ObjectProperty(None)


    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', localPort))
    #s.setblocking(0)
    dataDict = {}
    with open("dataformat.csv", "r") as dataformatfile:

        offset = 0;

        for line in dataformatfile:
            newdata = {}

            data = line.split(' ')
            type = data[0][:1]
            tmp = data[1].split(';')
            name = tmp[0]
            newoffset = offset
            if (type == 'i') : # signed integer
                newlength = 4
                offset = offset + newlength
            elif (type == 'I') : # unsigned integer
                newlength = 4
                offset = offset + newlength
            elif (type == 'f') : # 32-bit float
                newlength = 4
                offset = offset + newlength
            elif (type == 'H') : # 16-bit unsigned integer
                newlength = 2
                offset = offset + newlength
            elif (type == 'B') : # 8-bit unsigned integer
                newlength = 1
                offset = offset + newlength
            else :
                print("error in keys",data )
                sys.exit(1)
            #print(type,name)
            newdata["type"] = type
            newdata["offset"] = newoffset
            newdata["length"] = newlength
            #newdata["value"] = 0
            dataDict[name] = newdata
            #print(self.dataDict)


    def serve_ball(self):
        #self.value1 = ObjectProperty(None)
        x = 1
        self.ip = self.getIP()

    def update(self, dt):
        message, address = self.s.recvfrom(1024)
        for key,item in self.dataDict.items():
            (value,) = struct.unpack_from(item["type"],message, offset=item["offset"])
            item["value"] = value
            #print(value)
        if (self.dataDict["IsRaceOn"]["value"] == 1) :
            #print(self.dataDict["EngineMaxRpm"]["value"])
            self.text1 = int(self.dataDict["CurrentEngineRpm"]["value"])
            if (self.dataDict["EngineMaxRpm"]["value"] != 0):
                self.rpmobject.width = self.width * self.dataDict["CurrentEngineRpm"]["value"] / self.dataDict["EngineMaxRpm"]["value"]
            self.rpmobject.calcShiftLight(self.dataDict, self.gearobject.getBest(self.dataDict["Speed"]["value"], self.dataDict["Gear"]["value"]))
            self.tire_temp_fl = int(self.f2c(self.dataDict["TireTempFrontLeft"]["value"]))
            self.tire_temp_fr = int(self.f2c(self.dataDict["TireTempFrontRight"]["value"]))
            self.tire_temp_rl = int(self.f2c(self.dataDict["TireTempRearLeft"]["value"]))
            self.tire_temp_rr = int(self.f2c(self.dataDict["TireTempRearRight"]["value"]))

            self.fuel = int(self.dataDict["Fuel"]["value"]*100)
            self.fuel_DTE = self.fuelDTEobject.getDTE(self.dataDict)


            self.gearobject.giveData(self.dataDict["Gear"]["value"], self.dataDict["Speed"]["value"], self.dataDict["AccelerationZ"]["value"])
            self.bestgear = self.gearobject.getBestStr(self.dataDict["Speed"]["value"], self.dataDict["Gear"]["value"])
            self.bestLap = "BestLap: "+self.time2str(self.dataDict["BestLap"]["value"])
            self.lastLap = "LastLap: "+self.time2str(self.dataDict["LastLap"]["value"])

            self.boostObject.setBoost(self.dataDict)
            self.boostGaugeObject.setBoost(self.dataDict)

        ready = select.select([self.s], [], [], 0.001)
        if ready[0]:
            #print("flushing network")
            message, address = self.s.recvfrom(1024)
            ready = select.select([self.s], [], [], 0.001)
            if ready[0]:
                print("double flushing network")
                message, address = self.s.recvfrom(1024)


    def f2c(self,Fahrenheit):
        Celsius = (Fahrenheit - 32) * 5.0/9.0
        return Celsius
    def on_touch_move(self, touch):
        self.revlimitObject.center_x = touch.x
        self.revlimitObject.setRevLimit(touch.x, self.width)
        #reset?
        return
    def getIP(self):

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP+":"+str(localPort)
    def time2str(self, inTime):
        m, s = divmod(inTime, 60)

        out = "%02d:%02.3f" % (m, s)

        return out


class PongApp(App):
    def build(self):
        game = PongGame()
        game.serve_ball()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game


if __name__ == '__main__':
    PongApp().run()
