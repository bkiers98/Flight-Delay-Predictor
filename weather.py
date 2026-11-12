import json
import requests

def get_weather_code(code):
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snowfall",
        73: "Moderate snowfall",
        75: "Heavy snowfall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        97: "Heavy thunderstorm",
        99: "Thunderstorm with heavy hail"
    }

    return weather_codes[code]

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
        weather['weather_code'] = get_weather_code(current['weather_code'])
        weather['precipitation'] = current['precipitation']
        weather['snowfall'] = current['snowfall']
        weather['rain'] = current['rain']
        weather['showers'] = current['showers']
        weather['wind_gusts'] = current['wind_gusts_10m']
        return weather
    else:
        return weather
    