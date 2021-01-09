#!/usr/bin/python3
import sys
import os
SRC_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SRC_PATH+os.sep+'../common')
import netLog
from PyQt5 import QtWidgets, uic

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import  *
netLog.speedLog("import klart qt")
import sys
import socket
import os
import traceback
from datetime import datetime
import threading
import time
import struct
#from pathlib import Path
#from functools import partial
netLog.speedLog("import klart sys")
#Egna saker

netLog.speedLog("import klart eget")
#netLog.speedLog("started")

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
class Recorder(QMainWindow):
    def __init__(self):
        super(Recorder,self).__init__()

        self.started = False
        self.wait = False
        self.packets = 0
        self.initUI()



        redrawMs = 500
        self.timer1 = QTimer()
        self.timer1.timeout.connect(self.redraw)
        self.timer1.start(redrawMs)
        #

    def initUI(self):

        self.ui = uic.loadUi(SRC_PATH+os.sep+'gui.ui', self)
        try:
            f = open(SRC_PATH + os.sep + ".." + os.sep + "VERSION", "r")
            ver = f.read()
            print(ver)
            versionstring = ver.replace("\n", "")
        except Exception as err:
            print(err)
            versionstring = os.environ.get("GIT_VERSION", ".v")

        #versionstring = os.environ.get("GIT_VERSION", "v0.0.0")
        self.setWindowTitle("OFT Recorder "+versionstring)
        self.ui.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(102,204,255,255);color:black;font-weight:bold;}");
        self.ui.statusbar.hide()


        self.ui.startButton.clicked.connect(self.onStartButton)
        self.ui.stopButton.clicked.connect(self.onStopButton)



    def closeEvent(self, event):
        self.udpThread.doShutdown()
        event.accept() # let the window close

    def redraw(self):


        if self.started:
            status = "Recording: "
            if (self.packets != self.udpThread.counter):
                self.ui.labelStatus.setStyleSheet("background-color: lightgreen")
            else:
                self.ui.labelStatus.setStyleSheet("background-color: red")
            self.packets = self.udpThread.counter
        else:
            status = "Stopped"
            self.ui.labelStatus.setStyleSheet("background-color: lightblue")
        self.ui.labelStatus.setText(status+str(self.packets))

    def onStartButton(self):
        if self.started:
            self.wait = True
            self.udpThread.stopRecording()
        while(self.wait):
            continue
        self.started = True
        self.udpThread = UdpThread( int(self.ui.portIn.text()), self )
        self.udpThread.start()
        return
    def onStopButton(self):
        self.udpThread.stopRecording()
        self.started = False
        return


exitFlag = 0

class UdpThread(threading.Thread):



    localIP = ""

    bufferSize = 1024
    def __init__(self, port, parent):
        threading.Thread.__init__(self)
        self.parent = parent
        self.localPort = port
        self.counter = -1
        self.running = True
        self.update = True
        self.outputList = []

    def run(self):
        netLog.speedLog("started udpThread")

        #print(array)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1.0)
        s.bind(('', self.localPort))

        clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.counter = 0



        now = datetime.now()

        current_time = now.strftime("%Y-%m-%d_%H%M%S")

        filename = "output"+current_time+".csv"
        print("creating file :", filename)
        outfile = open(filename,"w")
        for key,item in dataDict.items():
            outfile.write("\""+key+"\""+";")
        outfile.write("\n")

        while self.running:
            try:
                message, address = s.recvfrom(1024)
            except socket.timeout:
                print("no data")
                continue
            for key,item in dataDict.items():
                (value,) = struct.unpack_from(item["type"],message, offset=item["offset"])
                item["value"] = value

            for key,item in dataDict.items():
                #print(key, item["value"] )
                outfile.write(str(item["value"])+";")
                continue
            outfile.write("\n")
            self.counter += 1
        outfile.close()
        clientSock.close()
        s.close()
        self.parent.wait = False

    def startRecording(self):
        return
    def stopRecording(self):
        self.running = False
        return
    def updateValues(self, portIn, ulist):
        self.localPort = int(portIn)
        self.outputList = ulist
        self.update = True

    def doShutdown(self):
        self.running = False


if __name__ == "__main__":
    netLog.speedLog("started main")
    try:
        app = QApplication(sys.argv)

        win = Recorder()
        win.show()
        sys.exit(app.exec_())
    except Exception as err:
        exception_type = type(err).__name__
        print(exception_type)
        #nl.netLog(f"exception {exception_type}")
        #nl.netLog(f"stacktrace {traceback.format_exc()}")
        print(traceback.format_exc())
        os._exit(1)
