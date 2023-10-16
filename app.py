from flask import Flask, render_template, session, request, jsonify, redirect, url_for
import requests
import os
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables from .env file
load_dotenv()

# Access the environment variable
api_key = os.getenv("WEATHER_API_KEY")
app_secret_key = os.getenv("SECRET_KEY")
app = Flask(__name__)
app.secret_key = app_secret_key 
CORS(app)

# Equivalent of the capitalizeWords function in JS
def capitalize_words(city_name):
    return " ".join(word.capitalize() for word in city_name.split())

@app.route('/')
def index():
    # Get the history of searches from a session variable (a Pythonic way to handle user sessions with Flask)
    history = session.get('history', [])
    return render_template('index.html', history=history)

@app.route('/getweather', methods=['POST'])
def search():
    print(request.form) 
    city = request.form.get('location')
    if not city:
        return jsonify({"error": "Please provide a city name"}), 400
    city = capitalize_words(city)
    # Update the session variable
    history = session.get('history', [])
    if city not in history:
        history.append(city)
        session['history'] = history

    # Fetching weather data, equivalent to your getCity function in JS
    endpoint = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(endpoint)
    if response.status_code == 200:
        data = response.json()
        lat, lon = data['coord']['lat'], data['coord']['lon']
        
        # Get the 5-day forecast
        five_day_data = get_five_day_forecast(lat, lon)
        return jsonify(five_day_data)
    else:
        print(response.content)  # This will print the reason for the failure
        return jsonify({"error": "Failed to fetch weather data"}), 400

def get_five_day_forecast(lat, lon):
    endpoint = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=imperial&appid={api_key}"
    response = requests.get(endpoint)
    data = response.json()

    # Extract data for the next 5 days (you might need to modify this based on the actual structure of the response)
    days_data = []
    for index in range(5):
        day_data = data['list'][index * 8]
        days_data.append({
            "temp": day_data['main']['temp'],
            "humidity": day_data['main']['humidity'],
            "wind_speed": day_data['wind']['speed'],
            "icon_url": f"https://openweathermap.org/img/w/{day_data['weather'][0]['icon']}.png"
        })
    return days_data

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
