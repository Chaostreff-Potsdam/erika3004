#! /bin/bash

# simple script to setup a Raspberry PI

# TODO currently outdated

serial_device="/dev/ttyAMA0"
erika_speed="1200"
rpirtsrtc_repo="git://github.com/mholling/rpirtscts.git"

#Disable Bluetooth on the RPi 3 B+ so that we can use the serial port.
sudo sh -c 'echo "dtoverlay=pi3-disable-bt" >> /boot/config.txt'

#disable the system service that initialises the modem so it doesn’t use the UART
sudo systemctl disable hciuart
sudo systemctl stop hciuart

#enable ctsrts
git clone $rpirtsrtc_repo
cd rpirtscts
make
sudo ./rpirtscts on

stty -F $serial_device crtscts
stty -F $serial_device speed $erika_speed

stty -F $serial_device -a

#@reboot sudo stty -F /dev/ttyAMA0 speed 1200 crtscts