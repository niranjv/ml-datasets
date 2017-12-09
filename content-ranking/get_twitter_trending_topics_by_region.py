import logging
import os
import sys

import tweepy


def main():

    logger = setup_logging()
    api = setup_api(logger)

    bayarea_cities = {'Oakland', 'San Francisco', 'San Jose'}

    locations = api.trends_available()
    woeid_dict = {}
    woeid_dict[1] = 'Global'
    
    for loc in locations:
        country = loc['country']
        place_name = loc['name']
        if country == 'United States' and place_name in bayarea_cities:
            woeid_dict[loc['woeid']] = place_name

    # setup output file
    output_filepath = 'twitter_trending_topics.csv'
    with open(output_filepath, 'w') as outfile:

        outfile.write('{},{},{}\n'.format('Place', 'Topic', 'Tweet_Volume'))

        for woeid, place_name in woeid_dict.items():
            logger.info('Processing location {} ({})'.format(place_name, woeid))
            response = api.trends_place(woeid)
            trends = response[0]['trends']

            for t in trends:
                tweet_volume = 'NA'
                if t['tweet_volume'] is not None and t['tweet_volume'] != 'null':
                    tweet_volume = t['tweet_volume']
                logger.info('{}: {} ({})'.format(place_name, t['name'], tweet_volume))

                outfile.write('{},{},{}\n'.format(place_name, t['name'], tweet_volume))

            logger.info('')

        


# -----
# Helper functions
# -----

def setup_logging():

    logger = logging.getLogger('get_twitter_trending_topics_by_region')
    logger.setLevel(logging.INFO)

    h = logging.StreamHandler(sys.stdout)
    FORMAT = '%(asctime)s %(filename)s:%(funcName)s:%(lineno)d %(levelname)s: %(message)s'
    h.setFormatter(logging.Formatter(FORMAT))
    logger.addHandler(h)

    return logger


def get_api_keys(logger):

    # Get Twitter API key info from env vars
    consumer_key = os.getenv('TWTR_CONSUMER_KEY')
    consumer_secret = os.getenv('TWTR_CONSUMER_SECRET')
    access_token = os.getenv('TWTR_ACCESS_TOKEN')
    access_token_secret = os.getenv('TWTR_ACCESS_TOKEN_SECRET')
     
    if (consumer_key is None) or (consumer_secret is None) or (access_token is None) or (access_token_secret is None):
        logger.error("Twitter env vars not set up correctly!")
        sys.exit(1)
        
    return (consumer_key, consumer_secret, access_token, access_token_secret)


def setup_api(logger):

    consumer_key, consumer_secret, access_token, access_token_secret = get_api_keys(logger)

    # Set up Tweepy to use above API keys
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    return api


if __name__ == "__main__":

    main()

