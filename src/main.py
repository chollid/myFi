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


### initialize turtle graphics
def initialize_turtle():
   """Sets up turtle graphics screen and pen"""
   screen = turtle.Screen()
   screen.setup(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
   screen.setworldcoordinates(-180, -90, 180, 90)  #set coordinates to match longitude and latitude
   screen.bgpic("world_map.gif")

   pen = turtle.Turtle()
   pen.hideturtle()
   pen.penup()
   pen.speed(0)  # sets speed to fastest

   return screen, pen

###initialize game

def initialize_game():
   """Inits game state."""
   load_city_data()

   if not game_state["game_over"]:
       # start random city
       start_city = random.choice(cities_data)
       player_data["current_city"] = start_city
       player_data["cities_visited"].append(start_city["city"])
       player_data["score"] += 1 # award points for starting


       game_state["message"] = f"Welcome to Travel the World! You start in {start_city['city']}."
       print(game_state["message"])


initialize_game()

#init turtle graphics
if not game_state["game_over"]:
   screen, pen = initialize_turtle()


turtle.mainloop()


def display_nearby_cities():
   """Displays a list of nearby cities player can travel to."""
   current_city = player_data["current_city"]
   nearby_cities = []


   for city in cities_data:
       if city["city"] != current_city["city"]:
           distance = haversine(
               float(current_city["latitude"]),
               float(current_city["longitude"]),
               float(city["latitude"]),
               float(city["longitude"])
           )
           if distance <= player_data["fuel"]:  # we will onyl consider cities within fuel range
               nearby_cities.append((city, distance))


   # sort by distance (asc)
   nearby_cities.sort(key=lambda x: x[1])


   print("Nearby cities:")
   for i, (city, distance) in enumerate(nearby_cities):
       travel_cost = distance * constants.FUEL_CONSUMPTION_RATE  # calculate travel cost
       print(
           f"{i + 1}. {city['city']} ({city['country']}) - {distance:.0f} km away"
           f" (Cost: {travel_cost:.0f} fuel)"
       )

   return nearby_cities


### calc travel costs
# base
#cost per km
#total cost = base + disatnce + cost per km


### handle player's choice of which city to visit
##grab choice for 
## loop through: 
    ## - save - quit - or number of city to visit
        ## if chooses valid city: 
            ## run travel_to_city function (TOD0)
            
            
#### travel to nearby city
## account for fuel spent at some rate
##account for money spent at some distance
#set new city if above calculations agree
## increment cities visited
# increment score
##update some game state
## may want to handle currency change if in different country 
## may add random event inside of city that decrements cash on hand