from datetime import datetime, timedelta
from dateutil import tz
import logging
import os
import sys

import tweepy


def main():

    logger = setup_logging()
    api = setup_api(logger)
    sources = setup_sources(logger)


    # Tweet created_at is in UTC timezone. Convert to local timezone
    now = datetime.now()
    now = now.replace(tzinfo=tz.tzlocal())

    # Set up output file
    total_tweets = 0
    output_filepath = 'twitter_data.csv'
    with open(output_filepath, 'w') as outfile:

        # Get tweets from each of above sources from the past 24 hours
        for s in sources:
            logger.info("Processing source:" + s)

            num_tweets = 0
            for tweet in tweepy.Cursor(api.user_timeline, id=s).items():

                tweet_text, tweet_time, retweet_count = process_tweet(tweet, logger)
                
                if (now - timedelta(hours=24) < tweet_time < now) and not tweet_text.startswith('https://t.co'):
                    while (retweet_count > 0):
                        outfile.write(tweet_text + '\n')
                        retweet_count -= 1

                    num_tweets += 1

                else:
                    logger.info("Got {} tweets from source '{}' in the past 24 hours".format(num_tweets, s))
                    total_tweets += num_tweets
                    break


# -----
# Helper functions
# -----

def setup_logging():

    logger = logging.getLogger('get_twitter_date')
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


def setup_sources(logger):

    # Setup news sources 
    national_newspapers = ['nytimes', 'washingtonpost', 'TIME', 'AP', 'Reuters', 'WSJ', 'USATODAY']
    local_newspapers = ['sfexaminer', 'SFGate', 'mercnews', 'EastBayTimes', 'OakTribNews']
    national_tv = ['cnnbrk', 'CNN', 'BBCWorld', 'BBCBreaking', 'FoxNews', 'ABC', 'CBSNews', 'NBCNews', 'NewsHour', 'NPR ']
    local_tv = ['nbcbayarea', 'abc7newsbayarea', 'KTVU', 'kron4news']
    other_news = ['HuffPost']

    sources = national_newspapers + local_newspapers + national_tv + local_tv + other_news

    # sources = ['nytimes', 'washingtonpost']

    return sources


def process_tweet(tweet, logger):

    # Remove URL at the end of tweet
    tweet_text = tweet.text
    urls = tweet.entities['urls']
    if (len(urls) > 0):
        url_start_index = urls[0]['indices'][0]
        tweet_text = tweet.text[0:url_start_index]

    # remove retweet prefix at the beginning
    rt_prefix = 'RT '
    if tweet_text.startswith(rt_prefix) and tweet_text.find(':') > 0:
        tweet_text = tweet_text[tweet_text.find(':')+2:]


    # Convert tweet time from UTC to local time
    utc = tweet.created_at.replace(tzinfo=tz.tzutc())
    tweet_time = utc.astimezone(tz.tzlocal())

    # Get retweet count
    retweet_count = tweet.retweet_count

    return (tweet_text, tweet_time, retweet_count)


if __name__ == "__main__":

    main()

