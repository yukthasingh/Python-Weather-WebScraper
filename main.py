import requests

# This URL is used to convert a city name like "New York" into latitude and longitude.
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

# This URL is used to request the current weather once we know the coordinates.
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


# This function looks up a city name and returns its location data from Open-Meteo.
def get_coordinates(city):
    # These parameters tell the geocoding API what city to search for.
    params = {
        # Send the city name the user typed in.
        "name": city,
        # Only ask for the best single match instead of a long list of cities.
        "count": 1,
        # Request the response in English.
        "language": "en",
        # Ask the API to return JSON data.
        "format": "json",
    }

    # Send an HTTP GET request to the geocoding endpoint with a 10-second timeout.
    response = requests.get(GEOCODING_URL, params=params, timeout=10)
    # Stop with an error if the server returns a bad status code like 404 or 500.
    response.raise_for_status()

    # Convert the JSON response body into a Python dictionary.
    data = response.json()
    # Pull out the list of matching locations, or use an empty list if none exist.
    results = data.get("results", [])

    # If no city matches were found, return None so the caller knows it failed.
    if not results:
        return None

    # Return the first and best-matching city result.
    return results[0]


# This function gets the current temperature for a city name.
def get_weather(city):
    # First, translate the city name into geographic coordinates.
    location = get_coordinates(city)
    # If the city could not be found, stop here and return None.
    if not location:
        return None

    # These parameters tell the forecast API which place and weather field we want.
    params = {
        # Use the latitude from the geocoding result.
        "latitude": location["latitude"],
        # Use the longitude from the geocoding result.
        "longitude": location["longitude"],
        # Ask only for the current air temperature at 2 meters above ground.
        "current": "temperature_2m",
        # Request the temperature in Fahrenheit.
        "temperature_unit": "fahrenheit",
    }

    # Send an HTTP GET request to the forecast endpoint with the chosen parameters.
    response = requests.get(FORECAST_URL, params=params, timeout=10)
    # Raise an error if the forecast request was not successful.
    response.raise_for_status()

    # Convert the weather response from JSON into a Python dictionary.
    data = response.json()
    # Get the nested "current" weather section, or an empty dictionary if it is missing.
    current = data.get("current", {})
    # Read the current temperature value from the response.
    temperature = current.get("temperature_2m")

    # If the temperature field is missing, return None to signal failure.
    if temperature is None:
        return None

    # Return a small dictionary with the cleaned-up data we want to display.
    return {
        # Save the city name from the location result.
        "city": location["name"],
        # Save the country name if available, otherwise use an empty string.
        "country": location.get("country", ""),
        # Save the temperature number from the weather result.
        "temperature": temperature,
        # Save the temperature unit from the API, or use "deg F" as a safe fallback.
        "unit": data.get("current_units", {}).get("temperature_2m", "deg F"),
    }


# This is the main function that runs the user interaction for the program.
def main():
    # Ask the user for a city name and remove extra spaces from the start or end.
    user_input = input("Enter a city name to get the current weather: ").strip()

    # If the user pressed Enter without typing a city, show a message and stop.
    if not user_input:
        print("Please enter a city name.")
        return

    try:
        # Try to get the weather data for the city the user entered.
        weather = get_weather(user_input)
    except requests.RequestException:
        # If a network or HTTP error happens, show a friendly message instead of crashing.
        print("Could not retrieve weather data right now.")
        return

    # If no weather data was returned, the city likely was not found.
    if not weather:
        print(f'Could not find weather data for "{user_input.upper()}".')
        return

    # Start building the location label with the city name.
    location_label = weather["city"]
    # If a country exists, append it after the city for a clearer result.
    if weather["country"]:
        location_label = f'{location_label}, {weather["country"]}'

    # Print the final weather message in uppercase for the location name.
    print(
        f'The current temperature in {location_label.upper()} is: '
        f'{weather["temperature"]}{weather["unit"]}'
    )


# This makes sure main() only runs when this file is executed directly.
if __name__ == "__main__":
    # Start the program.
    main()
