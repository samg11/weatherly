from flask import Blueprint, redirect, url_for, request

current_location = Blueprint('current_location', __name__)

@current_location.route('/<lat>/<lng>')
def location(lat, lng):
    request.args = {}
    using_current_location = True
    location = f'{lat},{lng}'
    return redirect(url_for('weatherdata',
        location=location,
        using_current_location=using_current_location))