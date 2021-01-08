import inspect
import socket
import json
import os
import datetime

os.system("")

NL_INFO = 1
NL_WARN = 2
NL_ERR = 3
NL_ERROR = 3
NL_DEBUG = 4
NL_POPUP = 5

def speedLog(intext):
    #if (os.path.sep == "\\"):
    #    escape = ""
    #else :
    #    escape = '\33'
    escape = '\33'
    CEND      = escape+'[0m'
    CGREEN2  = escape+'[92m'
    CYELLOW2 = escape+'[93m'
    if not hasattr(speedLog, "startTime"):
        speedLog.startTime = datetime.datetime.utcnow()
        speedLog.timer1 = datetime.datetime.utcnow()
    if not hasattr(speedLog, "quietflag"):
        quietflag = False
    currenttime = datetime.datetime.utcnow()
    time1 = currenttime - speedLog.startTime
    time2 = currenttime - speedLog.timer1
    funcName = inspect.currentframe().f_back.f_code.co_name
    if not quietflag and intext != "":
        out = f"{CGREEN2}  {time1.total_seconds()}s:{CEND} {funcName}() {intext} {CYELLOW2}{time2.total_seconds()}s{CEND}"
        print(out)
        #netLog.netLog(out)
    speedLog.timer1 = datetime.datetime.utcnow()

def progressBar(indata):

    dots  = 80
    progress = indata/progressBar.totalLines
    if (progress>1.0):
        progress = 1.0
    while(int(progress*dots)> progressBar.printedDots ):
        if not progressBar.quietflag:
            print(f"\33[3{progressBar.color}m.\33[0m", end="", flush=True)
        progressBar.printedDots += 1
def progressBarSetup(lines):

    progressBar.totalLines = lines
    progressBar.printedDots = 0
    progressBar.color += 1
    if (progressBar.color >= 8):
        progressBar.color = 1
def progressBarSetQuiet(quiet):
    progressBar.quietflag = quiet
progressBar.totalLines = 1
progressBar.printedDots = 0
progressBar.color = 0
progressBar.quietflag = False

def dummy():
    dummy.created = False
dummy.created = False
def LOG_INIT(appname, ip="127.0.0.1", port=10601, line=True):
    dummy.ip = ip
    dummy.port = port
    dummy.appname = appname
    dummy.line = line

    dummy.serverAddressPort = (dummy.ip, dummy.port)

    dummy.UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    dummy.created = True

def LOG_ERROR(text):
    funcName = inspect.currentframe().f_back.f_code.co_name
    if (not dummy.created):
        LOG_INIT(inspect.currentframe().f_back.f_code.co_filename)

    if (dummy.line):
        # this have big performance impact ##
        line = inspect.getframeinfo(inspect.stack()[1][0]).lineno
    else:
        line = -1
    netLog2(NL_ERROR, 10, text, func=funcName, line=line)

def LOG_INFO(text):
    funcName = inspect.currentframe().f_back.f_code.co_name
    if (not dummy.created):
        LOG_INIT(inspect.currentframe().f_back.f_code.co_filename)

    if (dummy.line):
        # this have big performance impact ##
        line = inspect.getframeinfo(inspect.stack()[1][0]).lineno
    else:
        line = -1
    netLog2(NL_INFO, 10, text, func=funcName, line=line)

def LOG_DEBUG(text):
    funcName = inspect.currentframe().f_back.f_code.co_name
    if (not dummy.created):
        LOG_INIT(inspect.currentframe().f_back.f_code.co_filename)

    if (dummy.line):
        # this have big performance impact ##
        line = inspect.getframeinfo(inspect.stack()[1][0]).lineno
    else:
        line = -1
    netLog2(NL_DEBUG, 10, text, func=funcName, line=line)

def netLog2(type, level, text,  func="", line=-1):
    outdata = {}
    if func=="":
        funcName = inspect.currentframe().f_back.f_code.co_name
    else:
        funcName = func
    if (not dummy.created):
        LOG_INIT(__file__)

    if line == -1:
        if (dummy.line):
            # this have big performance impact ##
            outdata["line"] = inspect.getframeinfo(inspect.stack()[1][0]).lineno
        else:
            outdata["line"] = -2
    else:
        outdata["line"] = line
    if (type == NL_ERROR):
        print(f'ERROR:{str(funcName)}({outdata["line"]}) {text}')
    outdata["func"] = str(funcName)
    outdata["type"] = type
    outdata["level"] = level
    outdata["text"] = str(text)
    outdata["appname"] = dummy.appname
    outdata["pid"] = os.getpid()

    data_json = json.dumps(outdata)
    bytesToSend = data_json.encode()

    dummy.UDPClientSocket.sendto(bytesToSend, dummy.serverAddressPort)

levelText = ["NONE", "INFO", "WARNING", "ERROR", "DEBUG", "POPUP"]
class NetLog():
    INFO = 1
    WARN = 2
    ERR = 3
    DEBUG = 4
    POPUP = 5

    def __init__(self,appname, ip="127.0.0.1", port=10601, line=True):
        self.ip = ip
        self.port = port
        self.appname = appname
        self.line = line

        self.serverAddressPort = (self.ip, self.port)

        self.UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    def netLog(self,text):
        funcName = inspect.currentframe().f_back.f_code.co_name
        if (self.line):
            # this have big performance impact ##
            line = inspect.getframeinfo(inspect.stack()[1][0]).lineno
        else:
            line = -1
        self.netLog2(self.DEBUG, 10, text, func=funcName, line=line)

    def netLog2(self, type, level, text,  func="", line=-1):
        outdata = {}
        if func=="":
            funcName = inspect.currentframe().f_back.f_code.co_name
        else:
            funcName = func
        if line == -1:
            if (self.line):
                # this have big performance impact ##
                outdata["line"] = inspect.getframeinfo(inspect.stack()[1][0]).lineno
            else:
                outdata["line"] = -2
        else:
            outdata["line"] = line

        outdata["func"] = str(funcName)
        outdata["type"] = type
        outdata["level"] = level
        outdata["text"] = str(text)
        outdata["appname"] = self.appname
        outdata["pid"] = os.getpid()

        data_json = json.dumps(outdata)
        bytesToSend = data_json.encode()

        self.UDPClientSocket.sendto(bytesToSend, self.serverAddressPort)
