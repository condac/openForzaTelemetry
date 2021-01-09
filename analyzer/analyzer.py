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
import mapWidget

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

        #self.data, self.dataHeaders = readCSV("output.csv")
        self.car1, self.dataHeaders = readCSV("car1.csv")
        self.car2, self.dataHeaders = readCSV("car2.csv")
        #print(self.data)
        self.ui.comboBoxDataX.addItems(self.dataHeaders)
        self.ui.comboBoxDataY.addItems(self.dataHeaders)
        #LapNumber Car 1
        laps1 = []
        lapStart1 = []
        lapStartTime1 = []
        for i in range(200):
            lapStart1.append(0.0)
            lapStartTime1.append(0.0)
        for i in range(len(self.car1["LapNumber"])):
            if str(int(self.car1["LapNumber"][i])) not in laps1:
                laps1.append(str(int(self.car1["LapNumber"][i])))
                #lapStart1.append(self.car1["DistanceTraveled"][i])
                lapStart1[int(self.car1["LapNumber"][i])] = self.car1["DistanceTraveled"][i]
                #lapStartTime1.append(self.car1["TimestampMS"][i])
                lapStartTime1[int(self.car1["LapNumber"][i])] = self.car1["TimestampMS"][i]
        for i in range(len(self.car1["DistanceTraveled"])):
            if i >= len(self.car1["LapNumber"]):
                print(i , len(self.car1["LapNumber"]))
            else:
                self.car1["DistanceTraveled"][i] = self.car1["DistanceTraveled"][i] - lapStart1[int(self.car1["LapNumber"][i])]
                self.car1["TimestampMS"][i] = self.car1["TimestampMS"][i] - lapStartTime1[int(self.car1["LapNumber"][i])]
                if (self.car1["Steer"][i] > 127.0):
                    self.car1["Steer"][i] = self.car1["Steer"][i]-255
        self.ui.comboBoxLaps1.addItems(laps1)
        self.laps1 = laps1
        #LapNumber Car 2
        laps2 = []
        lapStart2 = []
        lapStartTime2 = []
        for i in range(200):
            lapStart2.append(0.0)
            lapStartTime2.append(0.0)
        for i in range(len(self.car2["LapNumber"])):
            if str(int(self.car2["LapNumber"][i])) not in laps2:
                laps2.append(str(int(self.car2["LapNumber"][i])))
                #lapStart2.append(self.car2["DistanceTraveled"][i]) # Find where lap start
                #lapStartTime2.append(self.car2["TimestampMS"][i])
                lapStart2[int(self.car2["LapNumber"][i])] = self.car2["DistanceTraveled"][i]
                lapStartTime2[int(self.car2["LapNumber"][i])] = self.car2["TimestampMS"][i]
        for i in range(len(self.car2["DistanceTraveled"])):
            self.car2["DistanceTraveled"][i] = self.car2["DistanceTraveled"][i] - lapStart2[int(self.car2["LapNumber"][i])] # Subtract start distance from all points
            self.car2["TimestampMS"][i] = self.car2["TimestampMS"][i] - lapStartTime2[int(self.car2["LapNumber"][i])]
            if (self.car2["Steer"][i] > 127.0):
                self.car2["Steer"][i] = self.car2["Steer"][i]-255
        self.ui.comboBoxLaps2.addItems(laps2)
        self.laps2 = laps2
        index = self.ui.comboBoxDataX.findText("DistanceTraveled", Qt.MatchFixedString)
        if index >= 0:
             self.ui.comboBoxDataX.setCurrentIndex(index)
        self.map = mapWidget.Graph()
        self.plot = graphWidget.Graph(self.map)
        splitter = QSplitter()
        scroll = QScrollArea()
        boxwidget = QWidget()
        boxgrid = QGridLayout()
        boxwidget.setLayout(boxgrid)


        row = 3
        self.checkBoxes = []
        for heads in self.dataHeaders:
            checkbox = QCheckBox(heads)
            boxgrid.addWidget(checkbox, row, 0)
            self.checkBoxes.append(checkbox)
            row+=1
            #break
        boxgrid.sizeHint()
        boxwidget.sizeHint()
        scroll.setWidget(boxwidget)
        splitter.addWidget(scroll)
        splitter.addWidget(self.plot)
        splitter.addWidget(self.map)
        self.ui.gridLayout.addWidget(splitter, 2, 0, 1, 15)


        self.ui.buttonAdd.clicked.connect(self.onButtonAdd)


    def onButtonAdd(self):
        self.plot.clearAll()
        self.map.clearAll()
        row = 0
        col = 0
        for box in self.checkBoxes:
            if box.isChecked():
                row+=1

                print("add car1", box.text())
                for l in self.laps1:
                    if int(l) == int(self.ui.comboBoxLaps1.currentText()):
                        xd = []
                        yd = []
                        self.posx1 = []
                        self.posy1 = []
                        posdata = []
                        for i in range(len(self.car1[box.text()])):
                            if int(self.car1["LapNumber"][i]) == int(l):
                                xd.append(self.car1[self.ui.comboBoxDataX.currentText()][i])
                                yd.append(self.car1[box.text()][i])
                                pd = (self.car1["PositionX"][i], self.car1["PositionZ"][i])
                                posdata.append(pd)
                                #self.posx2.append(self.car2["PositionX"][i])
                                #self.posy2.append(self.car2["PositionY"][i])
                        xdata = xd
                        ydata = yd
                        #print(xdata)
                        #print(self.dataHeaders)
                        self.plot.addNew(name = box.text()+str(l), row=row, col=col, xdata=xdata, ydata=ydata, title=box.text(), color=1, posdata = posdata)
                print("add car2", box.text())
                for l in self.laps2:
                    if int(l) == int(self.ui.comboBoxLaps2.currentText()):
                        xd = []
                        yd = []
                        self.posx2 = []
                        self.posy2 = []
                        posdata = []
                        for i in range(len(self.car2[box.text()])):
                            if int(self.car2["LapNumber"][i]) == int(l):
                                xd.append(self.car2[self.ui.comboBoxDataX.currentText()][i])
                                yd.append(self.car2[box.text()][i])
                                pd = (self.car2["PositionX"][i], self.car2["PositionZ"][i])
                                posdata.append(pd)
                        xdata = xd
                        ydata = yd
                        #print(xdata)
                        #print(self.dataHeaders)
                        self.plot.addNew(name = box.text()+str(l), row=row, col=col, xdata=xdata, ydata=ydata, title=box.text(), color=2, posdata = posdata)

        var = self.ui.lineEditVar.text()
        # row = self.ui.spinBoxRow.value()
        # col = self.ui.spinBoxCol.value()
        #print("add ", var)
        # xdata = self.car1[self.ui.comboBoxDataX.currentText()]
        # ydata = self.car1[self.ui.comboBoxDataY.currentText()]
        #print(xdata)
        #print(self.dataHeaders)
        #self.plot.addNew(name = self.ui.comboBoxDataY.currentText(), row=row, col=col, xdata=xdata, ydata=ydata)
        #print("add2 ", var)
        xdata = self.car1["PositionX"]
        ydata = self.car1["PositionZ"]
        #print(xdata)
        #print(self.dataHeaders)
        for l in self.laps1:
            if int(l) == int(self.ui.comboBoxLaps1.currentText()):
                xd = []
                yd = []
                for i in range(len(self.car1[box.text()])):
                    if int(self.car1["LapNumber"][i]) == int(l):
                        xd.append(self.car1["PositionX"][i])
                        yd.append(self.car1["PositionZ"][i])
                xdata = xd
                ydata = yd
                #print(xdata)
                #print(self.dataHeaders)
                self.map.addNew(name = "Car1 Lap"+str(l), row=row+1, col=col, xdata=xdata, ydata=ydata, lock=False, color=1)

        xdata = self.car2["PositionX"]
        ydata = self.car2["PositionZ"]
        for l in self.laps2:
            if int(l) == int(self.ui.comboBoxLaps2.currentText()):
                xd = []
                yd = []
                for i in range(len(self.car1[box.text()])):
                    if int(self.car1["LapNumber"][i]) == int(l):
                        xd.append(self.car1["PositionX"][i])
                        yd.append(self.car1["PositionZ"][i])
                xdata = xd
                ydata = yd

                self.map.addNew(name = "Car2 Lap"+str(l), row=row+1, col=col, xdata=xdata, ydata=ydata, lock=False, color=2)

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
