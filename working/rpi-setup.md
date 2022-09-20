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
echo '1-1' | tee /sys/bus/usb/drivers/usb/unbind
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

15. Set up solardaemon as a linux service - add the following file `/etc/systemd/system/solardaemon.service`

```
    [Unit]
    Description = Monitor and manages the renogy solar charger and various relays in my shed
    After = multi-user.target

    [Service]
    Type = simple
    ExecStart = python3 -u /home/pi/solar/solardaemon/solardaemon.py
    User = pi
    Group = pi
    Restart = always
    SyslogIdentifier = solardaemon
    RestartSec = 5s
    TimeoutStartSec = infinity
    Environment=PYTHONPATH=/home/pi/solar/shared

    [Install]
    WantedBy=multi-user.target
```

and do the following to enable the service

```
sudo systemctl daemon-reload
sudo systemctl enable solardaemon.service
sudo systemctl start solardaemon.service
```

check on the service status using: `sudo systemctl status solardaemon.service`
and check the syslog for solardaemon messages using: `cat /var/log/syslog | grep solardaemon` or `tail -n 20 /var/log/syslog | grep solardaemon`

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

then do a `sudo smbpasswd -a pi` and `sudo systemctl restart smbd`

### Mumble setup

#### Mumble Server

30. Install mumble-server
    ```
    sudo apt install mumble-server
    ```
31. Configure mumble-server
    ```
    sudo dpkg-reconfigure mumble-server
    ```
    - auto start = yes
    - high priority
    - set SuperUser password
32. Edit the mumble-server.ini file

    ```
    sudo nano /etc/mumble-server.ini
    ```

    - Update the welcome message
    - (Optional) Update the server-password if you want to secure access to the server. Otherwise leave it blank.

33. Restart mumble-server

```
    4.	/etc/init.d/mumble-server restart
```

#### Mumble Client

34. Install pulseaudio (Mumble client seems to work best with these drivers)

```
    sudo apt install pulseaudio
```

35. Install Xvfb (An Xserver that does not use display)- This will allow the mumble client to run headless

```
    sudo apt install xvfb
```

36. Setup Xvfb to run as a service. Add the following file `/etc/systemd/system/xvfb.service`
```
    [Unit]
    Description=X Virtual Frame Buffer Service
    After=network.target

    [Service]
    ExecStart=/usr/bin/Xvfb :99 -screen 0 1024x768x24
    Restart = always
    SyslogIdentifier = Xvfb
    RestartSec = 5s

    [Install]
    WantedBy=multi-user.target
```

37. Enable and start the Xvfb service. Note: Use `export DISPLAY=:99` to send Xwindows to this service.

```
    sudo systemctl enable /etc/systemd/system/xvfb.service
    sudo service xvfb start
```

38. Install the mumble client

```
    sudo apt install mumble
```

39. The mumble client can be run manually by just typing `mumble`. To run the client headless do the following (Note: solarui and solarwwww will do this automatically when the rig is turned on). This uses `nohup` to allow the process to run after the session has ended. The mumble-server connection `mumble://rpi3:@rpi3.home` info is passed to mumble on the command line. The `2> /dev/null` redirects the stdout text into a blackhole. The whole thing is run as a background process `&`. You will need to use `ps aux | grep mumble` to find and then kill mumble. Reset the DISPLAY setting after finishing with mumble.

```
    export DISPLAY=:99
    nohup mumble mumble://rpi3:@rpi3.home 2> /dev/null &
```
