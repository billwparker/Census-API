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
Census tracts contain between 2,500 to 8,000
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
Census tracts contain between 2,500 to 8,000
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
@app.route("/api/v1.0/education/<latitude>/<longitude>")
def education_level():
    pass


if __name__ == '__main__':
    app.run(debug=True)
