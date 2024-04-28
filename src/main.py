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

# travel cost
def calculate_travel_cost_money(distance):
   """Calculates the monetary cost of travel - if any."""
   # for now, it's distance based cost - can be more complex later
   base_cost = 50  # base cost for any travel
   cost_per_km = 0.1  # vost per kilometer
   total_cost = base_cost + distance * cost_per_km
   return total_cost


def handle_player_choice(nearby_cities):
   """Handles the player's choice for travel, currency exchange, or other actions."""
   while True:
       try:
           choice = input("Enter your choice (number), 'x' to exchange currency, 's' to save, or 'q' to quit: ")
           if choice.lower() == 'q':
               game_state["game_over"] = True
               return
           elif choice.lower() == "x":
               handle_currency_exchange()
               return  # return main game loop after currency exchange
           elif choice.lower() == "s":
               ## TODO save_game()
               print("Game saved!")
           elif int(choice) >= 1 and int(choice) <= len(nearby_cities):
               chosen_city, distance = nearby_cities[int(choice) - 1]
               travel_to_city(chosen_city, distance)
               return  # return to main game loop after traveling
           else:
               print("Invalid choice. Please enter a valid number or 'x', 's', or 'q'.")
       except ValueError:
           print("Invalid input. Please enter a number, 'x', 's', or 'q'.")
           
     
# travel to a city      
def travel_to_city(new_city, distance):
    """Updates the game state when the player travels to a new city."""
    fuel_cost = distance * constants.FUEL_CONSUMPTION_RATE
    money_cost = calculate_travel_cost_money(distance)

    player_data["fuel"] -= fuel_cost
    player_data["money"] -= money_cost
    player_data["current_city"] = new_city
    player_data["cities_visited"].append(new_city["city"])
    player_data["score"] += 1

    game_state["message"] = f"You traveled to {new_city['city']} ({new_city['country']})."
    print(game_state["message"])

    # Handle currency change if visiting a city in a different country
    if new_city["country"] != player_data["current_city"]["country"]:
        player_data["currency"] = get_currency_for_country(new_city["country"])
        print(f"You are now using {player_data['currency']} as currency.")

    ## TODO: create a random event
    

def handle_currency_exchange():
    """Allows the player to exchange currency."""
    print("Currency Exchange:")
    print(f"Your current balance: {player_data['money']:.2f} {player_data['currency']}")
    print("Available currencies:")
    for currency in exchange_rates:
        if currency != player_data["currency"]:
            print(f"- {currency}")

    while True:
        target_currency = input(
            f"Enter the currency you want to exchange to (or 'b' to go back): "
        ).upper()

        if target_currency == "B":
            return
        elif target_currency not in exchange_rates:
            print("Invalid currency. Please choose from the available currencies.")
        else:
            break

    while True:
        try:
            amount_str = input(
                f"Enter the amount of {player_data['currency']} you want to exchange (or 'b' to go back): "
            )
            if amount_str.lower() == "b":
                return

            amount = float(amount_str)
            if amount <= 0:
                print("Please enter a positive amount.")
            else:
                break
        except ValueError:
            print("Invalid. Please enter a number.")

    # perform exchange
    converted_amount = convert_currency(
        amount, player_data["currency"], target_currency
    )

    player_data["money"] -= amount
    player_data["money"] += converted_amount
    player_data["currency"] = target_currency

    print(
        f"You exchanged {amount:.2f} {player_data['currency']} for {converted_amount:.2f} {target_currency}."
    )
    print(f"Your new balance: {player_data['money']:.2f} {player_data['currency']}")
    
    
# get currency for specific country 
def get_currency_for_country(country):
    """Returns the currency used in a given country"""
    if country in ["USA"]:
        return "USD"
    elif country in ["UK"]:
        return "GBP"
    elif country in ["Japan"]:
        return "JPY"
    elif country in ["Australia"]:
        return "AUD"
    elif country in ["India"]:
        return "INR"
    elif country in ["China"]:
        return "CNY"
    elif country in ["Russia"]:
        return "RUB"
    elif country in ["Brazil"]:
        return "BRL"
    elif country in ["South Africa"]:
        return "ZAR"
    elif country in ["France", "Germany", "Spain", "Italy", "Netherlands", "Belgium", "Portugal", "Greece", "Austria", "Finland", "Ireland"]:
        return "EUR"
    else:
        return "USD"  # Default to USD if not found


# save game
def save_game(filename):
    """Saves the current game state to a JSON file."""
    with open(filename, 'w') as f:
        json.dump({
            "player_data": player_data,
            "game_state": game_state
        }, f)
    print("Game saved successfully!")
        
def load_game(filename):
    """Loads the game state from a JSON file."""
    global player_data, game_state
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            player_data = data["player_data"]
            game_state = data["game_state"]
        print("Game loaded successfully!")
    except FileNotFoundError:
        print("Save file not found.")
        
        
# main game loop
while not game_state["game_over"]:
    print("\n---")
    nearby_cities = display_nearby_cities()
    if not nearby_cities:
        print("You are stranded! No cities within reach.")
        game_state["game_over"] = True
        break
    handle_player_choice(nearby_cities)

    if player_data["fuel"] <= 0:
        game_state["game_over"] = True
        game_state["message"] = "Game over! You ran out of fuel."

print(game_state["message"])