from json import load, loads
from os.path import join

import requests
import numpy as np
from pandas import DataFrame
from TwitterAPI import TwitterAPI, TwitterPager
#from nltk.sentiment.vader import SentimentIntensityAnalyzer

MAX_COUNT = 100

#sid = SentimentIntensityAnalyzer()


#def sentiment(text: str) -> int:
#    return sid.polarity_scores(text)['compound']


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
    pager = query_twitter_api(query, "recent")
    for result in pager.get_iterator():
        coordinates = None
        if result['coordinates'] is not None:
            coordinates = result['coordinates']['coordinates']
        elif result['place'] is not None:
            bbox = result['place']['bounding_box']['coordinates'][0]
            coordinates = np.mean(bbox, axis=0).tolist()
        if coordinates is None:
            continue
        entry = [result['text'], *coordinates]
        entries.append(entry)
        total += 1
        print("Adding record "+ str(total))
        if total >= num:
            break
    return DataFrame(data=entries, columns=['body', 'long', 'lat'])


def get_tweet_info_no_loc(query: str, num: int):
    entries = []
    total = 0
    pager = query_twitter_api(query, "popular")
    for result in pager.get_iterator():
        text = result['text']
        date = result['created_at']
        entry = [date, text, sentiment(text)]
        entries.append(entry)
        total += 1
        print("Adding record "+ str(total))
        if total >= num:
            break
    return DataFrame(data=entries, columns=['date', 'text', 'sentiment'])


"""
Takes a string query and sends a GET request to the Twitter API, and
returns the JSON output of the request as a dictionary.
"""
def query_twitter_api(query: str, result_type: str, count: int=MAX_COUNT) -> dict:
    with open(join('assets', 'keys.json')) as file:
        data = load(file)
    api = TwitterAPI(**data)
    params = {'q':              query,
               'result_type':   result_type,
               'count':         count}
    pager = TwitterPager(api, 'search/tweets', params)
    return pager

get_tweet_info("Donald Trump", 1)
    