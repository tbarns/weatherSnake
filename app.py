from flask import Flask, render_template, session, request, jsonify, redirect, url_for
import requests
import os
from dotenv import load_dotenv
from flask_cors import CORS
from datetime import datetime


# Load environment variables from .env file
load_dotenv()

# Access the environment variable
api_key = os.getenv("WEATHER_API_KEY")
app_secret_key = os.getenv("SECRET_KEY")
app = Flask(__name__)
app.secret_key = app_secret_key 
CORS(app)

def get_day_from_timestamp(timestamp):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return days[datetime.utcfromtimestamp(timestamp).weekday()]

def capitalize_words(city_name):
    return " ".join(word.capitalize() for word in city_name.split())
@app.route('/loading')
def loading():
    time.sleep(2)  # Sleep for 2 seconds to simulate loading
    return redirect(url_for('main'))
@app.route('/')
def index():
    history = session.get('history', [])
    return render_template('index.html', history=history, weather_data=[])

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        city = request.form.get('location')
    else:
        city = request.args.get('location')

    if not city:
        return redirect(url_for('index'))
    city = capitalize_words(city)
  
    history = session.get('history', [])
    if city not in history:
        history.append(city)
        session['history'] = history

    weather_data = fetch_weather_for_city(city)
    return render_template('index.html', history=history, weather_data=weather_data, city_name=city)

@app.route('/clear-history')
def clear_history():
    session['history'] = []
    return redirect(url_for('index'))

def fetch_weather_for_city(city):
    endpoint = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(endpoint)
    if response.status_code == 200:
        data = response.json()
        lat, lon = data['coord']['lat'], data['coord']['lon']
        return get_five_day_forecast(lat, lon)
    else:
        return []

@app.route('/getweather', methods=['POST'])
def get_weather():  # Renamed the function here
    city = request.form.get('location')
    if not city:
        return jsonify({"error": "Please provide a city name"}), 400
    city = capitalize_words(city)
  
    history = session.get('history', [])
    if city not in history:
        history.append(city)
        session['history'] = history

    endpoint = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(endpoint)
    if response.status_code == 200:
        data = response.json()
        lat, lon = data['coord']['lat'], data['coord']['lon']
        five_day_data = get_five_day_forecast(lat, lon)
        return jsonify(five_day_data)
    else:
        return jsonify({"error": "Failed to fetch weather data"}), 400

def get_five_day_forecast(lat, lon):
    endpoint = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=imperial&appid={api_key}"
    response = requests.get(endpoint)
    data = response.json()

    days_data = []
    day_names = ["Today", "Day 2", "Day 3", "Day 4", "Day 5"]
    for index in range(5):
        day_data = data['list'][index * 8]
        day_name = day_names[index] if index < len(day_names) else get_day_from_timestamp(day_data['dt'])
        days_data.append({
            "day": day_name,
            "temp": day_data['main']['temp'],
            "humidity": day_data['main']['humidity'],
            "wind_speed": day_data['wind']['speed'],
            "icon_url": f"https://openweathermap.org/img/w/{day_data['weather'][0]['icon']}.png"
        })
    return days_data

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
