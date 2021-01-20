from flask import Flask, render_template, jsonify, request, url_for
import os
import requests

app = Flask(__name__)

geocoding_api_key = os.environ.get('WEATHERLY_GEOCODING_API_KEY')

def generate_weather_url(longitude, latitude, hourly=False):
    return f'https://api.weather.gov/points/{longitude},{latitude}/forecast{"/hourly"if hourly else""}'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weatherdata')
def weatherdata():

    address = request.args.get('address')

    geocoded = requests.get(
        f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={geocoding_api_key}'
    ).json()['results'][0]
    
    location       = geocoded['geometry']['location']
    address_string = geocoded['formatted_address']

    request_url = generate_weather_url(
        location['lat'],
        location['lng'])

    print(request_url)

    forecast = requests.get(request_url).json()['properties']['periods']

    forecast_data = forecast[0:15]

    return render_template('weatherdata.html',
        forecast=forecast,
        address=address_string,
        data=forecast_data,
        geocoords=f'{location["lat"]},{location["lng"]}')

@app.route('/weatherdata/day')
def specific_day():
    
    date   = request.args.get('day')
    coords = request.args.get('address_string')

    if request.args.get('address'):
        address_string = 'in ' + requests.get(
            f'https://maps.googleapis.com/maps/api/geocode/json?address={request.args["address"]}&key={geocoding_api_key}'
        ).json()['results'][0]['formatted_address']
    
    else:
        address_string = ''

    date_arr = date.split('-')

    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    
    day   = date_arr[2]
    month = months[int(date_arr[1]) -1]
    year  = date_arr[0]

    date_string = f'{month} {day}, {year}'

    coords.replace(' ', '')
    coords = coords.split(',')

    request_url = generate_weather_url(
        coords[0],
        coords[1],
        hourly=True)

    forecast_request = requests.get(request_url).json()['properties']['periods']

    
    forecast = [x for x in forecast_request if x['startTime'].split('T')[0]==date]

    return render_template('hourly.html', forecast=forecast, date_string=date_string, address_string=address_string)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)