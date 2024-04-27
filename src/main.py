import math
import random
import csv 
import json
import turtle
import constants 


print(constants.SCREEN_HEIGHT)
#loaded from cities.csv)
cities_data = []

# player data
player_data = {
    "current_city": None,
    "fuel": constants.STARTING_FUEL,
    "cities_visited": [],
    "score": 0,
    "currency" : "USD",
    "money" : 1000
}

# exchange rates - based USD
exchange_rates = {
    "USD": 1.0,
    "EUR": 0.85,
    "JPY": 110.0,
    "GBP": 0.73,
    "AUD": 1.30,
    "INR": 74.00,
    "CNY": 6.45,
    "RUB": 73.50,
    "BRL": 5.40,
    "ZAR": 14.50
}

# game state
game_state = {
    "game_over": False,
    "message": ""
}

### load city data
def load_city_data(filepath="cities.csv"):
    """Loads city data from the csv file"""
    global cities_data
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                cities_data.append(row)
    except FileNotFoundError:
        print(f"{filepath}' not found!")
        game_state["game_over"] = True
        game_state["message"] = "city data not found!"

####currency conversion
def convert_currency(amount, from_currency, to_currency):
    """Converts an amount from one currency to another"""
    if from_currency == to_currency:
        return amount
    if from_currency != "USD":
        amount = amount / exchange_rates[from_currency] # mustw first convert to USD

    return amount * exchange_rates[to_currency]

### Haversine
def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (decimal degrees)
    """
    # converts lat and long from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # diff in coords
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    # haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # calculate the distance
    distance = constants.EARTH_RADIUS * c
    return distance



## start up turtle graphics here
# screen
# screen width
# coords ot match long ant lat
# need background
# pen - start
# set speed
# return these


###init the game 
## load data here
# check for game loop being over 
# find start city
# where they've visited
# award points

## init game


## init turtle graphs


#### show nearby cities
# show current? 
# list of nearby cities

## check the next city is not current city
##sort ascending
## grab distance bewteen both cities
##check fuel amount is sufficient

##show them all
