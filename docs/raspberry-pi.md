
# MoveHome Raspberry Pi Manual

In this section:

 1. [How to Setup the MoveHome Raspberry Pi](#how-to-setup-the-movehome-raspberry-pi)
 1. [How to Run MoveHome Server on docker](#how-to-run-movehome-server-on-docker)

Additional how-to:

 1. [How to Back Up the SD Card Image](#how-to-back-up-the-sd-card-image)

## How to Setup the MoveHome Raspberry Pi

This setup is for Raspberry models 2 and 3.

### Required Tools

Etcher: https://etcher.io/

### Setup from Prebuilt Image

Download the Raspbian ARM image: https://downloads.raspberrypi.org/raspbian_lite_latest

Or alternatively, you can use the prebuilt image that includes:

 - Users set up with password (root and pi)
 - git
 - Docker CE
 - ssh enabled

using this download link: https://www.dropbox.com/s/nfs6n85u1w91jwq/raspbian-arm-jessie-lite-git-docker-ssh.iso?dl=0

### Setup from Rasbian Lite Image (From Scratch)

Download the Raspbian Jessie Lite image [from the Raspberri Website](https://www.raspberrypi.org/downloads/raspbian/)

Burn the image to the SD card using Etcher and then proceed with the basic configuration below.

#### Basic Configuration

Once you boot the OS, use the default user and password for Rasbian:
```
login: pi
password: raspberry
```

Change the default password with:
```
sudo passwd root ****
sudo passwd pi ****
```

Enable SSH and login:
```bash
sudo raspi-config
```
In the raspbian UI, navigate to interfacing *options > ssh > enable*.

Install `vim` and `git`:
```
sudo apt-get install git vim
```

Login with:
```
ssh pi@<ip>
```

#### Docker

Install Docker CE: https://docs.docker.com/engine/installation/linux/docker-ce/debian/#install-using-the-repository

#### Dynamic DNS for SSH Access with NoIp Service

Get an account at: https://my.noip.com

Run the following commands to install the noip service:
```bash
cd /usr/local/src
wget http://www.no-ip.com/client/linux/noip-duc-linux.tar.gz
tar xzf noip-duc-linux.tar.gz
cd no-ip-2.1.9
make
make install
```

Enter your email password then start the client:
```bash
sudo /usr/local/bin/noip2
```

Configure the router to allow SSH, something like:

![image](https://user-images.githubusercontent.com/9644867/28098871-c46bd952-6686-11e7-9475-2856b74089d8.png)

Follow the steps on noip.com and you should be able to ssh with:
```
ssh pi@<dns-address>
```

### Enable and Setup a WIFI Connection

Open the wpa config file:
```
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```

Add the Wifi infos:
```
network={
   ssid="WIFI_SSID"
   psk="WIFIPASSWORD"
}
```

Then enter the command:
```
sudo wpa_cli reconfigure
```

Check the `wlan0` interface has an ip address:
```
ipconfig
```

If you have trouble connecting to the internet over Wifi on the raspberry pi try:

```
sudo ifconfig wlan0 down
sudo ifconfig wlan0 up
```

## How to Back Up the SD Card Image

Download Win32 Disk Imager: http://sourceforge.net/projects/win32diskimager/files/latest/download

In Imager, choose a filename and *read* from the SD card. It will create an iso/daa/bin that you can save and later burn to a new card.

## How to Run MoveHome Server on Docker

Once the setup is complete, we can use the raspberry pi to run our django server.

In order to work with Docker images and containers, we will go through the steps
of installing Docker, getting access to the Docker Hub,
see what commands we use to generate the images and finally how to run the containers
which include our application code (server).

### Docker Overview

The *movehome* Docker image is built from a basic raspbian image called *movehome-raspbian* (debian on raspberry pi) which include all the libraries we need to run
the application - meaning all apt-get installs are done on that image.

Base image: https://hub.docker.com/r/flight212121/movehome-raspbian/

What is in the base image is documented [below](#docker-movehome-raspbian-image-history).

And from the *movehome-raspbian* image, we have automated build to create
the *movehome* image which include the application code: https://hub.docker.com/r/flight212121/movehome/

The automated build is different from the base image because it's built from the Dockerfile on each commit.

### Docker Setup

Install Docker CE for windows/mac: https://www.docker.com/

Get access to Docker Hub: https://hub.docker.com/ and check the latest `<tag>` available for the *movehome* image.

Login to Docker with:
```
sudo docker login
```

### Run MoveHome Server on Docker

To run a container with the latest server, use the following command:
```
sudo docker rm -f movehome && \
    sudo docker pull flight212121/movehome && \
    sudo docker run -it --device /dev/mem:/dev/mem --name movehome -p 8000:8000 --privileged flight212121/movehome
```

To use a different database mounted on a *volume* add the `-v` option:
```
-v C:/Users/Phil/Downloads/movehome-db/:/home/movehome-db/
```
And then start a new container.

To replace the application code with a local git repo, which can be useful during development,
mount the git repo as a volume under `/home/movehome/`:
```
-v /home/movehome-git-repo/DjangoTutorials/myserver/:/home/movehome/
```
This will effectively replace the image's original code with the content of the mounted folder.

### Docker movehome-raspbian Image History

Create base image [from raspbian resin image](https://docs.resin.io/runtime/resin-base-images/?ref=dockerhub#-a-name-base-images-a-base-images-)
```
sudo docker pull resin/rpi-raspbian:jessie
```

Run the container
```
sudo docker run -it --name movehome resin/rpi-raspbian:jessie
```

Then perform the modifications you need:

```
# 0.0.4
sudo apt-get update
sudo apt-get install -y git
sudo apt-get install -y xinput
sudo apt-get install -y python3
sudo apt-get install -y python3-pip
sudo apt-get install -y python-rpi.gpio

# 0.0.5
sudo pip3 install django

# 0.0.6
sudo apt-get install -y python3-rpi.gpio

# 0.0.7 : installing dependencies for Django channels
sudo apt-get update
sudo apt-get install python-dev
sudo apt-get install python-pip
sudo apt-get install python-virtualenv
sudo apt-get install libpq-dev
... postgresql
... postgresql-contrib
... nginx
... supervisor
... python-software-properties
... redis-server

# 0.0.8 : Installing Django channels and its packages
sudo adduser web #with password the same as the pi user
sudo /usr/bin/easy_install virtualenv
apt-get install nano
nano /home/root/requirements.txt
mkdir -p /home/root/venv
virtualenv --no-site-packages /home/root/venv/
source /home/root/venv/bin/activate
pip install -r requirements.txt
deactivate

```

Exit the container with `exit` and commit the container to a new image:
```
sudo docker commit movehome-raspbian flight212121/movehome-raspbian:<tag>
```

Push the new image to Docker Hub with:
```
sudo docker push flight212121/movehome-raspbian:<tag>
```

On subsequent updates, you may want to modify the *movehome-raspbian* image and then increment the tag number.

To do so, pull the image and run it with:
```
sudo docker pull flight212121/movehome-raspbian:<tag>
sudo docker run -it --name movehome-raspbian<tag> flight212121/movehome-raspbian:<tag>
```

Then perform the changes you need as explained above and commit the result.