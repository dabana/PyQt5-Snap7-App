#David Banville
#Version 9: Handle connection errors
#Created 6 octobre 2017
#


# always seem to need this
import sys
import time
import datetime

#import Snap7 library for PLC communication
import snap7


# This gets the Qt stuff
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import *
from PyQt5 import QtSql, QtGui, QtWidgets
from memorythread import MemoryCheck
# This is our window from QtCreator
import mainwindow_auto

###PLC communication

# Establish communication with the PLC
plc = snap7.client.Client()
plc.connect('192.168.0.3', 0, 0)
mem = plc.db_read(4, 4, 1)

# Read the initial value of the VM areas for network input
memL = plc.db_read(4, 4, 1)  # Left displacement at V4.0
memR = plc.db_read(5, 5, 1)  # Right displacement at V5.0
memLi = plc.db_read(6, 6, 1)  # Light 1 at V6.0, light 3 at V7.0 and light3 at V8.0
memRstErr1 = plc.db_read(11, 11, 1) # Error 1 reset
memRstErr2 = plc.db_read(12, 12, 1) # Error 2 reset
WtrRstCntr = plc.db_read(13, 13, 1) # Water counter reset
memRstErr3 = plc.db_read(14, 14, 1) # Motor failure counter reset
memStopWtr = plc.db_read(15, 15, 1) # Manual water stop network input

lightmemindex = [6, 7, 8]
errrstmemindex = [11, 12, 14]

memL[0] = 0
memR[0] = 0
memLi[0] = 0
memRstErr1[0] = 0
memRstErr2[0] = 0
memStopWtr[0] = 0

errflag = [0, 0, 0]
err3cntr = 0

localdbID = 1 #initialize the localdbID
model = QtSql.QSqlTableModel()

#Create the water consumption variables
WaterCons = 0 #Water consumption since last reboot or reset in gallons
WaterConsRate = 0 #Water consumption rate since last reboot or reset in gallons per days
VolumeIncrement = [3.6, 13.5, 3.6, 13.5] #Volume increment set in the flowmeter. Initialized in gallons, can be in 15.14 Liters
WaterConsUnitStrFr = ['Gallons', 'Litres', 'Gallons/jour', 'Litres/jour']
WaterConsUnitStrEn = ['Gallons', 'Liters', 'Gallons/day', 'Liters/day']
WaterConsUnitStr = [WaterConsUnitStrFr, WaterConsUnitStrEn]


VolumeIncrementIndex = 0
t0 = time.time() # Time since last reset of the counter or last reboot of the app in seconds
t0date = datetime.datetime.now() # Time since last reset of the counter or last reboot of the app in days

#Light status variables
LOn = [True, True, True]
# administrator password
adminpswd = 'pi'

### INTERNATIONALISATION
#Bilangual strings
LanguageIndex = 1

#Construction of the fixed strings data structure
frfixstrings = ['Fr',
                'Lorem ipsum Lorem ipsum',
                "Consommation d'eau",
                'Cuisine',
                'Salle de bain',
                'Plafonnier']
enfixstrings = ['En',
                'Lorem ipsum Lorem ipsum',
                'Water consumption',
                'Kitchen',
                'Washroom',
                'Roof light']
fixstrings = [frfixstrings, enfixstrings]

#Construction of the dynamic strings data structure
frdynstrings = ['Mot de passe',
                "Êtes-vous sur de vouloir réinitialiser le compteur d'eau?",
                'Depuis le ',
                'Erreur pompe (Err1)',
                'Erreur pompe (Err2)',
                'Erreur moteur (Err3)\n(Décompte = ',
                "L'application tente de se connecter ..."]
endynstrings = ['Password',
                'Are you sure you want to reset the water meter?',
                'Since ',
                'Pump error (Err1)',
                'Pump error (Err2)',
                'Motor error (Err3)\n(Count = ',
                'The application is trying to connect ...']
dynstrings = [frdynstrings, endynstrings]


