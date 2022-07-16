1. Update the apache sites-available default file `/etc/apache2/sites-available/000-default.conf`. I added the WSGI configuration at the end of the
   standard file. Note: for Apache versions 2.4 and latter the directory permissions statement has a new form `Require all granted`.

```
VirtualHost *:80>
	ServerAdmin webmaster@localhost
	DocumentRoot /var/www/html

	ErrorLog ${APACHE_LOG_DIR}/error.log
	CustomLog ${APACHE_LOG_DIR}/access.log combined

    WSGIDaemonProcess helloapp threads=5 display-name=solarwww
    WSGIScriptAlias /hello /home/pi/solar/solarwww/hello.wsgi

    <Directory /home/pi/solar/solarwww>
        WSGIProcessGroup helloapp
        WSGIApplicationGroup %{GLOBAL}
        Require all granted
    </Directory>
</VirtualHost>
```

2. Create the `/home/pi/solar/solarwww/hello.wsgi` file

```
import sys
sys.path.insert(0, '/home/pi/solar/solarwww')
sys.path.append('/home/pi/solar/shared')

from hello import app as application
```

3. Restart apache

```
sudo /etc/init.d/apache2 reload
```

4. Check on logs

```
tail /var/log/apache2/error.log
tail /var/log/apache2/access.log
```

5. Give www-data access to the solar directories solarewww it needs to write to

```
sudo apt install acl -y
sudo setfacl -m u:www-data:rwx /home/pi/solar/logs
sudo setfacl -m u:www-data:rwx /home/pi/solar/shared
```
