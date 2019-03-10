### Raspbian-desktop SD card image

A desktop version of the Official Raspbian Image (password:raspberry!), including chromnium, window manager, git, pip, nano and all sort of other usefull stuff
has been prepared with the following:

0. Password was changed, the same as Movehome-raspbian (raspbian jessie lite base image)
1. SSH enabled with raspi-config
2. Wifi setup in /etc/wpa_supplicant/wpa_supplicant.conf
3. movehome git repo cloned at /home/pi
4. sudo pip install django
5. sudo apt-get update
6. sudo apt-get install xinput
7. Edited the /boot/config.txt file to rotate the screen and setup the TFT touch screen
8. added the line /home/pi/movehome/setup_script.sh to rotate the touch pad
9. Edited the file ~/.config/lxsession/LXDE-pi/autostart with the line
```
@chromium-browser --incognito --kiosk 192.168.0.170:8000/ledblink
```
10. A cronjob is there to start the Django server at reboot (check `crontab -e`) running the setup_server.sh script
12. sudo apt-get install python3-pyqt5
13. Commanded out and added some lines in setup_script.sh, server_script.sh and ~/.config/lxsession/LXDE-pi/autostart
to boot the PyQt app at startup
14. sudo pip install python-snap7
15. cd /home/pi/movehome/snap7-iot-arm-1.4.2/build/unix and execute
```
sudo make -f arm_v7_linux.mk install
```
15. sudo ldconfig
16. added sudo ifconfig eth0 192.168.0.2 netmask 255.255.255.0 up
 to the setup_script.sh
17. sudo pip3 install python-snap7