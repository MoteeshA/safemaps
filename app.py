from flask import Flask, render_template, request
import googlemaps
import requests

app = Flask(__name__)

# Replace with your actual Google Maps API key
GOOGLE_MAPS_API_KEY = "AIzaSyCTLKM1PdC2jaJEdMuuMq383I7XLB4QNWE"
WEATHER_API_KEY = "26789c50159d292a76c28eef3e7e68f5"  # Your OpenWeatherMap API key

# Initialize Google Maps client
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)


def get_route_with_traffic(start, end):
    try:
        # Get geocodes for both locations (start and end)
        start_location = gmaps.geocode(start)
        end_location = gmaps.geocode(end)

        if not start_location or not end_location:
            raise ValueError("One or both locations could not be found.")

        # Get directions with traffic information (departure_time="now")
        directions = gmaps.directions(start, end, mode="driving", departure_time="now")
        return directions
    except googlemaps.exceptions.ApiError as e:
        raise ValueError(f"Google Maps API error: {e}")


def get_alternative_route(start, end):
    try:
        # Fetch an alternative route with some waypoints (modify as needed)
        alternative_route = gmaps.directions(
            start,
            end,
            mode="driving",
            waypoints=[start],  # Modify this as needed to create alternative routes
            departure_time="now"
        )
        return alternative_route
    except googlemaps.exceptions.ApiError as e:
        raise ValueError(f"Google Maps API error: {e}")


def get_weather(location):
    try:
        # Geocode the location to get its latitude and longitude
        geocode = gmaps.geocode(location)
        if not geocode:
            raise ValueError(f"Could not find weather for location: {location}")

        lat = geocode[0]['geometry']['location']['lat']
        lng = geocode[0]['geometry']['location']['lng']

        # Make the weather API request to OpenWeatherMap
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(weather_url)
        weather_data = response.json()

        if weather_data.get("cod") != 200:
            raise ValueError(f"Error fetching weather data: {weather_data.get('message')}")

        # Extract relevant weather data
        weather_info = {
            "temperature": weather_data["main"]["temp"],
            "description": weather_data["weather"][0]["description"],
            "city": weather_data["name"],
            "country": weather_data["sys"]["country"]
        }
        return weather_info
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Weather API error: {e}")
    except Exception as e:
        raise ValueError(f"Error fetching weather data: {e}")


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/get_route', methods=['POST'])
def get_route():
    start = request.form['start']
    end = request.form['end']

    try:
        # Fetch route directions with traffic data
        route = get_route_with_traffic(start, end)

        # Fetch an alternative route (green line)
        alternative_route = get_alternative_route(start, end)

        # Fetch weather for both start and end locations
        start_weather = get_weather(start)
        end_weather = get_weather(end)

        # Return the map with the route, alternative route, and weather info
        return render_template('map.html',
                               route=route,
                               alternative_route=alternative_route,
                               start_weather=start_weather,
                               end_weather=end_weather)

    except ValueError as e:
        return f"Location or weather error: {e}", 400
    except Exception as e:
        return f"An unexpected error occurred: {e}", 500


if __name__ == '__main__':
    app.run(debug=True)
