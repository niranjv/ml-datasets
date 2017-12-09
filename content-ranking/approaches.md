

# Task

Get topics to recommend to writers based on trending topics in various social networks

-----

# Approach #1 - Use Twitter trending topics

## Description
- Get trending topics from Twitter API for 1 or more locations
- Reddit equivalent will be "Rising" or "Hot" topics

## References:
- [Twitter API: Get trends near a location](https://developer.twitter.com/en/docs/trends/trends-for-location/api-reference/get-trends-place)
- [Reddit API - Rising](https://www.reddit.com/dev/api/#GET_rising) & [Reddit API - Hot](https://www.reddit.com/dev/api/#GET_hot)

## Pros:
- Simplest approach since list of trending/hot topics is readily available from Twitter API (and Reddit API)
- Input data is "recent" tweets from all users in a given location 
- Tweet clustering and topic extraction are off-loaded to Twitter (exact method for determining trending topics is not known)
- Assuming "tweeting" users in these locations are representative of the population, so trending topics are applicable to the population

## Cons:
- Topics are usually a single hashtag or term, requiring writers to investigate more to determine which aspect of the topic they should write about
- Limited to top 50 trending topic per location (API limit)
- No explicit ranking of topics. Some topics have tweet volume which can be used for ranking but this value is typically missing for many topics. So all topics have to be considered to be equally important.
- Trending topics not available for all locations
- Topics may be too localized and may exclude non-local issues that may also be of interest to users in a location
- Twitter may change their definition of trending or remove this feature altogether, adversely affecting the apps

----- 

# Approach #2 - Use tweets from handpicked sources 

## Description
- Define sources of news in various categories (e.g., @nytimes, @washingtonpost, @cnn, @fox, for national news)
- Get tweets from these sources for the past 24 hours along with their retweet count
- Sort tweets by their retweet count; the most popular tweets are the ones that are retweeted the most
- An equivalent method also works for Reddit using comments

## Pros:
- Instead of single hashtag or term usually returned by Twitter's trending topics, tweets usually contain enoough context for the writers
- We get to pick the sources of "important/trending" topics instead of relying on Twitter's (unknown) sources
- Retweet count provides a measure to rank tweets by "importance"

## Cons:
- Each tweet is considered separately, so even if there are multiple tweets about the same topic, this method does not assign them to the same topic. E.g., the tweets below refer to the same topic but are considered different by this method:
  - "This man braved the California wildfires to save a rabbit from the flames ",5473
  - "Witnesses say this man pulled over to save a wild rabbit from flames along Highway 1 in Southern California as the… ",1361
  - "Man who 'saved' rabbit from wildfire probably made things worse ",94
  - "Incredible video shows a man rescuing a rabbit from the #ThomasFire along a #VenturaCounty highway ",55
- Older tweets within the 24 hour interval are likely to have the most tweets and will be assigned higher "importance" than newer tweets. This introduces a bias towards older tweets
- Selection of sources to monitor introduces a bias. Changing the sources will change the topics considered as "important" or "trending" and their relative ranking
- API limits restrict selection of sources & tweets that can be obtained from them
- Info returned by the Twitter API are based on a representative sample and not the full data set

-----

# Approach #3 - Use topics extracted from tweets

## Description
- As in Approach #2, define sources of news in Twitter (Reddit) and get tweets from these sources from the past 24 hours
- Instead of using tweets directly, extract topics from tweets using topic modeling with LDA. 
- Each tweet is now associated with a topic. Multiple tweets may be associated with the same topic
- Introduce the concept of a "retweet count" for a topic. Value for this metric is the sum of retweets of all tweets assigned to this topic
- Rank topics according to their retweet counts

References:
- [Amazon Comprehend - Topic Modeling](https://aws.amazon.com/comprehend/features/#Topic_Modeling)
- [scikit-learn Latent Dirichlet Allocation](http://scikit-learn.org/stable/modules/decomposition.html#latentdirichletallocation)

## Pros:
- This methods resolves a key issue with Approach #2 (where multiple tweets on the same topic are not combined). By extracting topics from tweets, we are merging tweets on the same topic. For instance, the "rabbit" tweets are combined into the (bag-of-words) topic below with a combined retweet count of 6,983. The words in the topic allow the writer to determine the context and are an improvement over single term that is typically part of Twitter's trending topics.
  - rabbit
  - highway
  - witness
  - pull
  - flame
  - save
  - california
  - wild
  - southern

## Cons:
- Carried over from Approach #2:
  - Older topics will be ranked higher than newer topics since they have more time to accumulate retweets
  - Selection of sources to monitor introduces a bias. Changing the sources will change the topics considered as "important" or "trending" and their relative ranking
  - API limits restrict selection of sources & tweets that can be obtained from them
  - Info returned by the Twitter API are based on a representative sample and not the full data set

-----

# Approach 4 - Use additional measures of "importance"

## Description
- Approaches #2 and #3 above use only retweet count (Twitter) or comment count (Reddit) to determine "importance"
- In addition to retweet/comment count, use other measures such a favorite_count (Twitter) to determine "importance"
- To get a single "importance score" from multiple measures, they need to be combined in some manner. For Twitter, a trivial score would be "topic_importance = topic_retweet_count + topic_favorite_count" (which assumes that retweets and favorites are equally important). 

## Pros:
- Additional measures will give a more comprehensive indication of a topic's importance

## Cons:
- Method of combining multiple measures introduces another source of bias to topic importance and ranking
- Not many additional measures of importance are available
- Replies for a tweet are difficult to calculate
- Carried over from Approach #2:
  - Older topics will be ranked higher than newer topics since they have more time to accumulate retweets
  - Selection of sources to monitor introduces a bias. Changing the sources will change the topics considered as "important" or "trending" and their relative ranking
  - API limits restrict selection of sources & tweets that can be obtained from them
  - Info returned by the Twitter API are based on a representative sample and not the full data set

-----

# Approach #5 - Other approaches

## Description
- Retweet/favorite/comment counts are simple point-in-time meaures of "importance". They do not take into account change of "importance" over time. 
- Monitor change over time in tweet / post volumes during the past 24 hours compared to a baseline to determine which topics are trending

## References:
- [Reddit, Stumbleupon, Del.icio.us and Hacker News Algorithms Exposed!](https://moz.com/blog/reddit-stumbleupon-delicious-and-hacker-news-algorithms-exposed)
- [What is the best way to compute trending topics or tags?](https://stackoverflow.com/questions/787496/what-is-the-best-way-to-compute-trending-topics-or-tags)
- [Inferring Tweet Quality From Retweets](https://www.evanmiller.org/inferring-tweet-quality-from-retweets.html)
- [Deriving the Reddit Formula](https://www.evanmiller.org/deriving-the-reddit-formula.html)

## Pros:
- These methods provide a better means of determining if a topic is "trending" since they take into account topic/user behavior over time 


## Cons:
- Method of determining trending topics can be arbitrary and introduce bias in the list of topics returned
- Carried over from Approach #2:
  - Selection of sources to monitor introduces a bias. Changing the sources will change the topics considered as "important" or "trending" and their relative ranking
  - API limits restrict selection of sources & tweets that can be obtained from them
  - Info returned by the Twitter API are based on a representative sample and not the full data set
