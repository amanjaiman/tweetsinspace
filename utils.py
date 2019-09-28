from json import load, loads
from os.path import join

import requests
import numpy as np
from pandas import DataFrame
from TwitterAPI import TwitterAPI, TwitterPager

MAX_COUNT = 100


"""
Takes a string representing a topic to collect tweets on and the number
of tweets to collect, and returns a DataFrame with three columns in the
following order:
body        str
lat         float64
long        float64
"""
def get_tweet_info(query: str, num: int):
    entries = []
    total = 0
    pager = query_twitter_api(query)
    for result in pager.get_iterator():
        coordinates = None
        if result['coordinates'] is not None:
            coordinates = results['coordinates']
        elif result['place'] is not None:
            bbox = result['place']['bounding_box']['coordinates'][0]
            coordinates = np.mean(bbox, axis=0).tolist()
        if coordinates is None:
            continue
        entry = [result['text'], *coordinates]
        entries.append(entry)
        total += 1
        if total > num:
            break
    return DataFrame(data=entries, columns=['body', 'lat', 'long'])

"""
Takes a string query and sends a GET request to the Twitter API, and
returns the JSON output of the request as a dictionary.
"""
def query_twitter_api(query: str, count: int=MAX_COUNT) -> dict:
    with open(join('assets', 'keys.json')) as file:
        data = load(file)
    api = TwitterAPI(**data)
    params = {'q':              query,
               'result_type':   'recent',
               'count':         count}
    pager = TwitterPager(api, 'search/tweets', params)
    return pager


#def getTweets(query: str):
#    tweets = []
#    for i in range(0, 11):
#        tweets.append(get_tweet_info(query, 1000))
    
