https://learn.adafruit.com/adafruit-5-800x480-tft-hdmi-monitor-touchscreen-backpack/overview

In the Movehome modules, the user interface is curently a very basic app written in PyQt. Does the job of moving the module back
and forth using the GPIO pins of the Raspberry Pi through the RPi.GPIO library.

1. Download and install the latest versions of the Python libraries

[Python library](https://pypi.python.org/pypi/RPi.GPIO) for the control of the GPIO pins on the Raspberry Pi

    sudo apt-get install python-dev python-rpi.gpio

to be able to run the PyQt5 app (yes it runs on python 3)

    sudo apt-get install python3 python3-pyqt5

2. To run the latest version of the PyQt app on the Raspberry Pi

First make sure you have the mainwindow_auto.py, the ressources_rc.py and the
main4pi_3.py files in the same directory. Then run

    Python3 main4pi_3.py

This should open the PyQt app

 3. Hook up the Adafruit TFT monitor to the Raspberry PI

    The image provided on the [google drive](https://drive.google.com/drive/folders/0B5Nqo8lWEvtDd0tzTlpUUjl5SjA) comes out of the box with the config.txt installed in the /boot/ repository.

    More information on the TFT monitor can be found [here](https://learn.adafruit.com/adafruit-5-800x480-tft-hdmi-monitor-touchscreen-backpack/overview)

    The TFT touch screen emulates a mouse pointer. If you feel the touch screen is not responsive enough not sensitive enough or not fast enough, read this [guide](https://learn.adafruit.com/ar1100-resistive-touch-screen-controller-guide)

 4. Plug the Raspberry PI to a suitable USB power supply using a suitable
USB power cable

    At this stage, the OS (Linux Raspbian) will boot up. If you observe erratic operation of the display, the power supply is too weak or the USB power cord to long or wire gage is to small. If you see a small thunderbolt on the screen, it means the same, but you can live with it.

 5. Access the Raspberry PI remotely using SSH

     For this you will need to hook up a keyboard and mouse if you do not want to use the touch screen. Then follow the instructions provided [here](https://computers.tutsplus.com/tutorials/take-control-of-your-raspberry-pi-using-your-mac-pc-ipad-or-phone--mac-54603)

 6. Rotate the touch screen

    On the SD card image, the touchscreen is configured to work in portrait mode. Out of the box,
the screen is in landscape. This [thread](https://www.raspberrypi.org/forums/viewtopic.php?f=108&t=120793)
on the raspberry PI forum goes through how to rotate the touch screen.

    Rotating the touch screen involves two steps:

    1. Rotating the display

        Simply by adding
        `display_rotate=3` or `display_rotate=1` to the /boot/config.txt file (included in this repo).
    2. Rotating the touch pad

First installing xinput

    sudo apt-get install xinput

Then run these to commands in the command line or through a bash script (see setup_script.sh)

    xinput set-prop 'Microchip Technology Inc. AR1100 HID-MOUSE' 'Evdev Axes Swap' 1
and

    xinput --set-prop 'Microchip Technology Inc. AR1100 HID-MOUSE' 'Evdev Axis inversion' 0 1

or

    xinput --set-prop 'Microchip Technology Inc. AR1100 HID-MOUSE' 'Evdev Axis inversion' 1 0

depending weather you used

    display_rotate=3

or

    display_rotate=1

in your /boot/config.txt file.

7. Boot the app at startup

The lines described above are included in the setup_script.sh script which runs on start up by adding

```
/home/pi/movehome/setup_script.sh
```

to the /etc/profile file using

```
sudo nano /etc/profile text file to boot at startup
```

[Other strategies](https://raspberrypi.stackexchange.com/questions/8734/execute-script-on-start-up)
are possible for running the script on startup.