# PyQt5-Snap7-App

This application is simple user interface writin in python with PyQt5 library for an home automation application. It is a simple touch screen interface that runs on raspberry pi. Its purpose is to read and write data to the registries of a Siemens PLC (tested on a logo8!) using the S7 protocol to control the PLC (programable logic controller) i.e. tell him to do stuff and read some sensor data. The UI was created using Qt creator (mainwindow_prod.ui). Then it is translated to a specific python class using the instructions described in the PyQt_instructions. The ressources_rc.py file is also created to grant access to the app to the images embedded in the app.

## What it does

It takes inputs values from the Siemens PLC using the [Snap7 library](http://snap7.sourceforge.net/) by Davide Nardella through a thread running in parallel (memorythread.py)and displays the harvested information as alarms or a increment to the water counter. It also send instructions to the PLC using the same protocol to move something around and turn lights on and off.

Sometimes the connection to the PLC can be lost for what ever reason. Their is therefore a mecanism in the app to pick up a connection error and display it as well as trying to automatically reconnect to the PLC.

Their are three tabs, one for moving curtains, one for turning lights on and off and one for displaying water consumption and alarms relative to the plumbing. In this tab there is also a button to turn off the main water valve in case of a leak and a button swap displayed language. Yes! It is also a internationalized application! Oh and one more thing, an alarm log is stored in a Qsqlite database


