from datetime import datetime, timedelta
from dateutil import tz
import logging
import operator
import os
import sys

import tweepy


def main():

    logger = setup_logging('get_twitter_data')
    api = setup_api(logger)
    sources = setup_sources(logger)

    # Tweet created_at is in UTC timezone. Convert to local timezone
    now = datetime.now()
    now = now.replace(tzinfo=tz.tzlocal())

    # Dictionary to store retweet & favorite counts for tweets
    # Assumption: can store dictionary in memory
    tweet_counts_dict = {}
    total_tweets = 0

    # Get tweets from each of above sources from the past 24 hours
    for s in sources:
        logger.info("Processing source: " + s)

        num_tweets = 0
        for tweet in tweepy.Cursor(api.user_timeline, id=s).items():

            tweet_text, tweet_time, retweet_count, favorite_count = process_tweet(tweet, logger)
            
            if (now - timedelta(hours=24) < tweet_time < now) and not tweet_text.startswith('https://t.co'):

                num_tweets += 1 

                if tweet_text in tweet_counts_dict:
                    counts = tweet_counts_dict[tweet_text].split(';')
                    retweet_count = retweet_count + int(counts[0])
                    favorite_count = favorite_count + int(counts[1])
                    
                    tweet_counts_dict[tweet_text] = '{};{};{}'.format(retweet_count+favorite_count, retweet_count, favorite_count)

                else:
                    tweet_counts_dict[tweet_text] = '{};{};{}'.format(retweet_count+favorite_count, retweet_count, favorite_count)

            # Assumption: tweets are ordered by timestamp and we can stop processing at the first tweet that is past 24 hours
            else:
                logger.info("Got {} tweets from source '{}' in the past 24 hours".format(num_tweets, s))
                total_tweets += num_tweets
                break

    logger.info('Got {} total unique tweets from all sources'.format(len(tweet_counts_dict)))
        
    # Write tweets to file in descending order of retweet+favorites
    sorted_tweets = sorted(tweet_counts_dict.items(), key=lambda x: int(x[1].split(';')[0]), reverse=True)
    # if (len(sorted_tweets) > 1000):
    #     sorted_tweets = sorted_tweets[0:1000]

    output_filepath = 'twitter_data.csv'
    with open(output_filepath, 'w') as outfile:
        for (k,v) in sorted_tweets:
            total, retweet_count, favorite_count = v.split(';')
            outfile.write('"{}",{},{}\n'.format(k, retweet_count, favorite_count))


# -----
# Helper functions
# -----

def setup_logging(logger_name):

    logger = logging.getLogger(logger_name)
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
        logger.error("Twitter API env vars not set up correctly!")
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

    news_sources = national_newspapers + local_newspapers + national_tv + local_tv + other_news

    # TODO: Add sources for other topics like politics, sports, religion, technology, business, entertainment, etc.

    # sources = news_sources
    sources = ['nytimes', 'washingtonpost']

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

    tweet_text = tweet_text.replace('"', "'")
    tweet_text = tweet_text.replace('\n', '')


    # Convert tweet time from UTC to local time
    utc = tweet.created_at.replace(tzinfo=tz.tzutc())
    tweet_time = utc.astimezone(tz.tzlocal())

    # Get retweet count
    retweet_count = tweet.retweet_count
    favorite_count = tweet.favorite_count

    return (tweet_text, tweet_time, retweet_count, favorite_count)


if __name__ == "__main__":
    main()
