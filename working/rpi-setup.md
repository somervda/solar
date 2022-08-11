## Guide to setting up the Raspberry Pi for the Solar System

Includes changes to reduce power usage (Turn off LEDS, turn of USB, Turn off HDMI and Blue tooth)

1. Use the raspberry pi imager () https://www.raspberrypi.com/software/ ) to set up the SD card for the RPI. I used Raspberry Pi OS (Lite) 32 bit. I opened the imager options and set the host name (solar in my case) and enabled ssh with the password option. Set the user/password (I used the pi user as my main one). Enter the WiFi SID and password you want to use (Because the solar system is remote you need to have the rpi set up for wireless internet)
2. Put the SD card in the RPI and plug in power.
3. Check you can connect to the RPI using ssh ( i.e. `ssh pi@<hostname>`)
4. from ssh run `sudo raspi-config`. Go to "interface Options" and turn on serial port hardware (serial port logon not needed). Reboot to apply.
5. Do `sudo apt update` and `sudo apt upgrade`
6. Do `sudo apt install apache2 -y`
7. Do `sudo apt install libapache2-mod-wsgi-py3 -y`
8. Do `sudo apt install python3-pip`
9. Do `sudo pip install flask`
10. Add the following to /etc/rc.local to minimize power usage . the first two lines turn off the LEDs on the RPI and the
    next two will change the permissions on the usb bind/unbind references so the usb hardware can be turned on and off.

```
    sh -c 'echo 0 > /sys/class/leds/led0/brightness'
    sh -c 'echo 0 > /sys/class/leds/led1/brightness'

    chmod o+w /sys/bus/usb/drivers/usb/unbind
    chmod o+w /sys/bus/usb/drivers/usb/bind
```

11. add the following to a /etc/profile.d/solarpath.sh

```
export PATH=$PATH:/home/pi/local/bin:/usr/local/lib/python3.9/site-packages
export PYTHONPATH=/home/pi/solar/shared:/home/pi/hamlib/hamlib-4.4/bindings:/home/pi/hamlib/hamlib-4.4/bindings/.libs
```

12. Add this to /boot/config.txt dtoverlay=disable-bt (turns off bluetooth, Place under the [All] section)

```
    [All]
    dtoverlay=disable-bt
```

also change the dtoverlay driver to vc4-fkms-v3d (The one that gets loaded in latest RPI OS doesn't work with tvservice)

```
   dtoverlay=vc4-fkms-v3d
```

13. Add the following to /etc/rc.local to minimize power usage (turns off the HDMI power)

```
    sh -c '/usr/bin/tvservice -o'
```

14. Install psutil - solar uses it to manage the rigctld daemon

```
    sudo pip install psutil
```

### Set up development environment

20. Create a folder called `~/solar`
21. In Visual Studio Code add the Remote Development Extension and do the setup shown in Part 3 video https://youtu.be/88nCALFmBRo
22. Load the code to solar from github https://github.com/somervda/solar
23. Optional `sudo apt install gedit` and set up an `export DISPLAY=<XWindows target IP>:0`

24. Optional `sudo apt install acl -y` to install the setfacl command , useful for viewing and changing ACL while debugging, didn't need it in the end
25. Optional `sudo apt-get install samba samba-common-bin` to install smb and `sudo gedit /etc/samba/smb.conf` to add a share over solar

```
    [global]
    netbios name = solar
    server string = The solar RPI shares
    workgroup = WORKGROUP


    [solar]
    path = /home/pi/solar
    comment = No comment
    writeable=Yes
    create mask=0777
    directory mask=0777
    public=no
```

then do a `sudo smbpasswd -a pi` and `sudo /etc/init.d/samba restart`
