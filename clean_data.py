import utils
import pandas as pd
import numpy as np

# df = utils.get_tweet_info("Apple", 100)

# df.to_csv('apple_geo.csv')

def get_data(path):
    df = pd.read_csv(path)

    df = df.replace(['type', 'coordinates'], np.nan)
    df = df.dropna()

    # print(df.shape)

    return df

# df = utils.get_tweet_info("Donald Trump", 100)

# df.to_csv('data/trump_geo.csv')
