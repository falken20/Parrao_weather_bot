# by Richi Rod AKA @richionline / falken20

import os
import tweepy
import logging
import sys
from dotenv import load_dotenv, find_dotenv
from datetime import datetime, timedelta
import pytz  # Work with time zones

import requests
import json

from models import Weather


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load env file
load_dotenv(find_dotenv())
# load_dotenv(os.path.join(BASE_DIR, '.env'), override=True)

# Set log level and secret key
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'ERROR'))
SECRET_KEY = os.getenv('SECRET_KEY', default='xsd--ammmss!!"kd(sss')

# Credentials for twitter API
CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')

# Weather station API data
STATION_ID = os.environ.get('STATION_ID')
API_KEY = os.environ.get('API_KEY')
URL_WEATHER = f"https://api.weather.com/v2/pws/observations/current?stationId={STATION_ID}" \
    f"&format=json&units=m&numericPrecision=decimal" \
    f"&apiKey={API_KEY}"
URL_WEATHER_DAILY = f"https://api.weather.com/v2/pws/history/daily?stationId={STATION_ID}" \
    f"&format=json&units=m&numericPrecision=decimal" \
    f"&apiKey={API_KEY}" \
    f"&date="
SOURCE = "Falken weather station"


def get_auth():
    """Get user credentials in Twitter"""
    logging.info(f'{os.getenv("ID_LOG", "")} Getting Twitter credentials...')

    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )

    return client


def get_api_data(url=URL_WEATHER):
    """ Process to get current weather data  """
    logging.info(f'{os.getenv("ID_LOG", "")} Getting weather data...')
    logging.debug(f"URL: {url}")

    try:
        # Getting a dataframe with the all data weather
        response = requests.get(url)
        dict_weather = json.loads(response.text)

        logging.debug(
            f'{os.getenv("ID_LOG", "")} Weather data JSON: \n {dict_weather}')

        return dict_weather["observations"][0]
    except Exception as err:
        logging.error(
            f'{os.getenv("ID_LOG", "")} ERROR getting weather data at line {sys.exc_info()[2].tb_lineno}: {err}')
        return None


def parrao_weather_bot(request):
    """ Method for publishing weather data in Twitter """

    logging.info(
        f'{os.getenv("ID_LOG", "")} Starting proccess to get CURRENT data....')

    try:
        # Twitter credentials
        client_twitter = get_auth()
        logging.info(
            f'{os.getenv("ID_LOG", "")} Twitter authentication succesfully: {client_twitter.get_me()}')
    except Exception as err:
        logging.error(
            f'{os.getenv("ID_LOG", "")} Error getting Twitter credentials: \n {format(err)}')
        raise requests.RequestException

    # Get the current weather data and post the tweet
    try:
        dict_weather_data = get_api_data(URL_WEATHER)

        logging.info(
            f'{os.getenv("ID_LOG", "")} Preparing tweet...')

        tz_MAD = pytz.timezone('Europe/Madrid')
        tweet = f'Current Weather in Cercedilla🇪🇸 at {datetime.now(tz_MAD).strftime("%Y-%m-%d %H:%M")}\n' \
                f'🌡 {dict_weather_data["metric"]["temp"]}º \n' \
                f'🌧 {dict_weather_data["metric"]["precipTotal"]} mm \n' \
                f'💧 {dict_weather_data["humidity"]} % \n' \
                f'💨 {dict_weather_data["metric"]["windSpeed"]} km/h \n' \
                f'🌞 {dict_weather_data["uv"]} UVI \n' \
                f'Source: {SOURCE}'

        logging.info(f'{os.getenv("ID_LOG", "")} Starting to post the tweet')
        if os.getenv("ENV_PRO", "N") == "Y":
            logging.info(
                f'{os.getenv("ID_LOG", "")} Posting tweet in Tweeter...')
            client_twitter.create_tweet(text=tweet)
            logging.info(
                f'{os.getenv("ID_LOG", "")} Post tweet succesfully: \n{tweet}')
        else:
            logging.info(
                f"\n************* TWEET:\n{tweet}\n*****************")

    except Exception as err:
        logging.error(
            f'{os.getenv("ID_LOG", "")} Error trying to post the tweet of weather data: \n {format(err)}')


def parrao_weather_bot_daily(request):
    """ Method for publishing daily weather data in Twitter """

    logging.info(
        f'{os.getenv("ID_LOG", "")} Starting proccess to get DAILY data....')

    try:
        # Twitter credentials
        client_twitter = get_auth()
        logging.info(
            f'{os.getenv("ID_LOG", "")} Twitter authentication succesfully: {client_twitter.get_me()}')
    except Exception as err:
        logging.error(
            f'{os.getenv("ID_LOG", "")} Error getting Twitter credentials: \n {format(err)}')
        raise requests.RequestException

    # Get the current weather data and post the tweet
    try:
        # Get yesterday date for getting yerday weather resume
        tz_MAD = pytz.timezone('Europe/Madrid')
        day_forecast = (datetime.now(tz_MAD) - timedelta(1)).strftime("%Y%m%d")

        dict_weather_data = get_api_data(URL_WEATHER_DAILY + day_forecast)

        logging.info(
            f'{os.getenv("ID_LOG", "")} Preparing tweet...')
        tweet = f'🟢 Daily resume in Cercedilla🇪🇸 ➡️ {(datetime.now(tz_MAD) - timedelta(1)).strftime("%Y-%m-%d")}\n' \
                f'🔴 T. Max.: {dict_weather_data["metric"]["tempHigh"]}º \n' \
                f'🔵 T. Min.: {dict_weather_data["metric"]["tempLow"]}º \n' \
                f'🌧 Precip.: {dict_weather_data["metric"]["precipTotal"]} mm \n' \
                f'💧 Humidi.: {dict_weather_data["humidityHigh"]} % - {dict_weather_data["humidityLow"]} %\n' \
                f'💨 Max Gust Wind: {dict_weather_data["metric"]["windgustHigh"]} km/h\n' \
                f'⏲ Press.: {dict_weather_data["metric"]["pressureMax"]} hpa -' \
                f' {dict_weather_data["metric"]["pressureMin"]} hpa\n' \
                f'🌞 UV High.: {dict_weather_data["uvHigh"]} UVI \n' \
                f'Source: {SOURCE} ({datetime.now(tz_MAD).strftime("%Y-%m-%d %H:%M")})'
        #       f'Source: {SOURCE} ({dict_weather_data["obsTimeLocal"]})'

        logging.info(f'{os.getenv("ID_LOG", "")} Starting to post the tweet')
        if os.getenv("ENV_PRO", "N") == "Y":
            logging.info(
                f'{os.getenv("ID_LOG", "")} Posting tweet in Tweeter...')
            client_twitter.create_tweet(text=tweet)
            logging.info(f'{os.getenv("ID_LOG", "")} Post tweet in Twitter')

            # Saving data in DB
            logging.debug("Starting to save in DB...")
            Weather.write_weather(dict_weather_data)
            logging.info(
                f'{os.getenv("ID_LOG", "")} Data succesfully saved in DB')

            logging.info(
                f'{os.getenv("ID_LOG", "")} Post and save tweet succesfully: \n{tweet}')
        else:
            logging.info(
                f"\n************* TWEET:\n{tweet}\n*****************")

    except Exception as err:
        logging.error(
            f'{os.getenv("ID_LOG", "")} Error trying to post the tweet of weather data: \n {format(err)}')


if __name__ == '__main__':

    print('***** Starting cron *****')
    parrao_weather_bot({})
    parrao_weather_bot_daily({})
    print('***** Shutdown cron *****')
