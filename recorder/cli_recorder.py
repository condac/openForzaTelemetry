import socket
import struct
import sys
import os

localIP = ""
localPort = 20006
bufferSize = 1024

dataDict = {}
#arduino = serial.Serial('/dev/ttyACM0', 9600)
SRC_PATH = os.path.dirname(os.path.abspath(__file__))

with open(SRC_PATH+"/../common/dataformat.csv", "r") as dataformatfile:
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


running = True
clearTimer = 0

outfile = open("output.csv","w")
for key,item in dataDict.items():
    outfile.write("\""+key+"\""+";")
outfile.write("\n")

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
        outfile.write(str(item["value"])+";")

        continue
    outfile.write("\n")
        #print("%s;%.0f" % (key, item["value"]) )
    #print("%s;%.0f" % ("Boost", dataDict["Boost"]["value"]) ,end='', flush=True)
    #print("%s;%.0f" % ("TireTempFrontLeft", dataDict["TireTempFrontLeft"]["value"]) ,end='\n', flush=True)
    #print(dataDict["CurrentEngineRpm"]["value"], dataDict["LapNumber"]["value"] )
