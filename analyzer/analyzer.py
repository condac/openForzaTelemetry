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
import json
import os
import traceback
#from pathlib import Path
#from functools import partial
netLog.speedLog("import klart sys")
import pyqtgraph as pg
netLog.speedLog("import klart pyqtgraph")
#Egna saker
import graphWidget

netLog.speedLog("import klart eget")
netLog.speedLog("import klart nl")
#netLog.speedLog("started")

SRC_PATH = os.path.dirname(os.path.abspath(__file__))

def readCSV(filename):
    netLog.speedLog("readCSV")
    list = {}
    count = 0
    try:
        file1 = open(filename, 'r')
        line1 = file1.readline()
        line1 = line1.replace("\"", "")
        headers = line1.split(";")

        for h in headers:
            list[h] = []

        print(headers)
        #print(list)
        while True:
            count += 1
            # Get next line from file
            line = file1.readline()
            line.replace("\n", "")
            # if line is empty
            # end of file is reached
            if not line:
                break
            #print("Line{}: {}".format(count, line.strip()))
            data = line.split(";")
            i = 0
            for d in data:
                try:
                    list[headers[i]].append(float(d) )
                except ValueError:
                    list[headers[i]].append(float(0) )
                i=i+1
        file1.close()
        print("close")
    except Exception as err:
        print(err)
        print(count)
        exception_type = type(err).__name__
        print(exception_type)
        print(traceback.format_exc())
    netLog.speedLog("readCSV klart")

    return list, headers

class Trend(QMainWindow):
    def __init__(self):
        super(Trend,self).__init__()

        self.initUI()

    def initUI(self):

        self.ui = uic.loadUi(SRC_PATH+os.sep+'analyzer.ui', self)
        try:
            f = open(SRC_PATH + os.sep + ".." + os.sep + "VERSION", "r")
            ver = f.read()
            print(ver)
            versionstring = ver.replace("\n", "")
        except Exception as err:
            print(err)
            versionstring = os.environ.get("GIT_VERSION", ".v")

        #versionstring = os.environ.get("GIT_VERSION", "v0.0.0")
        self.setWindowTitle("OFT Analyzer "+versionstring)
        self.ui.statusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(102,204,255,255);color:black;font-weight:bold;}");
        self.ui.statusbar.hide()

        self.data, self.dataHeaders = readCSV("output.csv")
        #print(self.data)
        self.ui.comboBoxDataX.addItems(self.dataHeaders)
        self.ui.comboBoxDataY.addItems(self.dataHeaders)
        #LapNumber
        laps = []
        lapStart = []
        for i in range(len(self.data["LapNumber"])):
            if str(int(self.data["LapNumber"][i])) not in laps:
                laps.append(str(int(self.data["LapNumber"][i])))
                lapStart.append(self.data["DistanceTraveled"][i])
        for i in range(len(self.data["DistanceTraveled"])):
            self.data["DistanceTraveled"][i] = self.data["DistanceTraveled"][i] - lapStart[int(self.data["LapNumber"][i])]
        self.ui.comboBoxLaps.addItems(laps)
        self.laps = laps
        index = self.ui.comboBoxDataX.findText("DistanceTraveled", Qt.MatchFixedString)
        if index >= 0:
             self.ui.comboBoxDataX.setCurrentIndex(index)
        self.plot = graphWidget.Graph()

        self.ui.verticalLayout.addWidget(self.plot)

        self.ui.buttonAdd.clicked.connect(self.onButtonAdd)

        row = 3
        self.checkBoxes = []
        for heads in self.dataHeaders:
            checkbox = QCheckBox(heads)
            self.ui.gridLayout_4.addWidget(checkbox, row, 0)
            self.checkBoxes.append(checkbox)
            row+=1
            #break


    def onButtonAdd(self):
        self.plot.clearAll()
        row = 0
        col = 0
        for box in self.checkBoxes:
            if box.isChecked():
                row+=1

                print("add ", box.text())
                for l in self.laps:
                    xd = []
                    yd = []
                    for i in range(len(self.data[box.text()])):
                        if int(self.data["LapNumber"][i]) == int(l):
                            xd.append(self.data[self.ui.comboBoxDataX.currentText()][i])
                            yd.append(self.data[box.text()][i])
                    xdata = xd
                    ydata = yd
                    #print(xdata)
                    #print(self.dataHeaders)
                    self.plot.addNew(name = box.text()+str(l), row=row, col=col, xdata=xdata, ydata=ydata, title=box.text())

        var = self.ui.lineEditVar.text()
        # row = self.ui.spinBoxRow.value()
        # col = self.ui.spinBoxCol.value()
        #print("add ", var)
        xdata = self.data[self.ui.comboBoxDataX.currentText()]
        ydata = self.data[self.ui.comboBoxDataY.currentText()]
        #print(xdata)
        #print(self.dataHeaders)
        #self.plot.addNew(name = self.ui.comboBoxDataY.currentText(), row=row, col=col, xdata=xdata, ydata=ydata)
        #print("add2 ", var)
        xdata = self.data["PositionX"]
        ydata = self.data["PositionY"]
        #print(xdata)
        #print(self.dataHeaders)
        for l in self.laps:
            xd = []
            yd = []
            for i in range(len(self.data[box.text()])):
                if int(self.data["LapNumber"][i]) == int(l):
                    xd.append(self.data["PositionX"][i])
                    yd.append(self.data["PositionY"][i])
            xdata = xd
            ydata = yd
            #print(xdata)
            #print(self.dataHeaders)
            self.plot.addNew(name = "Lap"+str(l), row=row+1, col=col, xdata=xdata, ydata=ydata, lock=False)

        #self.plot.addNew(name = "karta", row=row+1, col=col, xdata=xdata, ydata=ydata, lock=False)



if __name__ == "__main__":
    netLog.speedLog("started main")
    try:
        app = QApplication(sys.argv)

        win = Trend()
        win.show()
        sys.exit(app.exec_())
    except Exception as err:
        exception_type = type(err).__name__
        print(exception_type)
        #nl.netLog(f"exception {exception_type}")
        #nl.netLog(f"stacktrace {traceback.format_exc()}")
        print(traceback.format_exc())
        os._exit(1)
