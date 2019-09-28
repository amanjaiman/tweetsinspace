import utils
import pandas as pd

df = utils.get_tweet_info("Apple", 100)

df.to_csv('apple_geo.csv')