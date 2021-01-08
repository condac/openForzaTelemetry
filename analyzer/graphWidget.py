#!/usr/bin/python3
from PyQt5 import QtWidgets, uic

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import  *
import sys
import socket
import json
import os
import traceback
from pathlib import Path
from functools import partial
import time
import random
import pyqtgraph as pg
from collections import deque
from pyqtgraph.Qt import QtGui, QtCore

#Egna saker
import sys
sys.path.append('../common')
import netLog

#netLog.speedLog("started")

SRC_PATH = os.path.dirname(os.path.abspath(__file__))

COLORS = [
            (255,0,0),
            (0,255,0),
            (55,55,255),
            (255,255,0),
            (0,255,255),
            (255,0,255),
            (128,0,0),
            (0,128,0),
            (55,55,128),
]

#pg.setConfigOption('background', 'w')
#pg.setConfigOption('foreground', 'k')
class PlotLine():
    def __init__(self, parent, place=0, name ="noname", xdata=[], ydata=[]):
        self.name =name


        while (parent.colorRotation >= len(COLORS)):
            parent.colorRotation = parent.colorRotation - len(COLORS)
        #print("color", parent.colorRotation,len(COLORS) )
        color = COLORS[parent.colorRotation]
        parent.colorRotation += 1
        #color = (255,0,0)

        self.curve = parent.p.plot(pen=color, name=name)
        self.dat = ydata
        self.xdat = xdata
        #print(ydata)
        self.maxLen = 1200*10 #1200 1 minut, 72000 en timme 1728000 24h

        #print(1, self.curve)
        self.curve.setData(x=self.xdat, y=self.dat)
        ## Set up an animated arrow and text that track the curve
        #print(2)
        self.curvePoint = pg.CurvePoint(self.curve)

        #print(3)

        parent.p.addItem(self.curvePoint)

        self.text = pg.TextItem("test", anchor=(0.5, -1.0))
        self.text.setParentItem(self.curvePoint)

        self.arrow = pg.ArrowItem(angle=90)
        self.arrow.setParentItem(self.curvePoint)
        #print(4)

