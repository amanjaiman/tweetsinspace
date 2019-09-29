import utils
import pandas as pd
import numpy as np

# df = utils.get_tweet_info("Apple", 100)

# df.to_csv('apple_geo.csv')

def get_data(path):
    df = pd.read_csv(path, quotechar="|")

    df = df.replace(['type', 'coordinates'], np.nan)
    df = df.dropna()

    df.insert(3, 'sentiment', df['text'].map(utils.sentiment))
    # df['sentiment'] = df['body'].apply(utils.sentiment)
    # print(df.shape)

    return df

# def scrape_tweets(query, num):
#     get_tweet_info(query, num)

#     with open('data/'+query+'FULLresults.csv', 'r') as file:

# df = utils.get_tweet_info("Donald Trump", 100)
# df.to_csv('data/trump_geo.csv')
