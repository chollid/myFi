import math
import random
import csv 
import json
import turtle
import constants


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
def load_city_data(filepath="src/cities.csv"):
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
    # TODO: strengthen calculations for more accurate conversions
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
   screen.register_shape("src/travel_the_world.gif")
   screen.bgpic("src/travel_the_world.gif")

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
               save_game("save_game.json")
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

    handle_random_event()


def handle_currency_exchange():
    """Allows the player to exchange currency."""
    print("Currency Exchange:")
    print(f"Your current balance: {player_data['money']:.2f} {player_data['currency']}")
    print("Available currencies:")
    for currency in exchange_rates:
        if currency != player_data["currency"]:
            print(f"- {currency}")

    # TODO: check if there's a negative balance
    # TODO: don't allow exchange if not enough money
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

# handle a random event
def handle_random_event():
    """Handles random events that might occur during the game."""
    event_chance = random.randint(1, 2)  # 21% chance of event

    if event_chance == 1:
        event_type = random.choice(["fuel_loss", "fuel_gain", "money_loss", "money_gain", "shortcut"])
        if event_type == "fuel_loss":
            fuel_lost = random.randint(50, 200)
            player_data["fuel"] = max(0, player_data["fuel"] - fuel_lost)
            game_state["message"] = f"Oh no! You lost {fuel_lost} fuel due to an unexpected detour."
        elif event_type == "fuel_gain":
            fuel_gained = random.randint(50, 200)
            player_data["fuel"] += fuel_gained
            game_state["message"] = f"Lucky you! You found a shortcut and gained {fuel_gained} fuel."
        elif event_type == "money_loss":
            money_lost = random.randint(20, 100)
            player_data["money"] = max(0, player_data["money"] - money_lost)
            game_state["message"] = f"Bad luck! You lost {money_lost} {player_data['currency']} due to a scam."
        elif event_type == "money_gain":
            money_gained = random.randint(20, 100)
            player_data["money"] += money_gained
            game_state["message"] = f"Congratulations! You found {money_gained} {player_data['currency']} on the street."
        elif event_type == "shortcut":
            if len(cities_data) >= 2:
                # find two random cities other than the current one
                city1, city2 = random.sample([city for city in cities_data if city != player_data["current_city"]], 2)

                # calc original and shortcut distances
                original_distance = haversine(float(player_data["current_city"]["latitude"]), float(player_data["current_city"]["longitude"]), float(city1["latitude"]), float(city1["longitude"])) + \
                                    haversine(float(city1["latitude"]), float(city1["longitude"]), float(city2["latitude"]), float(city2["longitude"]))
                shortcut_distance = haversine(float(player_data["current_city"]["latitude"]), float(player_data["current_city"]["longitude"]), float(city2["latitude"]), float(city2["longitude"]))

                # if it saves distance, apply shortcut
                if shortcut_distance < original_distance:
                    fuel_saved = original_distance - shortcut_distance
                    player_data["fuel"] += fuel_saved
                    game_state["message"] = f"Amazing! You discovered a shortcut from {player_data['current_city']['city']} to {city2['city']} via {city1['city']} and saved {fuel_saved:.0f} fuel."
                else:
                    game_state["message"] = f"You tried to find a shortcut between {player_data['current_city']['city']}, {city1['city']}, and {city2['city']}, but it wasn't shorter."
            else:
                game_state["message"] = "Not enough cities to find a shortcut."

        print(game_state["message"])


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
while True:  # allow restarted
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

    # Play again logic
    play_again = input("Do you want to play again? (y/n): ")
    if play_again.lower() == 'y':
        # reseet game state and player data
        game_state["game_over"] = False
        game_state["message"] = ""
        player_data["current_city"] = random.choice(cities_data)
        player_data["fuel"] = constants.STARTING_FUEL
        player_data["cities_visited"] = [player_data["current_city"]["city"]]
        player_data["score"] = 1
        player_data["money"] = 1000
        player_data["currency"] = "USD"

        print(f"\nNew game started! You are in {player_data['current_city']['city']}.")
    else:
        break  # exit game

turtle.mainloop()