# Location API

**Python Flask API**

API that can give statistics for any latitude/longitude in the United States.

Uses FCC API to turn latitude/longitude into a US Census FIPs code. Then uses Census api. Census tracts contain between 2,500 to 8,000 people.

* Get the poverty rate (percentage) at a latitude/longitude in a census tract.  
Example:
/api/v1.0/poverty?lat=[Latuditude]&lon=[Longitude]

* Get the population density (per square mile) at a latitude/longitude in a census tract.  
Example:
/api/v1.0/population_density?lat=[Latuditude]&lon=[Longitude]

* Get the diversity index (probability of two people being of a different race) at a latitude/longitude in a census tract. 
* High scores close to 1 indicate higher diversity 
Example:
/api/v1.0/diversity?lat=[Latuditude]&lon=[Longitude]

* Get housing units as a percentage at a latitude/longitude in a census tract.  
Example:
/api/v1.0/housing_units?lat=[Latuditude]&lon=[Longitude]

* Get education level as a percentage at a latitude/longitude in a census tract.  
Example:
/api/v1.0/education?lat=[Latuditude]&lon=[Longitude]

* Get gender as a percentage at a latitude/longitude in a census tract.  
Example:
/api/v1.0/gender?lat=[Latuditude]&lon=[Longitude]

* Get average age at a latitude/longitude in a census tract.  
Example:
/api/v1.0/age?lat=[Latuditude]&lon=[Longitude]

* Get healthcare coverage (overall, medicare, medicaid, tricare) as percentages at a latitude/longitude in a census tract.  
Example:
/api/v1.0/insurance?lat=[Latuditude]&lon=[Longitude]


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
  "diversity_index": 0.599, 
  "population_density": 12980.35, 
  "poverty_rate": 11.39
}