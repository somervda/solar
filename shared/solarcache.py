# The solarcache class manages the interface to the solarcache.json file
# The solarcache.json file contains the run time parameters for the solar demon
# i.e. What to do when the batter drops below a particular levl, as 
# well as timeing parameter for how long the webcam and radio should be power 
# before being turned off.
# It also contains more transitive parameters like how long relays have been turned on.
# The class exposes all this data in a single name space as well as managing 
# locking and reading/writting of the soilarcache.json file. This class
# will be used by the solardemon and the solarwww web service processes.