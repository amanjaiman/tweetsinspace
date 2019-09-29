from json import load, loads, dump
from os.path import join

import requests
import numpy as np
from pandas import DataFrame
from TwitterAPI import TwitterAPI, TwitterPager
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from newsapi.newsapi_client import NewsApiClient
import dateutil.parser


import csv

MAX_COUNT = 100

sid = SentimentIntensityAnalyzer()


def sentiment(text: str) -> int:
   return sid.polarity_scores(text)['compound']


"""
Takes a string representing a topic to collect tweets on and the number
of tweets to collect, and returns a DataFrame with three columns in the
following order:
body        str
lat         float64
long        float64
"""
def get_tweet_info(query: str, num: int):
    total = 0
    pager = query_twitter_api(query, "recent")
    results = []
    with open('data/'+query+'results.csv', 'a') as file:
        for result in pager.get_iterator():
            results.append(result)
            coordinates = None
            if result['coordinates'] is not None:
                coordinates = result['coordinates']['coordinates']
            elif result['place'] is not None:
                bbox = result['place']['bounding_box']['coordinates'][0]
                coordinates = np.mean(bbox, axis=0).tolist()
            if coordinates is None:
                continue
            
            date = result['created_at']
            text = result['text']
            sent = sentiment(text)
            favorites = result['favorite_count']
            retweets = result['retweet_count']

            entry = [date, text, sent, favorites, retweets, *coordinates]

            writer = csv.writer(file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(entry)

            total += 1
            if total >= num:
                break
    with open('data/' + query + ".json", "w") as file:
        dump(results, file)


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

def return_news_df(query, start, end):
    newsapi = NewsApiClient(api_key='4b569ddbefbc4621927cbf78eaed5444')
    articles = newsapi.get_everything(q=query,from_param=start,to=end,language='en',sort_by='relevancy')
    dict_list = []
    pattern = "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"
    if articles['status'] == 'ok':
        for article in articles['articles']:
            dict_list.append({'source':article['source']['name'],'date':dateutil.parser.parse(article['publishedAt']).date(), 'author': article['author'], 'title': article['title'], 'description':article['description'], 'content':article['content'], 'sentiment':sentiment(article['content'])})
        df = pd.DataFrame(dict_list)
        return df
    return None
    
def new_time_series(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['date'], y=df['sentiment'], mode='marker', name=''))
    return fig

