from flask import Flask, render_template, jsonify, request, url_for, redirect, flash, session
import os
import requests
import json

app = Flask(__name__)
app.secret_key = 'test'

geocoding_api_key = os.environ.get('WEATHERLY_GEOCODING_API_KEY')

def generate_weather_url(location, hourly=False):
    if type(location) == list:
        return f'https://api.weather.gov/points/{location[0]},{location[1]}/forecast{"/hourly"if hourly else""}'
    
    elif type(location) == dict:
        return f'https://api.weather.gov/points/{location["lat"]},{location["lng"]}/forecast{"/hourly"if hourly else""}'
    return f'https://api.weather.gov/points/{location}/forecast{"/hourly"if hourly else""}'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weatherdata')
def weatherdata():

    location = request.args.get('location')

    geocoded = requests.get(
        f'https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={geocoding_api_key}'
    ).json()['results'][0]
    
    location       = geocoded['geometry']['location']
    address_string = geocoded['formatted_address']

    request_url = generate_weather_url(
        [location["lat"],
        location["lng"]])

    forecast_request_tries = 0
    max_forecast_request_tries = 10
    forecast = requests.get(request_url).json().get('properties')
    if forecast: forecast = forecast.get('periods')
    while not forecast:
        forecast = requests.get(request_url).json().get('properties')
        if forecast: forecast = forecast.get('periods')
        forecast_request_tries += 1
        if forecast_request_tries >= max_forecast_request_tries:
            flash('Something went wrong.')
            return redirect(url_for('index', **request.args))

    forecast_data = forecast[0:15]

    return render_template('weatherdata.html',
        forecast=forecast,
        address=address_string,
        data=forecast_data,
        location=location)

@app.route('/weatherdata/specific/<date>/<location>')
def specific_day(date, location):

    date_arr = date.split('-')

    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    
    day   = date_arr[2]
    month = months[int(date_arr[1]) -1]
    year  = date_arr[0]

    date_string = f'{month} {day}, {year}'

    geocoding_request = requests.get(
        f'https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={geocoding_api_key}'
    ).json()['results'][0]

    address_string = geocoding_request['formatted_address']

    coords = geocoding_request["geometry"]["location"]

    premise = False
    if 'premise' in geocoding_request['types']:
        premise = True

    request_url = generate_weather_url(coords, hourly=True)
    
    forecast_request = requests.get(request_url).json().get('properties')
    if forecast_request: forecast_request = forecast_request.get('periods')
    forecast_request_tries = 0
    max_forecast_request_tries = 10
    while not forecast_request:
        forecast_request = requests.get(request_url).json().get('properties')
        if forecast_request: forecast_request = forecast_request.get('periods')
        forecast_request_tries += 1
        if forecast_request_tries >= max_forecast_request_tries:
            flash('Something went wrong.')
            print(requests.get(request_url).json())
            return redirect(url_for('index'))

    if session.get('DONT_SHOW_NIGHT'):
        forecast = [x for x in forecast_request if x['startTime'].split('T')[0]==date and x['isDaytime']==True]
    else:
        forecast = [x for x in forecast_request if x['startTime'].split('T')[0]==date]
    return render_template('hourly.html',
        date=date,
        location=location,
        coords=coords,
        forecast=forecast,
        date_string=date_string,
        address_string=address_string,
        premise=premise,
        dont_show_night=session.get('DONT_SHOW_NIGHT'))

@app.route('/night/<date>/<location>')
def night(date, location):
    session['DONT_SHOW_NIGHT'] = not session.get('DONT_SHOW_NIGHT')

    return redirect(url_for('specific_day', date=date, location=location))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)