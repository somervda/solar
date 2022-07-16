## Guide to setting up the Raspberry Pi for the Solar System

1. Use the raspberry pi imager () https://www.raspberrypi.com/software/ ) to set up the SD card for the RPI. I used Raspberry Pi OS (Lite) 32 bit. I opened the imager options and set the host name (solar in my case) and enabled ssh with the password option. Set the user/password (I used the pi user as my main one). Enter the WiFi SID and password you want to use (Because the solar system is remote you need to have the rpi set up for wireless internet)
2. Put the SD card in the RPI and plug in power.
3. Check you can connect to the RPI using ssh ( i.e. `ssh pi@<hostname>`)
4. from ssh run `sudo raspi-config`. Go to "interface Options" and turn on serial port hardware (serial port logon not needed). Reboot to apply.
5. Do `sudo apt update` and `sudo apt upgrade`
6. Do `sudo apt install apache2 -y`
7. Do `sudo apt install libapache2-mod-wsgi-py3 -y`
8. Do `sudo apt install python3-pip`
9. Do `sudo pip install flask`
10. Add the following to /etc/rc.local to minimize power usage (turns off LEDs and usb bus)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`sh -c 'echo 0 > /sys/class/leds/led0/brightness`

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`sh -c 'echo 0 > /sys/class/leds/led1/brightness`

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`echo '1-1' |tee /sys/bus/usb/drivers/usb/unbind`

11. add the following to /etc/profile

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`export PYTHONPATH=/home/pi/solar/shared`

### Set up development environment

20. Create a folder called `~/solar`
21. In Visual Studio Code add the Remote Development Extension and do the setup shown in Part 3 video https://youtu.be/88nCALFmBRo
22. Load the code to solar from github https://github.com/somervda/solar
23. Optional `sudo apt install gedit` and set up an `export DISPLAY=<XWindows target IP>:0`

24. Do a `sudo apt install acl -y` to install the setfacl command - needed latter to add www-data user to some of the solar directory permissions
