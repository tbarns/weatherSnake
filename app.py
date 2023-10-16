from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

WEATHER_API_URL = "YOUR_API_ENDPOINT_HERE"
WEATHER_API_KEY = "YOUR_API_KEY_HERE"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/getweather', methods=['POST'])
def get_weather():
    location = request.form.get('location')
    response = requests.get(WEATHER_API_URL, params={
        'q': location,
        'days': 5,  # adjust if your API supports this parameter
        'apikey': WEATHER_API_KEY
    })
    data = response.json()
    # process and return the data as needed
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
