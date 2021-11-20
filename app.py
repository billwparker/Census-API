import numpy as np
import requests
import json
from config import CENSUS_API_KEY

from flask import Flask, request, jsonify


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
        f"/api/v1.0/poverty?lat=latitude&lon=longitude<br/><br/>"
        f"Get income: for latitude/longitude<br/>"
        f"/api/v1.0/income?lat=latitude&lon=longitude<br/><br/>"
        f"Get population density (per square mile): for latitude/longitude<br/>"
        f"/api/v1.0/population_density?lat=latitude&lon=longitude<br/><br/>"
        f"Get diversity index (probability of two people being of a different race): for latitude/longitude<br/>"
        f"/api/v1.0/population?lat=latitude&lon=longitude<br/><br/>"
        f"Get housing units (percentage): for latitude/longitude<br/>"
        f"/api/v1.0/housing_units?lat=latitude&lon=longitude<br/><br/>"
        f"Get education level (percentage): for latitude/longitude<br/>"
        f"/api/v1.0/education?lat=latitude&lon=longitude<br/><br/>"
        f"Get insurance coverage (percentage): for latitude/longitude<br/>"
        f"/api/v1.0/insurance?lat=latitude&lon=longitude<br/><br/>"
        f"Get gender (percentage): for latitude/longitude<br/>"
        f"/api/v1.0/gender?lat=latitude&lon=longitude<br/><br/>"
        f"Get average age: for latitude/longitude<br/>"
        f"/api/v1.0/age?lat=latitude&lon=longitude<br/><br/>"
        f"Get summary: for latitude/longitude<br/>"
        f"/api/v1.0/summary?lat=latitude&lon=longitude<br/><br/>"
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

    # print(fcc_data)

    l = {}

    l["state_code"] = fcc_data["State"]["FIPS"];
    l["county_code"] = fcc_data["County"]["FIPS"][2:5];
    l["tract_code"] = fcc_data["Block"]["FIPS"][5:11];

    return l

def get_poverty_rate(l):
    # Get census data based on FIPs code
    params = {
        "key": CENSUS_API_KEY,
        "get": "B17001_001E,B17001_002E",
        "for": "tract:" + l["tract_code"],
        "in": "state:" + l["state_code"] + "+county:" + l["county_code"]
    }

    base_ACS5 = "/2019/acs/acs5"
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

    return round(pov_rate, 2)



'''
Get the poverty rate at a latitude/longitude in a census tract
Uses FCC API to first turn latitude/longitude into a FIPS code then calls census for that FIPS code
Census tracts contain between 2,500 to 8,000 people
'''
@app.route("/api/v1.0/poverty")
def poverty_rate():

    if 'lat' in request.args:
          latitude = float(request.args['lat'])
    else:
        return jsonify({
            "Status": "Error",
            "Message": "Missing parameter: latitude" 
        })

    if 'lon' in request.args:
        longitude = float(request.args['lon'])
    else:
        return jsonify({
            "Status": "Error",
            "Message": "Missing parameter: longitude" 
        })

    l = get_fips_information(latitude, longitude)

    pov_rate = get_poverty_rate(l)

    r = {
        "Status": "Ok",
        "poverty_rate": pov_rate
    }

    return jsonify(r)


def get_income(l):
   
    income = "B19013_001E"
 
    get_vars = f'{income}'
 
    params = {
        "key": CENSUS_API_KEY,
        "get": get_vars,
        "for": "tract:" + l["tract_code"],
        "in": "state:" + l["state_code"] + "+county:" + l["county_code"]
    }
 
    base_ACS5 = "/2019/acs/acs5"
    base_url = "https://api.census.gov/data"
 
    response = requests.get(base_url + base_ACS5, params=params)
 
    census_data = response.json()
 
    a = census_data
 
    median_income = float(a[1][0])
 
    if median_income < 0:
        median_income = 0
 
    return median_income

'''
Get the income at a latitude/longitude in a census tract
Uses FCC API to first turn latitude/longitude into a FIPS code then calls census for that FIPS code
Census tracts contain between 2,500 to 8,000 people
'''
@app.route("/api/v1.0/income")
def income(latitude, longitude):
 
    l = get_fips_information(latitude, longitude)
 
    inc = get_income(l)
 
    r = {
        "Status": "Ok",
        "income": inc
    }
 
    return r

