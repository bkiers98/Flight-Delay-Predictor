import json
import requests

def get_weather(airport):
    lat = airport.at[0, 'latitude_deg']
    long = airport.at[0, 'longitude_deg']
    weather = {'latitude': lat,
               'longitude': long}
    res = requests.get('https://api.open-meteo.com/v1/forecast?latitude=' + str(lat) + '&longitude=' + str(long) + '&current=temperature_2m,precipitation,rain,showers,snowfall,weather_code,wind_gusts_10m&wind_speed_unit=mph&temperature_unit=fahrenheit&precipitation_unit=inch')
    if res.status_code == 200:
        j = json.loads(res.text)
        current = j['current']
        weather['temperature'] = current['temperature_2m']
        weather['weather_code'] = current['weather_code']
        weather['precipitation'] = current['precipitation']
        weather['snowfall'] = current['snowfall']
        weather['rain'] = current['rain']
        weather['showers'] = current['showers']
        weather['wind_gusts'] = current['wind_gusts_10m']
        return weather
    else:
        return weather
    