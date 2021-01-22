import os, requests

geocoding_api_key        = os.environ.get('WEATHERLY_GEOCODING_API_KEY')
geocoding_string_api_key = os.environ.get('WEATHERLY_GEOCODING_STRING_API_KEY')

def geocoding(location):
    geocode = {}
    geocoding_request_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={geocoding_api_key}'
    geocoded = requests.get(
        geocoding_request_url
    ).json()['results'][0]

    coords = f'{geocoded["geometry"]["location"]["lat"]},{geocoded["geometry"]["location"]["lng"]}'

    geocode['string'] = geocoded['formatted_address']
    ac = geocoded['address_components']
    for i in range(len(ac)):
        if 'locality' in ac[i]['types']:
            geocode['string'] = ac[i].get('short_name')
            break

    if geocode['string'] == geocoded['formatted_address']:
        for i in range(len(ac)):
            if 'address_level2' in ac[i]['types']:
                geocode['string'] = ac[i].get('short_name')
                break

    geocode['coords'] = coords

    return geocode

if __name__ == '__main__':
    print(geocoding('40.7128,-74.0060'))