def get_population_density(l):
    # Get census data based on FIPs code
    params = {
        "key": CENSUS_API_KEY,
        "get": "B17001_001E",
        "for": "tract:" + l["tract_code"],
        "in": "state:" + l["state_code"] + "+county:" + l["county_code"]
    }

    base_ACS5 = "/2019/acs/acs5"
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

    base_PDB  = "/2019/pdb/tract"
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

    return round(pop_density, 2)

'''
Get the population density at a latitude/longitude in a census tract
Uses FCC API to first turn latitude/longitude into a FIPS code then calls census for that FIPS code
Census tracts contain between 2,500 to 8,000 people
'''
@app.route("/api/v1.0/population_density")
def population_density():

    if 'lat' in request.args:
          latitude = float(request.args['lat'])
    else:
        return jsonify({
            "Status": "Error",
            "Message": "Missing parameter: latitude" 
        })

    if 'lon' in request.args:
        longitude = float(request.args['lon'])
    else:
        return jsonify({
            "Status": "Error",
            "Message": "Missing parameter: longitude" 
        })

    l = get_fips_information(latitude, longitude)

    pop_density = get_population_density(l)

    r = {
        "Status": "Ok",
        "population_density": pop_density
    }

    return jsonify(r)

def get_education_level(l):
    params = {
        "key": CENSUS_API_KEY,
        "get": "B15003_017E,B15003_018E,B15003_019E,B15003_020E,B15003_021E,B15003_022E,B15003_023E,B15003_024E,B15003_025E",
        "for": "tract:" + l["tract_code"],
        "in": "state:" + l["state_code"] + "+county:" + l["county_code"]
    }

    base_ACS5 = "/2019/acs/acs5"
    base_url = "https://api.census.gov/data"

    response = requests.get(base_url + base_ACS5, params=params)

    census_data = response.json()

    a = census_data

    #print(",".join(a[0]))
    #print(",".join(a[1]))

    high_school = float(a[1][0]) + float(a[1][1])
    some_college = float(a[1][2]) + float(a[1][3]) + float(a[1][4])
    bachelors = float(a[1][5])
    graduates = float(a[1][6]) + float(a[1][7]) + float(a[1][8])

    total = high_school + some_college + bachelors + graduates

    high_school_per = some_college_per = bachelors_per = graduates_per = 0
    if total > 0:
        high_school_per = (100.0 * high_school) / total
        some_college_per = 100.0 * some_college / total
        bachelors_per = 100.0 * bachelors / total
        graduates_per = 100.0 * graduates / total

    education = {
        "high school": round(high_school_per, 2),
        "some college": round(some_college_per, 2),
        "bachelors": round(bachelors_per, 2),
        "graduates": round(graduates_per, 2)
    }

    return education


'''
Get the education level at a latitude/longitude in a census tract
Uses FCC API to first turn latitude/longitude into a FIPS code then calls census for that FIPS code
Census tracts contain between 2,500 to 8,000 people
'''
@app.route("/api/v1.0/education")
def education_level(latitude=None, longitude=None):

    #High school
    #B15003_017E + B15003_018E 

    #Some college
    #B15003_019E + B15003_020E  + B15003_021E 

    #Bachelors
    #B15003_022E

    #Graduate Degree
    #B15003_023E + B15003_024E  + B15003_025E 

    if 'lat' in request.args:
          latitude = float(request.args['lat'])
    else:
        return jsonify({
            "Status": "Error",
            "Message": "Missing parameter: latitude" 
        })

    if 'lon' in request.args:
        longitude = float(request.args['lon'])
    else:
        return jsonify({
            "Status": "Error",
            "Message": "Missing parameter: longitude" 
        })

    l = get_fips_information(latitude, longitude)

    levels = get_education_level(l)

    r = {
        "Status": "Ok",
        "education": levels
    }

    return jsonify(r)

