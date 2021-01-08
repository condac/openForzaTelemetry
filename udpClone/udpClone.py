#!/usr/bin/python3
import sys
sys.path.append('../common')
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
#from pathlib import Path
#from functools import partial
netLog.speedLog("import klart sys")
#Egna saker

netLog.speedLog("import klart eget")
#netLog.speedLog("started")

SRC_PATH = os.path.dirname(os.path.abspath(__file__))

NR_OUTPUTS = 5

class udpClone(QMainWindow):
    def __init__(self):
        super(udpClone,self).__init__()

        self.checkboxList = []
        self.ipList = []
        self.portList = []
        self.packets = 0
        self.initUI()

        self.udpThread = UdpThread()

        redrawMs = 500
        self.timer1 = QTimer()
        self.timer1.timeout.connect(self.redraw)
        self.timer1.start(redrawMs)
        self.udpThread.start()

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
        self.setWindowTitle("OFT UDP Clone "+versionstring)
        self.ui.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(102,204,255,255);color:black;font-weight:bold;}");
        self.ui.statusbar.hide()


        self.ui.pushButton.clicked.connect(self.onUpdateButton)

        row = 3
        for i in range(NR_OUTPUTS):
            checkbox = QCheckBox("Active")
            ip = QLineEdit("localhost")
            port = QLineEdit(str(20002+i))

            self.ui.gridLayout.addWidget(checkbox, row, 0)
            self.ui.gridLayout.addWidget(ip, row, 1)

            self.ui.gridLayout.addWidget(port, row, 2)

            self.checkboxList.append(checkbox)
            self.ipList.append(ip)
            self.portList.append(port)
            row+=1

    def closeEvent(self, event):
        self.udpThread.running = False
        event.accept() # let the window close

    def redraw(self):

        if (self.packets != self.udpThread.counter):
            self.ui.labelPackets.setStyleSheet("background-color: lightgreen")
        else:
            self.ui.labelPackets.setStyleSheet("background-color: red")
        self.packets = self.udpThread.counter
        self.ui.labelPackets.setText(""+str(self.packets))


    def onUpdateButton(self):
        portIn = self.ui.portIn.text()

        print("update ", portIn)
        ulist = []
        for i in range(NR_OUTPUTS):
            out = {}
            out["check"] = self.checkboxList[i].isChecked()
            out["ip"] = self.ipList[i].text()
            out["port"] = self.portList[i].text()
            ulist.append(out)
            print("update ", out)

        self.udpThread.updateValues(portIn, ulist)
import threading
import time

exitFlag = 0

class UdpThread(threading.Thread):
    import socket
    import struct
    import sys

    localIP = ""
    localPort = 20001
    bufferSize = 1024
    def __init__(self):
        threading.Thread.__init__(self)
        self.counter = 0
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
        self.counter = 110
        while self.running:
            if self.update:
                self.counter = 0
                self.update = False
                clientSock.close()
                s.close()
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.settimeout(1.0)
                s.bind(('', self.localPort))

                clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                message, address = s.recvfrom(1024)
                #print(data)
                self.counter = self.counter+1
                for out in self.outputList:
                    if (out["check"]):
                        clientSock.sendto(message, (out["ip"], int(out["port"])) )

            except socket.timeout:
                print('no data')
            #message, address = s.recvfrom(1024)

            #clientSock.sendto(message, ("192.168.0.102", 20002))
            #clientSock.sendto(message, ("192.168.0.111", 20002))
            #clientSock.sendto(message, ("192.168.0.111", 20003))
            #self.counter = self.counter+1
            #print(nr)
    def updateValues(self, portIn, ulist):
        self.localPort = int(portIn)
        self.outputList = ulist
        self.update = True



if __name__ == "__main__":
    netLog.speedLog("started main")
    try:
        app = QApplication(sys.argv)

        win = udpClone()
        win.show()
        sys.exit(app.exec_())
    except Exception as err:
        exception_type = type(err).__name__
        print(exception_type)
        #nl.netLog(f"exception {exception_type}")
        #nl.netLog(f"stacktrace {traceback.format_exc()}")
        print(traceback.format_exc())
        os._exit(1)
