## MoveHome Udoo Manual

In this section:

 1. [How to Setup the MoveHome Raspberry Pi](#how-to-setup-the-movehome-raspberry-pi)
 1. [How to Back Up the SD Card Image](#how-to-back-up-the-sd-card-image)

## How to Setup the MoveHome Raspberry Pi

This is for the u

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

https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-9.1.0-amd64-netinst.iso

#### Installing Fluxbox Window Server on Raspbian (Optional)

Install the following packages:
```bash
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install xorg
sugo apt-get install fluxbox
sudo apt-get install lightdm
```
And then reboot.