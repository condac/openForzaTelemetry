from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty,\
    ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
import socket
import struct

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

class Bar(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    r = NumericProperty(0)
    g = NumericProperty(0)
    b = NumericProperty(0)
    prevRPM = 0
    prevPower = 0

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos
    def setColor(self,inR,inG,inB):
        self.r = inR
        self.g = inG
        self.b = inB
    def calcShiftLight(self, inRpm, inPower, inGear, inGearRec) :

        result = False
        #currentRpm = dataDict["CurrentEngineRpm"]["value"]
        #currentPower = dataDict["Power"]["value"]

        if (self.prevRPM < inRpm) :
            if (self.prevPower > inPower) :

                result = True
        self.prevRPM = inRpm
        self.prevPower = inPower
        if (result):
            if (inGear != inGearRec):
                #print(inGear,inGearRec)
                self.setColor(1,0,0)
            else:
                self.setColor(1,1,0)
        else:
            if (inGear != inGearRec):
                #print(inGear,inGearRec)
                self.setColor(1,0,0)
            else:
                self.setColor(1,1,1)
        return result

class PongGame(Widget):
    rpmobject = ObjectProperty(None)
    gearobject = ObjectProperty(None)
    rpm_color = (1,1,1)
    rpmMax = ObjectProperty(None)
    text1 = ObjectProperty(None)
    value1 = 1
    x1 = ObjectProperty(None)

    tire_temp_fl = ObjectProperty(None)
    tire_temp_fr = ObjectProperty(None)
    tire_temp_rl = ObjectProperty(None)
    tire_temp_rr = ObjectProperty(None)

    fuel = ObjectProperty(None)
    fuel_DTE_last = 1.0
    fuel_DTE = ObjectProperty(None)
    fuel_DTE_lastlap = 0

    bestgear = ObjectProperty(None)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', localPort))
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


    def serve_ball(self, vel=(4, 0)):
        #self.value1 = ObjectProperty(None)
        x = 1

    def update(self, dt):
        message, address = self.s.recvfrom(1024)
        for key,item in self.dataDict.items():
            (value,) = struct.unpack_from(item["type"],message, offset=item["offset"])
            item["value"] = value
            #print(value)
        self.text1 = int(self.dataDict["CurrentEngineRpm"]["value"])
        if (self.dataDict["EngineMaxRpm"]["value"] != 0):
            self.rpmobject.width = self.width * self.dataDict["CurrentEngineRpm"]["value"] / self.dataDict["EngineMaxRpm"]["value"]
        self.rpmobject.calcShiftLight(self.dataDict["CurrentEngineRpm"]["value"], self.dataDict["Power"]["value"], self.dataDict["Gear"]["value"], self.gearobject.getBest(self.dataDict["Speed"]["value"], self.dataDict["Gear"]["value"]))
        self.tire_temp_fl = int(self.f2c(self.dataDict["TireTempFrontLeft"]["value"]))
        self.tire_temp_fr = int(self.f2c(self.dataDict["TireTempFrontRight"]["value"]))
        self.tire_temp_rl = int(self.f2c(self.dataDict["TireTempRearLeft"]["value"]))
        self.tire_temp_rr = int(self.f2c(self.dataDict["TireTempRearRight"]["value"]))

        self.fuel = int(self.dataDict["Fuel"]["value"]*100)
        if (self.dataDict["LapNumber"]["value"]> self.fuel_DTE_lastlap) :

            fuelDelta = self.fuel_DTE_last - self.dataDict["Fuel"]["value"]
            self.fuel_DTE = float(int((self.dataDict["Fuel"]["value"] / fuelDelta)*10))/10
            self.fuel_DTE_last = self.dataDict["Fuel"]["value"]
            self.fuel_DTE_lastlap = self.dataDict["LapNumber"]["value"]

        self.gearobject.giveData(self.dataDict["Gear"]["value"], self.dataDict["Speed"]["value"], self.dataDict["AccelerationZ"]["value"])
        self.bestgear = self.gearobject.getBestStr(self.dataDict["Speed"]["value"], self.dataDict["Gear"]["value"])

    def f2c(self,Fahrenheit):
        Celsius = (Fahrenheit - 32) * 5.0/9.0
        return Celsius
    def on_touch_move(self, touch):
        if touch.x < self.width / 3:
            self.player1.center_y = touch.y
        if touch.x > self.width - self.width / 3:
            self.player2.center_y = touch.y


class PongApp(App):
    def build(self):
        game = PongGame()
        game.serve_ball()
        Clock.schedule_interval(game.update, 1.0 / 120.0)
        return game


if __name__ == '__main__':
    PongApp().run()