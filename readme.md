# Solar Shed

The solar shed repository is used to hold the various collections of code used for my solar shed project
see videos about this project at https://www.lupincorp.com/blogs?panel=solarShed .

It contains these main directories:

1. `working` _Contains throw away code snippits to do POC type tests - e.g. renogyTest.py_
2. `solardaemon` _Contains the python code used for the demon process that runs in the background and contiuously manages my solar setup._
3. `solarwww` _Contains the python code for a flask based impmentation of web services to interface to my solar setup (and solardemon)_
4. `solarui` _The Angular program that provides the main interface to my solar shed_
5. `shared` _Shared python modules and the `solarcache.json` file location_
6. `logs` _The daily log files containing the solar controller history_

Information on setting up the Raspberry Pi environment is at https://github.com/somervda/solar/blob/master/working/rpi-setup.md
Notes on setting up the apache-wsgi-flask configuration is at https://github.com/somervda/solar/blob/master/solarwww/flask-apache2-setup.md
