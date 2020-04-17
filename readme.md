# Census API

Python Flask API

Census API endpoints that pulls information for a specific latitude/longitude.

Uses FCC API to turn latitude/longitude into a US Census FIPs code.

Census tracts contain between 2,500 to 8,000 people.

Get the poverty rate at a latitude/longitude in a census tract.
/api/v1.0/poverty/<float:latitude>/<float:longitude>