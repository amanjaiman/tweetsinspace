import utils
import pandas as pd

df = utils.get_tweet_info("Donald Trump", 400)

df.to_csv('data/trump_geo_400.csv')