def get_housing_units(l):
    # B25024_002E: 1 Detached
    # B02001_003E: 1 Attached
    # B25024_004E: 2
    # B25024_005E: 3 to 4
    # B25024_006E: 5 to 9
    # B25024_007E: 10 - 19
    # B25024_008E: 20 - 49
    # B25024_009E: 50 or more
    # B25024_010E: Mobile home
    # B25024_011E: Boat, RV, Van, etc

    params = {
        "key": CENSUS_API_KEY,
        "get": "B25024_002E,B25024_003E,B25024_004E,B25024_005E,B25024_006E,B25024_007E,B25024_008E,B25024_009E,B25024_010E,B25024_011E",
        "for": "tract:" + l["tract_code"],
        "in": "state:" + l["state_code"] + "+county:" + l["county_code"]
    }

    base_ACS5 = "/2019/acs/acs5"
    base_url = "https://api.census.gov/data"

    response = requests.get(base_url + base_ACS5, params=params)

    census_data = response.json()

    a = census_data

    total = 0
    for i in range(11):
        total += float(a[1][i])

    units = []
    if total > 0:
        units.append(100 * (float(a[1][0]) + float(a[1][1])) / total)

    for i in range(2, 11):
        if total > 0:
            units.append(round(100 * float(a[1][i]) / total), 2)
        else:
            units.append(0)

    housing = {
        "1": units[0],
        "2": units[1],
        "3 to 4": units[2],
        "5 to 9": units[3],
        "10 - 19": units[4],
        "20 - 49": units[5],
        "50 or more": units[6],
        "mobile home": units[7],
        "boat, RV, van, etc": units[8]
    }

    return housing

'''
Get the number of housing units at a structure at a latitude/longitude in a census tract
Uses FCC API to first turn latitude/longitude into a FIPS code then calls census for that FIPS code
Census tracts contain between 2,500 to 8,000 people
'''
@app.route("/api/v1.0/housing_units")
def housing_units():

    if 'lat' in request.args:
          latitude = float(request.args['lat'])
    else:
        return jsonify({
            "Status": "Error",
            "Message": "Missing parameter: latitude" 
        })

    if 'lon' in request.args:
        longitude = float(request.args['lon'])
    else:
        return jsonify({
            "Status": "Error",
            "Message": "Missing parameter: longitude" 
        })

    l = get_fips_information(latitude, longitude)

    units = get_housing_units(l)

    r = {
        "Status": "Ok",
        "units": units
    }

    return jsonify(r)