class Plot():
    def __init__(self, parent, row=0, col=0, title="noname", lock=True):
        self.parent = parent
        self.colorRotation = row+col
        self.lineList = []
        self.p = self.parent.addPlot(row=row, col=col)
        self.legend = self.p.addLegend(offset=(10,10))
        self.legend.setBrush(self.parent.themeBack)
        self.legend.setLabelTextColor(self.parent.themeFore)
        #self.label = pg.LabelItem(justify='right')
        #p.addItem(self.label)
        if (parent.firstPlot):
            if lock:
                self.p.setXLink(parent.firstPlot.p)
        #p.addItem(self.curvePoint)
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        #self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.p.addItem(self.vLine, ignoreBounds=True)
        #p.addItem(self.hLine, ignoreBounds=True)
        self.proxy = pg.SignalProxy(self.p.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

    def addNewLine(self, place=0, name ="noname", xdata=[], ydata=[]):

        plot = PlotLine(self, place=place, name=name, xdata=xdata, ydata=ydata)

        self.lineList.append(plot)
        self.parent.varList.append(name)

    def mouseMoved(self, evt):
        return
        pos = evt[0]  ## using signal proxy turns original arguments into a tuple
        vb = self.p.vb
        if self.p.sceneBoundingRect().contains(pos):
            mousePoint = vb.mapSceneToView(pos)
            index = float(int(mousePoint.x()*20))/20
            self.vLine.setPos(mousePoint.x())
            title = ""
            i = 0
            for line in self.lineList:
                a, b = self.p.legend.items[i]
                i+=1
                try:
                    index2 = line.xdat.index(index)
                except ValueError as ex:
                    index2 = 0

                if index2 > 0 and index2 < len(line.xdat)-2 and index2 < len(line.dat)-2:
                    try:
                        line.curvePoint.setIndex(index2)
                    except:
                        ba=0
                    line.text.setText('[%0.1f]' % (line.dat[index2]))
                    title = title + f"{line.name}={line.dat[index2]} "
                    b.setText(f"{line.name}={line.dat[index2]}")

    def updateValues(self, resList):
        return
        for plot in self.lineList:
            if len(plot.dat) > plot.maxLen:
                plot.dat.popleft() #remove oldest
                plot.xdat.popleft()

            plot.dat.append(random.randint(0,100))
            plot.xdat.append(time.time())
            #self.data1 = plot.dat
            # import datetime
            # d = 1
            # h = 2
            # m = 3
            # s = 4
            # us = resList["clock(4)"] *50*1000
            # if (h<0):
            #     h = h + 128 +128
            # while (h>23):
            #     h = h - 24
            #     d= d+1
            # try:
            #
            #     timestamp = datetime.datetime(2000, 1, d, h, m, s, us ) + datetime.timedelta(hours=1)
            # except:
            #     print("ERROR tidsfel",d,h,m,s,us)
            # plot.xdat.append(timestamp.timestamp())
            #plot.curve.setData(x=plot.xdat, y=plot.dat)
    def redraw(self):

        for plot in self.lineList:
            plot.curve.setData(x=plot.xdat, y=plot.dat)



class Graph(pg.GraphicsLayoutWidget ):
    def __init__(self):
        super(Graph,self).__init__()
        netLog.speedLog("Graph init")
        self.axisItems = {'bottom': pg.DateAxisItem()}
        self.plotList = {}
        self.placeList = []
        self.colorRotation = 0
        self.varList = []
        self.varList.append("status")
        self.varList.append("clock(1)")
        self.varList.append("clock(2)")
        self.varList.append("clock(3)")
        self.varList.append("clock(4)")
        self.themeBack = "k"
        self.themeFore = "w"
        self.firstPlot = None
        #dafo211kd411da1

        ip = os.environ.get('ICE_SERVER_IP', "localhost")
        port = os.environ.get('ICE_SERVER_PORT', 1431)
        #self.jsocket = jsonsocket.JSocket(ip, port)

        #self.proxy = pg.SignalProxy(p1.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)

        #self.win = pg.GraphicsWindow()

    def setTheme(self, input):
        if (input == "light"):
            self.setBackground("w")
            self.themeBack = "w"
            self.themeFore = "k"
            for plot in self.plotList:
                self.plotList[plot].legend.setBrush(self.themeBack)
                self.plotList[plot].legend.setLabelTextColor(self.themeFore)
            #self.setForeground("k")
        else:
            self.setBackground("k")
            self.themeBack = "k"
            self.themeFore = "w"
            for plot in self.plotList:
                self.plotList[plot].legend.setBrush(self.themeBack)
                self.plotList[plot].legend.setLabelTextColor(self.themeFore)
            #self.setForeground("w")

    def addNew(self, row=0, col=0, name="noname", xdata=[], ydata=[], title="noname", lock=True):
        #self.setConfigOption('background', 'k')
        #self.setBackground("k")
        #self.setConfigOption('foreground', 'w')
        id = str(row)+","+str(col)
        if (id not in self.plotList):
            plot = Plot(self, row=row, col=col, title=title, lock=lock)
            if (not self.firstPlot):
                self.firstPlot = plot
            self.plotList[id] = plot
        self.plotList[id].addNewLine(place=row+col, name=name, xdata=xdata, ydata=ydata)

    def clearAll(self):
        print("clearAll")
        self.plotList = {}
        self.placeList = []
        self.colorRotation = 0
        self.varList = []
        self.varList.append("status")
        self.varList.append("clock(1)")
        self.varList.append("clock(2)")
        self.varList.append("clock(3)")
        self.varList.append("clock(4)")
        self.firstPlot = None
        self.clear()

    def updateValues(self):
        cmd = {}
        cmd["cmd"] = "getValueS"
        cmd["varList"] = self.varList
        #res = self.jsocket.sendCommandGetResponse(cmd)


        for plot in self.plotList:
            self.plotList[plot].updateValues(1)
    def redraw(self):
        for plot in self.plotList:
            self.plotList[plot].redraw()
