import numpy as np
import requests
import json
from config import CENSUS_API_KEY

from flask import Flask, jsonify


app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/><br/>"
        f"Get poverty rate: for latitude/longitude<br/>"
        f"/api/v1.0/poverty/&lt;float:latitude&gt;/&lt;float:longitude><br/&gt;<br/><br/>"
        f"Get population density (per square mile): for latitude/longitude<br/>"
        f"/api/v1.0/population/&lt;float:latitude&gt;/&lt;float:longitude><br/&gt;<br/><br/>"
        f"Get diversity index (probability of two people being of a different race): for latitude/longitude<br/>"
        f"/api/v1.0/population/&lt;float:latitude&gt;/&lt;float:longitude><br/&gt;<br/><br/>"
    )

'''
 Get FIPS information from FCC
 '''
def get_fips_information(latitude, longitude):
    params = {
        "format": "json",
        "showall": "true",
        "censusYear": "2010",
        "latitude": latitude,
        "longitude": -longitude
    }

    base_url = "https://geo.fcc.gov/api/census/block/find"

    response = requests.get(base_url, params=params)

    fcc_data = response.json()

    l = {}

    l["state_code"] = fcc_data["State"]["FIPS"];
    l["county_code"] = fcc_data["County"]["FIPS"][2:5];
    l["tract_code"] = fcc_data["Block"]["FIPS"][5:11];

    return l


'''
Get the poverty rate at a latitude/longitude in a census tract
Uses FCC API to first turn latitude/longitude into a FIPS code then calls census for that FIPS code
Census tracts contain between 2,500 to 8,000 people
'''
@app.route("/api/v1.0/poverty/<float:latitude>/<float:longitude>")
def poverty_rate(latitude=None, longitude=None):

    l = get_fips_information(latitude, longitude)

    # Get census data based on FIPs code
    params = {
        "key": CENSUS_API_KEY,
        "get": "B17001_001E,B17001_002E",
        "for": "tract:" + l["tract_code"],
        "in": "state:" + l["state_code"] + "+county:" + l["county_code"]
    }

    base_ACS5 = "/2018/acs/acs5"
    base_url = "https://api.census.gov/data"

    response = requests.get(base_url + base_ACS5, params=params)

    census_data = response.json()

    a = census_data
    population = float(a[1][0])
    poverty = float(a[1][1])

    if float(population) > 0.0:
        pov_rate = 100.0 * poverty / population
    else:
        pov_rate = 0.0

    r = {
        "Status": "Ok",
        "poverate_rate": pov_rate
    }

    return jsonify(r)


'''
Get the population density at a latitude/longitude in a census tract
Uses FCC API to first turn latitude/longitude into a FIPS code then calls census for that FIPS code
Census tracts contain between 2,500 to 8,000 people
'''
@app.route("/api/v1.0/population/<float:latitude>/<float:longitude>")
def population_density(latitude=None, longitude=None):

    l = get_fips_information(latitude, longitude)

    # Get census data based on FIPs code
    params = {
        "key": CENSUS_API_KEY,
        "get": "B17001_001E",
        "for": "tract:" + l["tract_code"],
        "in": "state:" + l["state_code"] + "+county:" + l["county_code"]
    }

    base_ACS5 = "/2018/acs/acs5"
    base_url = "https://api.census.gov/data"

    response = requests.get(base_url + base_ACS5, params=params)

    census_data = response.json()

    a = census_data
    population = float(a[1][0])

    params = {
        "key": CENSUS_API_KEY,
        "get": "LAND_AREA",
        "for": "tract:" + l["tract_code"],
        "in": "state:" + l["state_code"] + "+county:" + l["county_code"]
    }

    base_PDB  = "/2018/pdb/tract"
    base_url = "https://api.census.gov/data"

    response = requests.get(base_url + base_PDB, params=params)

    census_data = response.json()

    # square miles
    a = census_data
    land_area = float(a[1][0])

    #print(",".join(a[0]))
    #print(",".join(a[1]))

    if float(land_area) > 0.0:
        pop_density = population / land_area
    else:
        pop_density = 0.0

    r = {
        "Status": "Ok",
        "population_density": pop_density
    }

    return jsonify(r)


'''
Get the education level at a latitude/longitude in a census tract
Uses FCC API to first turn latitude/longitude into a FIPS code then calls census for that FIPS code
Census tracts contain between 2,500 to 8,000
'''
@app.route("/api/v1.0/education/<float:latitude>/<float:longitude>")
def education_level(latitude=None, longitude=None):
    pass

'''
Get the diversity index at a latitude/longitude in a census tract
Uses FCC API to first turn latitude/longitude into a FIPS code then calls census for that FIPS code
Census tracts contain between 2,500 to 8,000
'''
@app.route("/api/v1.0/diversity/<float:latitude>/<float:longitude>")
def diversity_index(latitude=None, longitude=None):

    l = get_fips_information(latitude, longitude)

    # B02001_001E: Total
    # B02001_002E: White alone
    # B02001_003E: Black or African American alone
    # B02001_004E: American Indian and Alaska Native alone
    # B02001_005E: Asian alone
    # B02001_006E: Native Hawaiian and Other Pacific Islander alone
    # B02001_007E: Some other race alone
    # B02001_008E: Two or more races
    # B02001_009E: Two or more races, Two races including Some other race
    # B02001_010E: Two or more races!!Two races excluding Some other race, and three or more races

    #Pr(Same race) = Pr(B02001_002E) ** 2 + Pr(B02001_003E) ** 2 + Pr(B02001_004E) ** 2 +
    #Pr(B02001_005E) ** 2 + Pr(B02001_006E) ** 2 + Pr(B02001_007E) ** 2 + Pr(B02001_008E) ** 2 +
    #Pr(B02001_009E) ** 2 + Pr(B02001_010E) ** 2

    # Homogeneity Probability
    # Probability two people are the same race 
    # Diversity Index (1 - Homogeneity Probability)
    # Higher diversity index means area more diverse

    params = {
        "key": CENSUS_API_KEY,
        "get": "B02001_002E,B02001_003E,B02001_004E,B02001_005E,B02001_006E,B02001_007E,B02001_008E,B02001_009E,B02001_010E",
        "for": "tract:" + l["tract_code"],
        "in": "state:" + l["state_code"] + "+county:" + l["county_code"]
    }

    base_ACS5 = "/2018/acs/acs5"
    base_url = "https://api.census.gov/data"

    response = requests.get(base_url + base_ACS5, params=params)

    census_data = response.json()

    a = census_data

    total = float(a[1][0]) + float(a[1][1]) + float(a[1][2]) + float(a[1][3]) + float(a[1][4]) + float(a[1][5]) + float(a[1][6]) + float(a[1][7])  + float(a[1][8])

    homogeneity = (float(a[1][0])/total)**2 + (float(a[1][1])/total)**2 + (float(a[1][2])/total)**2 + (float(a[1][3])/total)**2 + (float(a[1][4])/total)**2 + (float(a[1][5])/total)**2 + (float(a[1][6])/total)**2 + (float(a[1][7])/total)**2 + (float(a[1][8])/total)**2

    print(",".join(a[0]))
    print(",".join(a[1]))

    r = {
        "Status": "Ok",
        "diversity_index": 1-homogeneity,
    }

    return jsonify(r)


if __name__ == '__main__':
    app.run(debug=True)
