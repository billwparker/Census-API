# Census API

**Python Flask API**

API that can give statistics for any latitude/longitude in the United States.

Uses FCC API to turn latitude/longitude into a US Census FIPs code. Then uses Census api. Census tracts contain between 2,500 to 8,000 people.

* Get the poverty rate (percentage) at a latitude/longitude in a census tract.  
Example:
/api/v1.0/poverty?lat=[Latuditude]&lon=[Longitude]

* Get the population density (per square mile) at a latitude/longitude in a census tract.  
Example:
/api/v1.0/population?lat=[Latuditude]&lon=[Longitude]

* Get the diversity index (probability of two people being of a different race) at a latitude/longitude in a census tract.  
Example:
/api/v1.0/diversity?lat=[Latuditude]&lon=[Longitude]

* Get housing units as a proportion at a latitude/longitude in a census tract.  
Example:
/api/v1.0/housing_units?lat=[Latuditude]&lon=[Longitude]

* Gets the summary at a latitude/longitude in a census tract.  
Example:
/api/v1.0/summary?lat=[Latuditude]&lon=[Longitude]

|Parameters|Description|
|-----|-----------|
|lat	|Latitude	  |
|lon	|Longitude  |

**Example:**
[base url]/api/v1.0/summary?lat=41.8781&lon=87.6298

**Response:**
{
  "Status": "Ok", 
  "diversity_index": 0.5990012104551553, 
  "population_density": 12980.349344978165, 
  "poverty_rate": 11.387720773759462
}