def get_insurance(l):

    with_insurance_male = "B27001_004E,B27001_007E,B27001_010E,B27001_013E,B27001_016E,B27001_019E,B27001_022E,B27001_025E,B27001_028E"
    with_insurance_female = "B27001_032E,B27001_035E,B27001_038E,B27001_041E,B27001_044E,B27001_047E,B27001_050E,B27001_053E,B27001_056E"

    totals = "B27001_001E"

    get_vars = f'{with_insurance_male},{with_insurance_female},{totals}'

    params = {
        "key": CENSUS_API_KEY,
        "get": get_vars,
        "for": "tract:" + l["tract_code"],
        "in": "state:" + l["state_code"] + "+county:" + l["county_code"]
    }

    base_ACS5 = "/2019/acs/acs5"
    base_url = "https://api.census.gov/data"

    response = requests.get(base_url + base_ACS5, params=params)

    census_data = response.json()

    a = census_data

    population = float(a[1][18])

    sum_with_insurance = 0
    for i in range(18):
        sum_with_insurance += float(a[1][i]) 

    if population > 0:
        per_with_insurance = round((100.0 * sum_with_insurance) / population, 2)
    else:
        per_with_insurance = 0.0


    #----------------------
    # Medicare
    with_medicare = "B27010_006E,B27010_012E,B27010_013E,B27010_022E,B27010_028E,B27010_029E,B27010_038E,B27010_039E,B27010_044E,B27010_045E,B27010_046E,B27010_055E,B27010_060E,B27010_061E,B27010_062E"

    totals = "B27010_001E"

    get_vars = f'{with_medicare},{totals}'

    params = {
        "key": CENSUS_API_KEY,
        "get": get_vars,
        "for": "tract:" + l["tract_code"],
        "in": "state:" + l["state_code"] + "+county:" + l["county_code"]
    }

    base_ACS5 = "/2019/acs/acs5"
    base_url = "https://api.census.gov/data"

    response = requests.get(base_url + base_ACS5, params=params)

    census_data = response.json()

    a = census_data

    cat_num = len(with_medicare.split(','))

    sum_with_medicare = 0
    for i in range(cat_num):
        sum_with_medicare += float(a[1][i]) 

    population = float(a[1][cat_num])

    if population > 0:
        per_with_medicare = round((100.0 * sum_with_medicare) / population, 2)
    else:
        per_with_medicare = 0.0


    #----------------------
    # Medicaid
    with_medicaid = "B27010_007E,B27010_013E,B27010_023E,B27010_029E,B27010_039E,B27010_046E,B27010_062E"

    totals = "B27010_001E"

    get_vars = f'{with_medicaid},{totals}'

    params = {
        "key": CENSUS_API_KEY,
        "get": get_vars,
        "for": "tract:" + l["tract_code"],
        "in": "state:" + l["state_code"] + "+county:" + l["county_code"]
    }

    base_ACS5 = "/2019/acs/acs5"
    base_url = "https://api.census.gov/data"

    response = requests.get(base_url + base_ACS5, params=params)

    census_data = response.json()

    a = census_data

    cat_num = len(with_medicaid.split(','))

    sum_with_medicaid = 0
    for i in range(cat_num):
        sum_with_medicaid += float(a[1][i]) 

    population = float(a[1][cat_num])

    if population > 0:
        per_with_medicaid = round((100.0 * sum_with_medicaid) / population, 2)
    else:
        per_with_medicaid = 0.0


    #----------------------
    # Tricare
    with_tricare = "B27010_008E,B27010_024E,B27010_040E,B27010_056E"

    totals = "B27010_001E"

    get_vars = f'{with_tricare},{totals}'

    params = {
        "key": CENSUS_API_KEY,
        "get": get_vars,
        "for": "tract:" + l["tract_code"],
        "in": "state:" + l["state_code"] + "+county:" + l["county_code"]
    }

    base_ACS5 = "/2019/acs/acs5"
    base_url = "https://api.census.gov/data"

    response = requests.get(base_url + base_ACS5, params=params)

    census_data = response.json()

    a = census_data

    cat_num = len(with_tricare.split(','))

    sum_with_tricare = 0
    for i in range(cat_num):
        sum_with_tricare += float(a[1][i]) 

    population = float(a[1][cat_num])

    if population > 0:
        per_with_tricare = round((100.0 * sum_with_tricare) / population, 2)
    else:
        per_with_tricare = 0.0

    ins = {
        "healthcare coverage": per_with_insurance,
        "medicare": per_with_medicare,
        "medicaid": per_with_medicaid,
        "tricare": per_with_tricare,
    }

    return ins


'''
Get the insurance coverage at a latitude/longitude in a census tract
Uses FCC API to first turn latitude/longitude into a FIPS code then calls census for that FIPS code
Census tracts contain between 2,500 to 8,000 people
'''
@app.route("/api/v1.0/insurance")
def insurance():

    if 'lat' in request.args:
          latitude = float(request.args['lat'])
    else:
        return jsonify({
            "Status": "Error",
            "Message": "Missing parameter: latitude" 
        })

    if 'lon' in request.args:
        longitude = float(request.args['lon'])
    else:
        return jsonify({
            "Status": "Error",
            "Message": "Missing parameter: longitude" 
        })

    l = get_fips_information(latitude, longitude)

    categories = get_insurance(l)

    r = {
        "Status": "Ok",
        "insurance": categories
    }

    return jsonify(r)


