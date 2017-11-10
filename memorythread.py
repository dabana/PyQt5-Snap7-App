from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import *
from PyQt5.QtCore import QThread, pyqtSignal
import snap7
import sys

#This QThread object is used to check the values of
#the PLC VM memory spaces specific to pump (Err1 and Err2) and motor (Err3)
# errors and counters. It also keeps the connection alive and
#send out a connection error (Err4)


class MemoryCheck(QThread):

    #Create the PyQt signals
    motorvaluechanged = pyqtSignal(int)
    watercntrchanged = pyqtSignal(int)
    pumperror = pyqtSignal(int)
    ConnectionFail = pyqtSignal()

    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        #Establish client connection with the PLC

        try:
            plc = snap7.client.Client()
            plc.connect('192.168.0.3', 0, 0)
        except:
            self.ConnectionFail.emit()

        #Infinite loop running as a separate thread
        while True:
            sys.stdout.flush()
            try:
                # Read counters
                motorcntr = plc.db_read(44, 47, 4)# Motor failure counter
                watercntr = plc.db_read(40, 43, 4)# Water tank counter

                # Read error flags
                memErr1 = plc.db_read(9, 9, 1)  # Error 1 flag
                memErr2 = plc.db_read(10, 10, 1)  # Error 2 flag
            except:
                self.ConnectionFail.emit()
                break
            else:
                #Sleep 100 ms to avoid job pending errors from the Snap7 Library
                self.sleep(0.1)

                #Convert values to integers
                motorCntrInt = int.from_bytes(motorcntr, byteorder='little', signed=False)
                waterCntrInt = int.from_bytes(watercntr, byteorder='little', signed=False)
                errcode = memErr1[0] + 2 * memErr2[0]

                #Emit signals
                self.motorvaluechanged.emit(motorCntrInt)
                self.watercntrchanged.emit(waterCntrInt)
                self.pumperror.emit(errcode)





