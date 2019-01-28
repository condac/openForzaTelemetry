import socket
import struct
import sys
import serial

localIP = "192.168.0.111"
localPort = 20001
bufferSize = 1024


#print(array)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('192.168.0.118', localPort))

clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    nr = 0
    message, address = s.recvfrom(1024)

    clientSock.sendto(message, ("192.168.0.102", 20002))
    clientSock.sendto(message, ("192.168.0.111", 20002))
    nr = nr+1
    print(nr)
