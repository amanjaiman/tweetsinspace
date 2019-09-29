from json import load, loads, dump
from os.path import join
import matplotlib.pyplot as plt
import matplotlib.colors
import requests
import numpy as np
from pandas import DataFrame
from TwitterAPI import TwitterAPI, TwitterPager
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from newsapi.newsapi_client import NewsApiClient
import dateutil.parser

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime

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
    with open('data/'+query+'2FULLresults.csv', 'a') as file:
        writer = csv.writer(file, delimiter=',', quotechar="'", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["date", "text", "sent", "favorites", "retweets"])
    with open('data/'+query+'2GEOresults.csv', 'a') as file:
        writer = csv.writer(file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["date", "text", "sent", "favorites", "retweets", "longitude", "latitude"])

    total = 0
    pager = query_twitter_api(query, "mixed")
    for result in pager.get_iterator():
        coordinates = None
        date = result['created_at']
        text = result['text']
        sent = sentiment(text)
        favorites = result['favorite_count']
        retweets = result['retweet_count']
        if result['coordinates'] is not None:
            coordinates = result['coordinates']['coordinates']
        elif result['place'] is not None:
            bbox = result['place']['bounding_box']['coordinates'][0]
            coordinates = np.mean(bbox, axis=0).tolist()
        if coordinates is None:
            entry = [date, text, sent, favorites, retweets]
            with open('data/'+query+'FULLresults.csv', 'a') as file:
                writer = csv.writer(file, delimiter=',', quotechar="|", quoting=csv.QUOTE_MINIMAL)
                writer.writerow(entry)
            continue

        entry = [date, text, sent, favorites, retweets, *coordinates]
        with open('data/'+query+'GEOresults.csv', 'a') as file:
            writer = csv.writer(file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(entry)

        total += 1
        if total >= num:
            break

def get_tweet_info_no_loc(query: str, num: int):
    with open('data/'+query+'FULLresults.csv', 'a') as file:
        writer = csv.writer(file, delimiter=',', quotechar="'", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["data", "text", "sent", "favorites", "retweets"])

    total = 0
    pager = query_twitter_api(query, "mixed")
    for result in pager.get_iterator():
        date = result['created_at']
        text = result['text']
        sent = sentiment(text)
        favorites = result['favorite_count']
        retweets = result['retweet_count']
        entry = [date, text, sent, favorites, retweets]
        with open('data/'+query+'FULLresults.csv', 'a') as file:
            writer = csv.writer(file, delimiter=',', quotechar="'", quoting=csv.QUOTE_MINIMAL)
            writer.writerow(entry)
        total += 1
        if total >= num:
            break

"""
Takes a string query and sends a GET request to the Twitter API, and
returns the JSON output of the request as a dictionary.
"""
def query_twitter_api(query: str, result_type: str, count: int=MAX_COUNT) -> dict:
    with open(join('assets', 'keys.json')) as file:
        data = load(file)['twitter']
    api = TwitterAPI(**data)
    params = {'q':              query,
               'result_type':   result_type,
               'count':         count}
    pager = TwitterPager(api, 'search/tweets', params)
    return pager

"""
query -> string
start -> string (yyyy-mm-dd)
end -> string (yyyy-mm-dd)
"""
def return_news_df(query, start, end):
    newsapi = NewsApiClient(api_key='4b569ddbefbc4621927cbf78eaed5444')
    articles = newsapi.get_everything(q=query,from_param=start,to=end,language='en',sort_by='relevancy')
    dict_list = []
    pattern = "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"
    if articles['status'] == 'ok':
        for article in articles['articles']:
            if article['content']:
                dict_list.append({'source':article['source']['name'],'date':dateutil.parser.parse(article['publishedAt']).date(), 'author': article['author'], 'title': article['title'], 'description':article['description'], 'content':article['content'], 'sentiment':sentiment(article['content'])})
        df = pd.DataFrame(dict_list)
        return df
    return None

# sentiment
def new_time_series(df):
	df = df.rename(columns={'data':'date'})
	colorscale=[[0.0, "rgb(165,0,38)"],
                [0.1111111111111111, "rgb(215,48,39)"],
                [0.2222222222222222, "rgb(244,109,67)"],
                [0.3333333333333333, "rgb(253,174,97)"],
                [0.4444444444444444, "rgb(254,224,144)"],
                [0.5555555555555556, "rgb(224,243,248)"],
                [0.6666666666666666, "rgb(171,217,233)"],
                [0.7777777777777778, "rgb(116,173,209)"],
                [0.8888888888888888, "rgb(69,117,180)"],
                [1.0, "rgb(49,54,149)"]]
	fig = go.Figure()
	fig.add_trace(go.Scatter(x=df['date'], y=df['sentiment'], marker = {'color':df['sentiment']+1,'colorscale':colorscale}, mode='markers', name=''))
	return fig

# volume
def tweet_line_graph_popularity(df):
    df = df.rename(columns={'data':'date'})
    df['date'] = df['date'].apply(lambda x: datetime.datetime.strptime(x, '%a %b %d %H:%M:%S %z %Y').strftime("%Y-%m-%d %H"))
    sum_df = df.groupby(by='date', as_index=False).count()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sum_df['date'], y=sum_df['retweets'], mode='markers+lines'))
    return fig


def twitter_csv_to_df(csv):
	df = pd.read_csv(csv)
	return df

