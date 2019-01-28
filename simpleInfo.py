import socket
import struct
import sys
import serial

import pygame
import pygame.freetype

# Pygame stuff
pygame.init()
screen = pygame.display.set_mode((800, 450))
GAME_FONT = pygame.freetype.Font("LED.ttf", 24)

clock = pygame.time.Clock()

localIP = ""
localPort = 20002
bufferSize = 1024

dataDict = {}
#arduino = serial.Serial('/dev/ttyACM0', 9600)

with open("dataformat.csv", "r") as dataformatfile:
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
        print(type,name)
        newdata["type"] = type
        newdata["offset"] = newoffset
        newdata["length"] = newlength
        #newdata["value"] = 0
        dataDict[name] = newdata
        print(dataDict)
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

running = True
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


    screen.fill((0, 0, 0)) # Clear screen every frame

    color = (255, 100, 0)
    x1 = int(dataDict["CurrentEngineRpm"]["value"])/10
    pygame.draw.rect(screen, color, pygame.Rect(0, 60, x1, 60))
    GAME_FONT.render_to(screen, (40, 350), str(dataDict["Fuel"]["value"]), (128, 128, 128))
    if calcShiftLight():
        color = (0, 0, 200)
        pygame.draw.rect(screen, color, pygame.Rect(0, 0, 1000, 60))

    pygame.display.flip()
