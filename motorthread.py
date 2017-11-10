from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import *
from PyQt5.QtCore import QThread, pyqtSignal
import snap7

class MotorCheck(QThread):

    motorvaluechanged = pyqtSignal(int)

    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        # your logic here
        plc = snap7.client.Client()
        plc.connect('192.168.0.3', 0, 0)

        while True:
            connected = plc.get_connected()
            if connected == True:
                motorCntr = plc.db_read(44, 47, 4)
                self.sleep(0.1)# Motor failure counter
                motorCntrInt = int.from_bytes(motorCntr, byteorder='little', signed=False)
                self.motorvaluechanged.emit(motorCntrInt)
            elif connected == False:
                plc.connect('192.168.0.3', 0, 0)

