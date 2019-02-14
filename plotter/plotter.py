import socket
import struct
import sys
import serial

import pygame
import pygame.freetype

# Pygame stuff
pygame.init()
screen_x = 1280
screen_y = 1000 # times 2
screen = pygame.display.set_mode((screen_x, screen_y),  pygame.DOUBLEBUF, 32)
GAME_FONT = pygame.freetype.SysFont(name="default", size=24)

su = pygame.Surface((screen_x,screen_y), pygame.SRCALPHA)   # per-pixel alpha
su.fill((0,0,0,1))                         # notice the alpha value in the color

clock = pygame.time.Clock()

localIP = ""
localPort = 20003
bufferSize = 1024

dataDict = {}
#arduino = serial.Serial('/dev/ttyACM0', 9600)

with open("../dataformat.csv", "r") as dataformatfile:
    array = []
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
        #print(dataDict)
        array.append(line)
#print(array)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', localPort))


prevRPM = 0
prevPower = 0
def calcShiftLight() :
    global prevRPM
    global prevPower
    result = False
    currentRpm = dataDict["CurrentEngineRpm"]["value"]
    currentPower = dataDict["Power"]["value"]

    if (prevRPM < currentRpm) :
        if (prevPower > currentPower) :

            result = True
    prevRPM = currentRpm
    prevPower = currentPower

    return result

def speed2X(inSpeed) :
    global screen_x
    maxSpeed = 230
    multi = inSpeed/maxSpeed
    x = screen_x*multi
    return x
def rpm2Y(inRPM) :
    if (inRPM<0) :
        inRPM = 0
    global screen_y
    maxRPM = dataDict["EngineMaxRpm"]["value"] +1
    multi = inRPM/maxRPM
    y = screen_y*multi
    y = screen_y - y
    #print(inAxx, y)
    return y
def hp2Y(inAxx) :
    if (inAxx<0) :
        inAxx = 0
    global screen_y
    screen = screen_y/2
    maxAxx = 1300000
    multi = inAxx/maxAxx
    y = screen*multi
    y = screen - y
    #print(inAxx, y)
    return y
def nm2Y(inAxx) :
    if (inAxx<0) :
        inAxx = 0
    global screen_y
    screen = screen_y/2
    maxAxx = 1300
    multi = inAxx/maxAxx
    y = screen*multi
    y = screen - y
    #print(inAxx, y)
    return y
def axx2Y(inAxx) :
    if (inAxx<0) :
        inAxx = 0
    global screen_y
    maxAxx = 10
    multi = inAxx/maxAxx
    y = screen_y*multi
    y = screen_y - y
    #print(inAxx, y)
    return y
def axx2Y2(inAxx) :
    if (inAxx<0) :
        inAxx = 0
    global screen_y
    maxAxx = 0.01
    multi = inAxx/maxAxx
    y = screen_y*multi
    #print(inAxx, y)
    y = screen_y*2 - y
    return y
lastTime = 0
lastSpeed = 0
def calcAxx():
    global lastTime
    global lastSpeed
    deltaTime = dataDict["TimestampMS"]["value"] - lastTime
    deltaSpeed = dataDict["Speed"]["value"] - lastSpeed
    axxout = 0
    if (deltaTime != 0) :
        axxout = deltaSpeed / deltaTime

    lastTime = dataDict["TimestampMS"]["value"]
    lastSpeed = dataDict["Speed"]["value"]
    return  axxout

def getGearColor(inGear):
    if (inGear == 1):
        return (66, 133, 244)
    if (inGear == 2):
        return (219, 68, 55)
    if (inGear == 3):
        return (244, 180, 0)
    if (inGear == 4):
        return (15, 157, 88)
    if (inGear == 5):
        return (255, 109, 0)
    if (inGear == 6):
        return (70, 189, 198)
    if (inGear == 7):
        return (171, 48, 196)
    if (inGear == 8):
        return (255, 100, 0)
    return (0,0,0)

running = True
clearTimer = 0
while running:
    message, address = s.recvfrom(1024)

    for key,item in dataDict.items():
        (value,) = struct.unpack_from(item["type"],message, offset=item["offset"])
        item["value"] = value

    #test = struct.unpack_from('i',message)
    #print(type(test) )
    #print(test)
    #(test,) = struct.unpack_from('f',message, offset=4*4)
    #print(type(test) )Boost
    for key,item in dataDict.items():
        #print(key, item["value"] )
        continue
        #print("%s;%.0f" % (key, item["value"]) )
    #print("%s;%.0f" % ("Boost", dataDict["Boost"]["value"]) ,end='', flush=True)
    #print("%s;%.0f" % ("TireTempFrontLeft", dataDict["TireTempFrontLeft"]["value"]) ,end='\n', flush=True)
    #print(dataDict["CurrentEngineRpm"]["value"], dataDict["LapNumber"]["value"] )
    arduinoOut = str(int((dataDict["Boost"]["value"]+11)*10)).encode()
    arduinoOut = arduinoOut + b"\n"
    #arduino.write(arduinoOut)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_c]:
        print("c is pressed")
        screen.fill((0, 0, 0)) # Clear screen when pressing key

    #screen.fill((0, 0, 0, 1))
    clearTimer+=1
    if (clearTimer>100):
        screen.blit(su, (0,0))
        clearTimer = 0
    color = (255, 100, 0)
    x1 = int(speed2X(dataDict["Speed"]["value"]*3.6))
    y1 = int(axx2Y(dataDict["AccelerationZ"]["value"]))
    pygame.draw.rect(screen, getGearColor(dataDict["Gear"]["value"]), pygame.Rect(x1, y1, 2, 2))
    y2 = int(rpm2Y(dataDict["CurrentEngineRpm"]["value"]))
    pygame.draw.rect(screen, (255,255,255), pygame.Rect(x1, y2, 1, 1))
    y3 = int(hp2Y(dataDict["Power"]["value"]))
    pygame.draw.rect(screen, (255,100,100), pygame.Rect(x1, y3, 1, 1))
    y3 = int(nm2Y(dataDict["Torque"]["value"]))
    pygame.draw.rect(screen, (100,255,100), pygame.Rect(x1, y3, 1, 1))
    print(dataDict["Torque"]["value"], dataDict["Power"]["value"])
    #y1 = int(axx2Y2(calcAxx()))
    #pygame.draw.rect(screen, getGearColor(dataDict["Gear"]["value"]), pygame.Rect(x1, y1, 2, 2))

    #GAME_FONT.render_to(screen, (40, 350), str(dataDict["Fuel"]["value"]), (128, 128, 128))

    pygame.display.flip()
