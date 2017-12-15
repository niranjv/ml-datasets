import logging
import sys

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

n_features = 1000
n_components = 1
n_top_words = 5

def main():

    logger = setup_logging('get_topics')
    
    # Use tf (raw term count) features for LDA.
    logger.info("Extracting tf features for LDA...")
    tf_vectorizer = CountVectorizer(
                        # max_df=0.95, 
                        # min_df=2,
                        max_features=n_features,
                        stop_words='english'
                    )
    
    get_twitter_topics(tf_vectorizer, logger)
    

def setup_logging(logger_name):

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    h = logging.StreamHandler(sys.stdout)
    FORMAT = '%(asctime)s %(filename)s:%(funcName)s:%(lineno)d %(levelname)s: %(message)s'
    h.setFormatter(logging.Formatter(FORMAT))
    logger.addHandler(h)

    return logger


def get_twitter_topics(tf_vectorizer, logger):
                    
    with open("twitter_data.csv") as f:
        for idx, tweet in enumerate(f):
            tweet_text = tweet.split('"')[1]
            tf = tf_vectorizer.fit_transform([tweet_text])
            
            lda = LatentDirichletAllocation(
                                n_components=n_components, 
                                max_iter=5,
                                learning_method='online',
                                learning_offset=50.,
                                random_state=0
                            )
            lda.fit(tf)
            tf_feature_names = tf_vectorizer.get_feature_names()
            # logger.info(tf_feature_names)
            # print_top_words(lda, tf_feature_names, n_top_words)
            
            for topic in lda.components_:
                logger.info('{}: {}'.format(idx, ",".join([tf_feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]])))


def print_top_words(model, feature_names, n_top_words):
    for topic_idx, topic in enumerate(model.components_):
        message = "Topic #%d: " % topic_idx
        message += " ".join([feature_names[i]
                             for i in topic.argsort()[:-n_top_words - 1:-1]])
        print(message)
    print()

def get_reddit_topics():
    pass


if __name__ == "__main__":
    main()
    