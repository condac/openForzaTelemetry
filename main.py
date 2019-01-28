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

class Bar(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos


class PongGame(Widget):
    rpmobject = ObjectProperty(None)
    text1 = ObjectProperty(None)
    value1 = 1
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
        self.rpmobject.x = int(self.dataDict["CurrentEngineRpm"]["value"]) / 10

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
