1. Update the apache sites-available default file '/etc/apache2/sites-available/000-default.conf'

```
VirtualHost *:80>
	# The ServerName directive sets the request scheme, hostname and port that
	# the server uses to identify itself. This is used when creating
	# redirection URLs. In the context of virtual hosts, the ServerName
	# specifies what hostname must appear in the request's Host: header to
	# match this virtual host. For the default virtual host (this file) this
	# value is not decisive as it is used as a last resort host regardless.
	# However, you must set it for any further virtual host explicitly.
	#ServerName www.example.com

	ServerAdmin webmaster@localhost
	DocumentRoot /var/www/html

	# Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
	# error, crit, alert, emerg.
	# It is also possible to configure the loglevel for particular
	# modules, e.g.
	#LogLevel info ssl:warn

	ErrorLog ${APACHE_LOG_DIR}/error.log
	CustomLog ${APACHE_LOG_DIR}/access.log combined

	# For most configuration files from conf-available/, which are
	# enabled or disabled at a global level, it is possible to
	# include a line for only one particular virtual host. For example the
	# following line enables the CGI configuration for this host only
	# after it has been globally disabled with "a2disconf".
	#Include conf-available/serve-cgi-bin.conf

    WSGIDaemonProcess helloapp threads=5 display-name=solarwww
    WSGIScriptAlias /hello /home/pi/solar/solarwww/hello.wsgi

    <Directory /home/pi/solar/solarwww>
        WSGIProcessGroup helloapp
        WSGIApplicationGroup %{GLOBAL}
        Require all granted
    </Directory>
</VirtualHost>
```

2. Create the wsgi file

```
import sys
sys.path.insert(0, '/home/pi/solar/solarwww')

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
