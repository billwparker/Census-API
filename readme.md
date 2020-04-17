# Census API

**Python Flask API**

API that can give statitics for a latitude/longitude.


Uses FCC API to turn latitude/longitude into a US Census FIPs code.

Census tracts contain between 2,500 to 8,000 people.

* Get the poverty rate at a latitude/longitude in a census tract.  
Example:
/api/v1.0/poverty/<latitude>/<longitude>

* Get the population density (per square mile) at a latitude/longitude in a census tract.  
Example:
/api/v1.0/population/<latitude>/<longitude>

* Get the diversity index (probability of two people being of a different race) at a latitude/longitude in a census tract.  
Example:
/api/v1.0/diversity/<latitude>/<longitude>