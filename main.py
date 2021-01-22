from flask import Flask, render_template, jsonify, request, url_for, redirect, flash, session
import os
import requests
import json
from geocoding import geocoding

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
    # using_current_location = int(bool(request.args.get('CURRENT_LOCATION')))
    location = request.args.get('location')
    original_location = location

    geocode = geocoding(location)

    request_url = generate_weather_url(geocode['coords'])
    print(request_url)
    forecast_request_tries = 0
    max_forecast_request_tries = 10

    try:
        forecast = requests.get(request_url).json()
        forecast = forecast.get('properties')

    except json.decoder.JSONDecodeError:
        return redirect(url_for('weatherdata', **request.args))

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
        address=geocode['string'],
        data=forecast_data,
        location=location,
        link_location=original_location
    )

@app.route('/weatherdata/specific/<date>/<location>')
def specific_day(date, location):

    date_arr = date.split('-')

    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    
    day   = date_arr[2]
    month = months[int(date_arr[1]) -1]
    year  = date_arr[0]

    date_string = f'{month} {day}, {year}'

    geocode = geocoding(location)

    request_url = generate_weather_url(geocode['coords'], hourly=True)
    
    try:
        forecast_request = requests.get(request_url).json()
        forecast_request = forecast_request.get('properties')

    except json.decoder.JSONDecodeError:
        return redirect(url_for('weatherdata', date=date, location=location))

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
        coords=geocode['coords'],
        forecast=forecast,
        date_string=date_string,
        link_location=location,
        address_string=geocode['string'],
        dont_show_night=session.get('DONT_SHOW_NIGHT')
        )

@app.route('/night/<date>/<location>')
def night(date, location):
    session['DONT_SHOW_NIGHT'] = not session.get('DONT_SHOW_NIGHT')

    return redirect(url_for('specific_day', date=date, location=location))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)