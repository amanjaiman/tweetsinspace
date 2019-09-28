import utils
import pandas as pd

df = utils.get_tweet_info("Donald Trump", 100)

df.to_csv('data/trump_geo.csv')