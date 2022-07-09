from solarcache import SolarCache
import json

sc=SolarCache()
sc.loadCache()
# sc.writeCache()
print(sc.cache)