def get_gender(l):
  
    male = "B01001_002E"
    female = "B01001_026E"

    totals = "B01001_001E"

    get_vars = f'{male},{female},{totals}'

    params = {
        "key": CENSUS_API_KEY,
        "get": get_vars,
        "for": "tract:" + l["tract_code"],
        "in": "state:" + l["state_code"] + "+county:" + l["county_code"]
    }

    base_ACS5 = "/2019/acs/acs5"
    base_url = "https://api.census.gov/data"

    response = requests.get(base_url + base_ACS5, params=params)

    census_data = response.json()

    a = census_data

    population = float(a[1][2])

    if population > 0:
        per_male = round((100.0 * float(a[1][0])) / population, 2)
    else:
        per_male = 0.0

    if population > 0:
        per_female = round((100.0 * float(a[1][1])) / population, 2)
    else:
        per_female = 0.0

    gen = {
        "male": per_male,
        "female": per_female
    }

    return gen


'''
Get the gender at a latitude/longitude in a census tract
Uses FCC API to first turn latitude/longitude into a FIPS code then calls census for that FIPS code
Census tracts contain between 2,500 to 8,000 people
'''
@app.route("/api/v1.0/gender")
def gender():

    if 'lat' in request.args:
          latitude = float(request.args['lat'])
    else:
        return jsonify({
            "Status": "Error",
            "Message": "Missing parameter: latitude" 
        })

    if 'lon' in request.args:
        longitude = float(request.args['lon'])
    else:
        return jsonify({
            "Status": "Error",
            "Message": "Missing parameter: longitude" 
        })

    l = get_fips_information(latitude, longitude)

    categories = get_gender(l)

    r = {
        "Status": "Ok",
        "gender": categories
    }

    return jsonify(r)


def get_age(l):
  
    age_male   = "B01001_003E,B01001_004E,B01001_005E,B01001_006E,B01001_007E,B01001_008E,B01001_009E,B01001_010E,B01001_011E,B01001_012E,B01001_013E,B01001_014E,B01001_015E,B01001_016E,B01001_017E,B01001_018E,B01001_019E,B01001_020E,B01001_021E,B01001_022E,B01001_023E,B01001_024E,B01001_025E"
    age_female = "B01001_027E,B01001_028E,B01001_029E,B01001_030E,B01001_031E,B01001_032E,B01001_033E,B01001_034E,B01001_035E,B01001_036E,B01001_037E,B01001_038E,B01001_039E,B01001_040E,B01001_041E,B01001_042E,B01001_043E,B01001_044E,B01001_045E,B01001_046E,B01001_047E,B01001_048E,B01001_049E"

    totals = "B01001_001E"

    get_vars = f'{age_male},{age_female},{totals}'

    params = {
        "key": CENSUS_API_KEY,
        "get": get_vars,
        "for": "tract:" + l["tract_code"],
        "in": "state:" + l["state_code"] + "+county:" + l["county_code"]
    }

    base_ACS5 = "/2019/acs/acs5"
    base_url = "https://api.census.gov/data"

    response = requests.get(base_url + base_ACS5, params=params)

    census_data = response.json()

    a = census_data

    population = float(a[1][46])

    sum = 0
    sum += float(a[1][0]) * 2 
    sum += float(a[1][1]) * 7
    sum += float(a[1][2]) * 12
    sum += float(a[1][3]) * 16
    sum += float(a[1][4]) * 18.5
    sum += float(a[1][5]) * 20
    sum += float(a[1][6]) * 21
    sum += float(a[1][7]) * 23
    sum += float(a[1][8]) * 27
    sum += float(a[1][9]) * 32
    sum += float(a[1][10]) * 37
    sum += float(a[1][11]) * 42
    sum += float(a[1][12]) * 47
    sum += float(a[1][13]) * 52
    sum += float(a[1][14]) * 57
    sum += float(a[1][15]) * 60.5
    sum += float(a[1][16]) * 63
    sum += float(a[1][17]) * 65.5
    sum += float(a[1][18]) * 68
    sum += float(a[1][19]) * 72
    sum += float(a[1][20]) * 77
    sum += float(a[1][21]) * 82
    sum += float(a[1][22]) * 87

    sum += float(a[1][23]) * 2 
    sum += float(a[1][24]) * 7
    sum += float(a[1][25]) * 12
    sum += float(a[1][26]) * 16
    sum += float(a[1][27]) * 18.5
    sum += float(a[1][28]) * 20
    sum += float(a[1][29]) * 21
    sum += float(a[1][30]) * 23
    sum += float(a[1][31]) * 27
    sum += float(a[1][32]) * 32
    sum += float(a[1][33]) * 37
    sum += float(a[1][34]) * 42
    sum += float(a[1][35]) * 47
    sum += float(a[1][36]) * 52
    sum += float(a[1][37]) * 57
    sum += float(a[1][38]) * 60.5
    sum += float(a[1][39]) * 63
    sum += float(a[1][40]) * 65.5
    sum += float(a[1][41]) * 68
    sum += float(a[1][42]) * 72
    sum += float(a[1][43]) * 77
    sum += float(a[1][44]) * 82
    sum += float(a[1][45]) * 87

    if population > 0:
        age_avg = round(sum / population, 2)
    else:
        age_avg = 0.0

    a = {
        "age avg": age_avg,
    }

    return a