# create class for our Raspberry Pi GUI
class MainWindow(QMainWindow, mainwindow_auto.Ui_MainWindow):

     ### Initialization of the GUI
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self) # gets defined in the UI file
        self.showFullScreen() # Puts the app fullscreen

        #Connect the PLC memory check thread and fetch signals from the thread
        self.memoryThread = MemoryCheck()
        self.memoryThread.motorvaluechanged.connect(self.motorvaluechanged)
        self.memoryThread.watercntrchanged.connect(self.IncWaterConsCntr)
        self.memoryThread.pumperror.connect(self.displaypumpError)
        self.memoryThread.ConnectionFail.connect(self.displayconnectionfail)


        self.lcdWaterCons.display(WaterCons)
        self.tabMain.setCurrentIndex(0) # selects the first tab
        self.switchlanguage() #Populate all strings

        #Read the water reset button state
        global memStopWtr, plc
        memStopWtr = plc.db_read(15, 15, 1)
        if memStopWtr[0] == 0:
            #change the button visual
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/images/block-faucet.png"))
            self.btnStopWater.setIcon(icon)

        elif memStopWtr[0] == 1:
            # change the button visual
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/images/block-faucet-red.png"))
            self.btnStopWater.setIcon(icon)

            #Write the action to the database
            self.writetodatabase(5, 0)

        #Turn off all the lights at bootup
        self.clickedLightButton(0)
        time.sleep(0.1)
        self.clickedLightButton(1)
        time.sleep(0.1)
        self.clickedLightButton(2)
        time.sleep(0.1)

        #Release all displacement buttons at bootup
        self.releasedLButton()
        time.sleep(0.1)
        self.releasedRButton()

        # Start the PLC memory check thread
        self.memoryThread.start()

        ### Hooks for buttons

        #Signals for pressing displacement buttons
        self.btnL.pressed.connect(lambda: self.pressedLButton())
        self.btnR.pressed.connect(lambda: self.pressedRButton())

        #Signals for releasing button
        self.btnL.released.connect(lambda: self.releasedLButton())
        self.btnR.released.connect(lambda: self.releasedRButton())

        #Signals for clicking light buttons
        self.btnL1.clicked.connect(lambda: self.clickedLightButton(0))
        self.btnL2.clicked.connect(lambda: self.clickedLightButton(1))
        self.btnL3.clicked.connect(lambda: self.clickedLightButton(2))

        #Signal for clicking quit button
        #self.btnQuit.clicked.connect(lambda: self.pressedQuitButton())

        #Signals for the clicking the error buttons
        self.btnErr1.clicked.connect(lambda: self.clickedErrButton(1))
        self.btnErr2.clicked.connect(lambda: self.clickedErrButton(2))
        self.btnErr3.clicked.connect(lambda: self.clickedErrButton(3))

        #Signal for clicking the Water counter reset button
        self.btnWtrCntrRst.clicked.connect(lambda: self.clickedWtrCntrRstButton())

        #Signal for clicking the stop water button
        self.btnStopWater.clicked.connect(lambda: self.clickedStopWaterbutton())

        #Signal for clicking the water unit button
        self.btnWtrCntrUnit.clicked.connect(lambda: self.clickecWtrCntrUnitButton())

        #Signal for clicking the switch language button
        self.btnLanguage.clicked.connect(lambda: self.switchlanguage())

        #Create the DB connection and Signal for clicking the Table button
        self.createDB()
        global model
        model = QtSql.QSqlTableModel()
        self.initializeModel(model)
        #self.btnTable.clicked.connect(lambda: self.clickedTablebutton(model))

        #Signal for clicking the Video button
        self.btnVideo.clicked.connect(lambda: self.clickedVideobutton())

    def checkconnection(self):
        print('checking connection...')
        isRunning = self.memoryThread.isRunning()
        if isRunning == False:
            print(str(isRunning))
            try:
                print("Connection fail. Disconnect client ...")
                sys.stdout.flush()
                plc.disconnect()
                while plc.get_connected() == False:
                    print("Client disconnected. trying to reconnect client")
                    sys.stdout.flush()
                    plc.connect('192.168.0.3', 0, 0)
                    print("Restarting the memory thread")
                    self.memoryThread.start()
            except:
                self.displayconnectionfail()
                return 0
        elif isRunning == True:
            return 1

    def displayconnectionfail(self):
        # Enhancement: add a "waiting for App to connect" dialog
        # Pop a confirmation prompt
        global LanguageIndex, dynstrings
        print("I am in display connection")
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(dynstrings[LanguageIndex][6])
        msg.setWindowTitle("Connection")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.exec_()


     ### Handler functions for the buttons and UI actions

    #Handlers for button L (left displacement)
    def releasedLButton(self):

        global plc, memL, memR
        print ("Released L!")
        if self.checkconnection() == 1:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/images/left-arrow-button.png"))
            self.btnL.setIcon(icon)

            memR[0] = 0
            memL[0] = 0
            plc.as_db_write(4,4,memL)
            plc.as_db_write(5,5,memR)

    def pressedLButton(self):
        global plc, memL, memR
        print("Pressed L!")
        if self.checkconnection() == 1:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/images/left-arrow-button (1).png"))
            self.btnL.setIcon(icon)
            self.checkconnection()

            memR[0] = 0
            memL[0] = 1
            plc.as_db_write(4, 4, memL)
            plc.as_db_write(5, 5, memR)

    #Handlers for button R (right displacement)
    def releasedRButton(self):
        global plc, memL, memR
        print ("Released R!")
        if self.checkconnection() == 1:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/images/right-arrow-button.png"))
            self.btnR.setIcon(icon)
            self.checkconnection()

            memR[0] = 0
            memL[0] = 0
            plc.as_db_write(5, 5, memR)
            plc.as_db_write(4, 4, memL)

    def pressedRButton(self):
        global plc, memL, memR
        print ("Pressed R!")
        if self.checkconnection() == 1:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/images/right-arrow-button (1).png"))
            self.btnR.setIcon(icon)
            self.checkconnection()

            memR[0] = 1
            memL[0] = 0
            plc.as_db_write(5, 5, memR)
            plc.as_db_write(4, 4, memL)

    #Handlers for Light buttons
    def clickedLightButton(self, lamp):
        self.checkconnection()
        global plc, mem, LOn, lightmemindex
        print ("Clicked Light!")
        if self.checkconnection() == 1:
            LOn[lamp] = not LOn[lamp]
            icon = QtGui.QIcon()
            i = lightmemindex[lamp]

            if LOn[lamp] == True:

                icon.addPixmap(QtGui.QPixmap(":/images/idea (2).png"))

                if lamp == 0:
                    self.btnL1.setIcon(icon)
                elif lamp == 1:
                    self.btnL2.setIcon(icon)
                elif lamp == 2:
                    self.btnL3.setIcon(icon)

                mem[0] = 1
                plc.as_db_write(i, i, mem)
                print("light is On")

            else:
                icon.addPixmap(QtGui.QPixmap(":/images/idea (1).png"))

                if lamp == 0:
                    self.btnL1.setIcon(icon)
                elif lamp == 1:
                    self.btnL2.setIcon(icon)
                elif lamp == 2:
                    self.btnL3.setIcon(icon)

                mem[0] = 0
                plc.as_db_write(i, i, mem)
                print("light is Off")

    # Handler for Err reset buttons
    def clickedErrButton(self, errcode):
        self.checkconnection()
        global plc, mem, errflag, errrstmemindex
        if self.checkconnection() == 1:
            i = errrstmemindex[errcode - 1]

            if errflag[errcode - 1] == 1:
                # pop-up a password dialog
                gonogo = self.passwordDialog()

                # reset the error
                if gonogo == 1:
                    mem[0] = 1
                    plc.as_db_write(i, i, mem)
                    time.sleep(0.1) #avoids a job pending error from the snap7 library
                    mem[0] = 0
                    plc.as_db_write(i, i, mem)
                    time.sleep(0.1) #avoids a job pending error from the snap7 library
                    self.updatetabadminicon()

                    # Write reset action to the database
                    self.writetodatabase(errcode, 0)

    #Handler for quit button
    def pressedQuitButton(self):

        gonogo = self.passwordDialog()
        if gonogo == 1:
            self.close()

    #Handle for clicking the water counter RESET button in the admin tab
    def clickedWtrCntrRstButton(self):
        global t0, t0date, LanguageIndex
        if self.checkconnection() == 1:
            #Pop a confirmation prompt
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText(dynstrings[LanguageIndex][1])
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

            retval = msg.exec_()
            if retval == 1024:
                WtrRstCntr[0] = 1
                plc.as_db_write(13, 13, WtrRstCntr)
                time.sleep(0.1)
                WtrRstCntr[0] = 0
                plc.as_db_write(13, 13, WtrRstCntr)
                time.sleep(0.1)

                #Reset the time interval
                t0 = time.time()  # Time since last reset of the counter or last reboot of the app in seconds
                t0date = datetime.datetime.now()  # Time since last reset of the counter or last reboot of the app in days

    ### Frequently used functions

    # pop-up a password dialog and return a go no-go flag
    def passwordDialog(self):
        global adminpswd, LanguageIndex, dynstrings
        string = dynstrings[LanguageIndex][0]

        text, ok = QInputDialog.getText(self, '', string)

        if ok:
            if str(text) == adminpswd:
                return 1
            else:
                return 0


    #Updates the water consumption
    def IncWaterConsCntr(self, watercntrvalue):
        global WaterCons, VolumeIncrement, VolumeIncrementIndex, t0, t0date, LanguageIndex, dynstrings
        string = dynstrings[LanguageIndex][2]
        lblstring = string + t0date.strftime("%d-%m-%y")
        self.lblLastRst.setText(lblstring)

        WaterCons = VolumeIncrement[VolumeIncrementIndex] * watercntrvalue
        t = time.time()
        deltat = t - t0
        deltatdays = deltat / (60 * 60 * 24)
        deltatdaysceil = -(-deltat // (60 * 60 * 24))

        if VolumeIncrementIndex / 2 >= 1:

            if deltatdays < 2:
                WaterCons = WaterCons / deltatdaysceil
            else:
                WaterCons = WaterCons / deltatdays

        self.lcdWaterCons.display(WaterCons)

    def clickecWtrCntrUnitButton(self):

        global VolumeIncrementIndex, WaterConsUnitStr, LanguageIndex

        #Scroll to the next index
        VolumeIncrementIndex = (VolumeIncrementIndex + 1) % len(VolumeIncrement)

        string = WaterConsUnitStr[LanguageIndex][VolumeIncrementIndex]
        self.btnWtrCntrUnit.setText(string)

    #Updates the error messages
    def displaypumpError(self, errcode):
        global errflag, LanguageIndex, dynstrings

        actualerrorcode = errflag[0] + 2 * errflag[1]

        if errcode != actualerrorcode:


            #Update the pump error flags
            if errcode == 0:
                errflag[0] = 0
                errflag[1] = 0

            if errcode == 1:
                if errflag[0] == 0:
                    self.writetodatabase(1, 1)
                errflag[0] = 1
                errflag[1] = 0

                self.clickedStopWaterbutton()

            if errcode == 2:
                if errflag[1] == 0:
                    self.writetodatabase(2, 1)
                errflag[0] = 0
                errflag[1] = 1

            if errcode == 3:
                errflag[0] = 1
                errflag[1] = 1

            self.updatetabadminicon()

            # Handle error display of pump errors
            icon = QtGui.QIcon()
            if errflag[0] == 0:
                icon.addPixmap(QtGui.QPixmap(":/images/warning_black.png"))
                self.btnErr1.setIcon(icon)
                self.Err1lbl.setText('')
            else:
                icon.addPixmap(QtGui.QPixmap(":/images/warning_yellow.png"))
                self.btnErr1.setIcon(icon)
                self.Err1lbl.setText(dynstrings[LanguageIndex][3])

            # Handle error display of pump errors
            if errflag[1] == 0:
                icon.addPixmap(QtGui.QPixmap(":/images/warning_black.png"))
                self.btnErr2.setIcon(icon)
                self.Err2lbl.setText('')
            else:
                icon.addPixmap(QtGui.QPixmap(":/images/warning_yellow.png"))
                self.btnErr2.setIcon(icon)
                self.Err2lbl.setText(dynstrings[LanguageIndex][4])

    def updatetabadminicon(self):
        global errflag
            #update the admin tab icon
        icon = QtGui.QIcon()
        errorsum = errflag[0] + errflag[1] + errflag[2]
        if errorsum == 0:
            icon.addPixmap(QtGui.QPixmap(":/images/wrench.png"))
            self.tabMain.setTabIcon(2, icon)
        if errorsum > 0:
            icon.addPixmap(QtGui.QPixmap(":/images/warning_yellow.png"))
            self.tabMain.setTabIcon(2, icon)

    def motorvaluechanged(self, value):
        global errflag, err3cntr, LanguageIndex, dynstrings

        if value > err3cntr:
            string = dynstrings[LanguageIndex][5] + str(value) + ')'
            self.Err3lbl.setText(string)
            # Write raise action to the database
            self.writetodatabase(3, value)
            err3cntr = value

        if (value > 0) != errflag[2]:

            if value > 0:

                # Turn on the error display
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap(":/images/warning_yellow.png"))
                self.btnErr3.setIcon(icon)
                errflag[2] = 1
                self.updatetabadminicon()

            elif value == 0:

                # Turn off the error display
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap(":/images/warning_black.png"))
                self.btnErr3.setIcon(icon)
                self.Err3lbl.setText('')
                #Write reset action to the database
                self.writetodatabase(3, 0)
                errflag[2] = 0
                err3cntr = 0
                self.updatetabadminicon()

    def switchlanguage(self):
        global LanguageIndex, VolumeIncrementIndex, fixstrings, err3cntr
        LanguageIndex = (LanguageIndex + 1) % 2

        #Update all fix strings
        self.btnLanguage.setText(fixstrings[LanguageIndex][0])
        self.contactlbl.setText(fixstrings[LanguageIndex][1])
        self.labelcons.setText(fixstrings[LanguageIndex][2])
        self.labelkitc.setText(fixstrings[LanguageIndex][3])
        self.labelwash.setText(fixstrings[LanguageIndex][4])
        self.labelroof.setText(fixstrings[LanguageIndex][5])


        #Update dynamic strings
        string = WaterConsUnitStr[LanguageIndex][VolumeIncrementIndex]
        self.btnWtrCntrUnit.setText(string)
        if errflag[0] == 1:
            self.Err1lbl.setText(dynstrings[LanguageIndex][3])
        if errflag[1] == 1:
            self.Err2lbl.setText(dynstrings[LanguageIndex][4])
        if errflag[2] == 1:
            string = dynstrings[LanguageIndex][5] + str(err3cntr) + ')'
            self.Err3lbl.setText(string)

    def clickedStopWaterbutton(self):
        global plc, errflag, memStopWtr
        if self.checkconnection() == 1:

            if memStopWtr[0] == 0:
                # Stop the water
                memStopWtr[0] = 1
                plc.as_db_write(15, 15, memStopWtr)

                # change the button visual
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap(":/images/block-faucet-red.png"))
                self.btnStopWater.setIcon(icon)

                # Write the action to the database
                self.writetodatabase(5, 1)

            elif memStopWtr[0] == 1:
                # If error 1 has been reinitialized
                if errflag[0] == 0:
                    # Start the water
                    memStopWtr[0] = 0
                    plc.as_db_write(15, 15, memStopWtr)

                    # change the button visual
                    icon = QtGui.QIcon()
                    icon.addPixmap(QtGui.QPixmap(":/images/block-faucet.png"))
                    self.btnStopWater.setIcon(icon)

                    # Write the action to the database
                    self.writetodatabase(5, 0)

    def clickedVideobutton(self):
        # pop-up a password dialog
        #gonogo = self.passwordDialog()
        go = 1
        # start automated displacement for the video
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/video_gr.png"))
        if go == 1:

            self.btnVideo.setIcon(icon)

            self.automaticDisplacement()

            icon.addPixmap(QtGui.QPixmap(":/images/video.png"))
            self.btnVideo.setIcon(icon)

    def automaticDisplacement(self):

        time.sleep(15)
        self.pressedRButton()
        time.sleep(30)
        self.releasedRButton()
        time.sleep(10)
        self.pressedLButton()
        time.sleep(15)
        self.releasedLButton()

    def clickedTablebutton(self, model):
        #Pop-up the table view

        view = QtWidgets.QTableView()
        view.setModel(model)
        view.setWindowTitle("Table Model (View1)")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(view)

        dlg = QtWidgets.QDialog()
        dlg.setLayout(layout)
        dlg.setWindowTitle("Contenu de la database")
        dlg.exec_()

    # Writes to the local database
    def writetodatabase(self, errcode, action):

        #Increment database entry ID
        global localdbID, model
        localdbID += 1
        localdbIDstr = str(localdbID)

        #Build the action string
        if action == 0:
            actionstr = "RESET"
        elif action == 1:
            actionstr = "RAISE"
        elif action > 1:
            actionstr = "RAISE (" + str(action) + ")"

        #Build the date and time strings
        dt = datetime.datetime.now()
        datestr = dt.strftime("%d-%m-%y")
        timestr = dt.strftime("%H:%M")
        errorcodestr = str(errcode)

        #issue the query to the database
        query = QtSql.QSqlQuery()
        SQLstring = "insert into localdb values("\
                    + localdbIDstr + ", '" \
                    + errorcodestr + "', '" \
                    + actionstr + "', '" \
                    + datestr + "', '" \
                    + timestr + "')"
        query.exec_(SQLstring)

        #Update the model
        model = QtSql.QSqlTableModel()
        self.initializeModel(model)

    def initializeModel(self, model):
        model.setTable('localdb')
        model.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        model.select()
        model.setHeaderData(0, QtCore.Qt.Horizontal, "ID")
        model.setHeaderData(1, QtCore.Qt.Horizontal, "Err")
        model.setHeaderData(2, QtCore.Qt.Horizontal, "Action")
        model.setHeaderData(3, QtCore.Qt.Horizontal, "Date")
        model.setHeaderData(4, QtCore.Qt.Horizontal, "Time")





### CREATE A SQLite DATABASE
    def createDB(self):

        db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('localdb.db')

        if not db.open():
            QtGui.QMessageBox.critical(None, QtGui.qApp.tr("Cannot open database"),
                                    QtGui.qApp.tr("Unable to establish a database connection.\n"
                                                  "This example needs SQLite support. Please read "
                                                  "the Qt SQL driver documentation for information "
                                                  "how to build it.\n\n" "Click Cancel to exit."),
                                    QtGui.QMessageBox.Cancel)
            return False

        query = QtSql.QSqlQuery()
        dt = datetime.datetime.now()
        datestr = dt.strftime("%d-%m-%y")
        timestr = dt.strftime("%H:%M")
        errorcodestr = "1"
        actionstr = "RESET"

        query.exec_("create table localdb("
                    "id int primary key, "
                    "errorcode varchar(5), "
                    "action varchar(10), "
                    "date varchar(20), "
                    "time varchar(20))")
        return True



# I feel better having one of these
def main():
    # a new app instance
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()


    # without this, the script exits immediately.
    sys.exit(app.exec_())



# python bit to figure how who started This
if __name__ == "__main__":
    main()





