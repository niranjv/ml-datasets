from datetime import datetime, timedelta
from dateutil import tz
import logging
import operator
import os
import pytz
import sys

import praw


# Constants
SUBREDDIT_LIMIT = 100 # number of submissions to get from each subreddit


def main():

    logger = setup_logging('get_reddit_data')
    reddit = setup_reddit_api(logger)
    subreddits = get_subreddits(logger)
    
    now = datetime.now()
    now = now.replace(tzinfo=tz.tzlocal())
    
    # Dictionary to store score and num_comments for Reddit posts
    # Assumption: can store dictionary in memory
    submission_counts_dict = {}
    total_posts = 0
    
    # Get posts from each subreddit from the past 24 hours
    for sr in subreddits:
        
        num_submissions = 0
        submissions = reddit.subreddit(sr).new(limit=SUBREDDIT_LIMIT)
        
        for s in submissions:
            title, time, score, num_comments = process_submission(s, logger)
            
            if (now - timedelta(hours=24) < time < now):
                num_submissions += 1
                
                if title in submission_counts_dict:
                    counts = submission_counts_dict[title].split(';')
                    score = score + int(counts[0])
                    num_comments = num_comments + int(counts[1])
                    
                    submission_counts_dict[title] = '{};{};{}'.format(score+num_comments, score, num_comments)
                    
                else:
                    submission_counts_dict[title] = '{};{};{}'.format(score+num_comments, score, num_comments)
            else:
                pass # TODO: submission order is not by time, so cannot stop processing if current submission was created > 24 hours ago
            
        logger.info("Got {} submissions from subreddit '{}' in the past 24 hours".format(num_submissions, sr))
    
    logger.info('Got {} total unique submissions from all subreddits'.format(len(submission_counts_dict)))
    
    # Write submissions to file in descending order of score + num_comments
    sorted_submissions = sorted(submission_counts_dict.items(), key=lambda x: int(x[1].split(';')[0]), reverse=True)
    if (len(sorted_submissions) > 1000):
        sorted_submissions = sorted_submissions[0:1000]

    output_filepath = 'reddit_data.csv'
    with open(output_filepath, 'w') as outfile:
        for (k,v) in sorted_submissions:
            total, score, num_comments = v.split(';')
            outfile.write('"{}",{},{}\n'.format(k, score, num_comments))


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
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
     
    if (client_id is None) or (client_secret is None):
        logger.error("Reddit API env vars not set up correctly!")
        sys.exit(1)
        
    return (client_id, client_secret)


def setup_reddit_api(logger):

    # Setup read-only Reddit instance to access public info
    client_id, client_secret = get_api_keys(logger)
    user_agent="script:test_app:v0.1 (by /u/sniphw)"

    # Set up PRAW to access Reddit
    reddit = praw.Reddit(
                    client_id=client_id, 
                    client_secret=client_secret,
                    user_agent=user_agent
            )
    
    return reddit


def get_subreddits(logger):
    
    # TODO: refine subreddits to use
    # TODO: how to handle duplicate submissions across subreddits?
    # TODO: 'hot', 'rising', 'controversial' subreddits result in no recent submissions. 'all' subreddit results in strange submissions. Why?
    subreddits = ['news', 'technology', 'politics', 'sports', 'religion', 'business', 'entertainment']
    
    return subreddits


def process_submission(s, logger):
    
    title = s.title
    time = datetime.fromtimestamp(s.created_utc, pytz.utc)
    score = s.score
    num_comments = s.num_comments
    
    return title, time, score, num_comments;


if __name__ == "__main__":
    main()