'''
Get the average age at a latitude/longitude in a census tract
Uses FCC API to first turn latitude/longitude into a FIPS code then calls census for that FIPS code
Census tracts contain between 2,500 to 8,000 people
'''
@app.route("/api/v1.0/age")
def age():

    if 'lat' in request.args:
          latitude = float(request.args['lat'])
    else:
        return jsonify({
            "Status": "Error",
            "Message": "Missing parameter: latitude" 
        })

    if 'lon' in request.args:
        longitude = float(request.args['lon'])
    else:
        return jsonify({
            "Status": "Error",
            "Message": "Missing parameter: longitude" 
        })

    l = get_fips_information(latitude, longitude)

    age = get_age(l)

    r = {
        "Status": "Ok",
        "age": age
    }

    return jsonify(r)


def get_diversity_index(l):
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

    base_ACS5 = "/2019/acs/acs5"
    base_url = "https://api.census.gov/data"

    response = requests.get(base_url + base_ACS5, params=params)

    census_data = response.json()

    a = census_data

    total = 0
    for i in range(9):
        total += float(a[1][i])

    homogeneity = 0
    for i in range(9):
        homogeneity += (float(a[1][i])/total)**2

    #print(",".join(a[0]))
    #print(",".join(a[1]))

    return 1 - homogeneity

'''
Get the diversity index at a latitude/longitude in a census tract, high scores close to 1 indicate higher diversity
Uses FCC API to first turn latitude/longitude into a FIPS code then calls census for that FIPS code
Census tracts contain between 2,500 to 8,000
'''
@app.route("/api/v1.0/diversity")
def diversity_index():

    if 'lat' in request.args:
          latitude = float(request.args['lat'])
    else:
        return jsonify({
            "Status": "Error",
            "Message": "Missing parameter: latitude" 
        })

    if 'lon' in request.args:
        longitude = float(request.args['lon'])
    else:
        return jsonify({
            "Status": "Error",
            "Message": "Missing parameter: longitude" 
        })


    l = get_fips_information(latitude, longitude)

    diversity = get_diversity_index(l)

    r = {
        "Status": "Ok",
        "diversity_index": diversity
    }

    return jsonify(r)


'''
Get a summary at a latitude/longitude in a census tract
Uses FCC API to first turn latitude/longitude into a FIPS code then calls census for that FIPS code
Census tracts contain between 2,500 to 8,000
'''
@app.route("/api/v1.0/summary")
def summary():

    if 'lat' in request.args:
        latitude = float(request.args['lat'])
    else:
        return jsonify({
            "Status": "Error",
            "Message": "Missing parameter: latitude" 
        })

    if 'lon' in request.args:
        longitude = float(request.args['lon'])
    else:
        return jsonify({
            "Status": "Error",
            "Message": "Missing parameter: longitude" 
        })


    l = get_fips_information(latitude, longitude)

    pov_rate = get_poverty_rate(l)
    pop_density = get_population_density(l)
    diversity = get_diversity_index(l)
    income = get_income(l)

    r = {
        "Status": "Ok",
        "diversity_index": diversity,
        "poverty_rate": pov_rate,
        "income": income,
        "population_density": pop_density
    }

    return jsonify(r)


if __name__ == '__main__':
    app.run(debug=True)
