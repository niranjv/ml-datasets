import logging
import sys

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

n_features = 1000
n_components = 1
n_top_words = 5

def main():

    logger = setup_logging('get_topics')
    
    get_topics('twitter_data.csv', 'twitter_topics.csv', logger)
    get_topics('reddit_data.csv', 'reddit_topics.csv', logger)
    

def setup_logging(logger_name):

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    h = logging.StreamHandler(sys.stdout)
    FORMAT = '%(asctime)s %(filename)s:%(funcName)s:%(lineno)d %(levelname)s: %(message)s'
    h.setFormatter(logging.Formatter(FORMAT))
    logger.addHandler(h)

    return logger


def get_topics(input_filename, output_filename, logger):

    logger.info("Processing file " + input_filename)
    
    # Use tf (raw term count) features for LDA.
    logger.info("Extracting tf features for LDA...")
    tf_vectorizer = CountVectorizer(
                        # max_df=0.95, 
                        # min_df=2,
                        max_features=n_features,
                        stop_words='english'
                    )
                    
    with open(input_filename) as infile:
        with open(output_filename, 'w') as outfile:
            for idx, line in enumerate(infile):
                text = line.split('"')[1]
                
                try:
                    tf = tf_vectorizer.fit_transform([text])
                except ValueError as e:
                    logger.warn('Line {}: {}'.format(idx, str(e)))
                    
                lda = LatentDirichletAllocation(
                                    n_components=n_components, 
                                    max_iter=5,
                                    learning_method='online',
                                    learning_offset=50.
                                )
                lda.fit(tf)
                tf_feature_names = tf_vectorizer.get_feature_names()
                
                for topic in lda.components_:
                    outfile.write('{}: {}\n'.format(idx, ",".join([tf_feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]])))
                    

if __name__ == "__main__":
    main()
    