import requests
import RPi.GPIO as GPIO
import time
from statistics import mean, stdev
from xml.etree import ElementTree

LATITUDE = "58.9353"
LONGITUDE = "5.6895"

GPIO.setmode(GPIO.BOARD)
GPIO.setup(1, GPIO.OUT)
GPIO.setup(2, GPIO.OUT)
GPIO.setup(3, GPIO.OUT)

def get_weather_data(lat, lon):
    url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Error fetching weather data")
    return response.json()

def update_leds(weather_data):
    next_hour = weather_data["properties"]["timeseries"][0]
    details = next_hour["data"]["next_1_hours"]["details"]
    rain_mm = details["precipitation_amount"]
    temp = details["air_temperature"]

    # Calculate mean and standard deviation for the current date
    temp_data = [temp]  # Add more historical temperature data for the current date
    temp_mean = mean(temp_data)
    temp_sd = stdev(temp_data)

    # Check if it's raining
    if rain_mm > 0:
        GPIO.output(1, GPIO.HIGH)
    else:
        GPIO.output(1, GPIO.LOW)

    # Check temperature mean +/- 1 SD
    if temp < temp_mean - temp_sd:
        GPIO.output(2, GPIO.HIGH)
        GPIO.output(3, GPIO.LOW)
    elif temp > temp_mean + temp_sd:
        GPIO.output(2, GPIO.LOW)
        GPIO.output(3, GPIO.HIGH)
    else:
        GPIO.output(2, GPIO.HIGH)
        GPIO.output(3, GPIO.HIGH)

try:
    while True:
        weather_data = get_weather_data(LATITUDE, LONGITUDE)
        update_leds(weather_data)
        time.sleep(3600)  # Update hourly
finally:
    GPIO.cleanup()
