from utils import return_news_df as get_news

import requests
import pandas as pd
from json import load

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from PIL import Image
import numpy as np

def getauth():
    with open("assets/keys.json") as file:
        data = load(file)["microsoft"]
        endpoint = data["endpoint"]
        key = data["key"]

    return endpoint, key

def kp_request(df, endpoint, key):
    content = {"documents": []}
    i = 1
    for _,row in df.iterrows():
        text = row['content'][:5000]
        entry = {"id": str(i), "language": "en", "text": text}
        i+=1
        content["documents"].append(entry)

    keyphrase_url = endpoint + "/text/analytics/v2.1/keyphrases"
    headers = {"Ocp-Apim-Subscription-Key": key}
    response = requests.post(keyphrase_url, headers=headers, json=content)
    kp_json = response.json()

    key_phrases = []
    for doc in kp_json["documents"]:
        doc_phrases = ""
        for word in doc['keyPhrases']:
            doc_phrases += word+" "
        key_phrases.append(doc_phrases)
    return key_phrases;

def entities_request(key_phrases, endpoint, key):
    entity_docs = {"documents": []}
    i = 1
    for phrases in key_phrases:
        entry = {"id": str(i), "text": phrases}
        entity_docs["documents"].append(entry)
        i += 1

    entities_url = endpoint + "/text/analytics/v2.1/entities"
    headers = {"Ocp-Apim-Subscription-Key": key}
    response = requests.post(entities_url, headers=headers, json=entity_docs)
    entities_json = response.json()

    entities = ""
    for doc in entities_json["documents"]:
        for entity in doc["entities"]:
            entities += entity["name"]+" "
    return entities

def generate_word_cloud(words, picture_location):
    image = np.array(Image.open(picture_location))
    stopwords = set(STOPWORDS)

    wc = WordCloud(background_color="white", max_words=750, mask=image, stopwords=stopwords, margin=10, max_font_size=25, random_state=5)

    wc.generate(words)
    image_colors = ImageColorGenerator(image)

    plt.imshow(wc.recolor(color_func=image_colors), interpolation="bilinear")
    plt.axis("off")

    savename = 'assets/' + ''.join(picture_location.split("/")[-1:])+"_wordcloud.png"

    plt.savefig(savename)
    # plt.close(wc)
    print("done")
    return savename

# returns path to image
def get_word_cloud(query: str, start: str, end: str, picture_location: str, entities: bool):
    endpoint, key = getauth()

    news = get_news(query, start, end)
    df = pd.concat([news[:500], news[-500:]])

    key_phrases = kp_request(df, endpoint, key)

    if entities:
        words = entities_request(key_phrases, )
    else:
        words = " ".join(key_phrases)

    return generate_word_cloud(words, picture_location)

# Example Usage: get_word_cloud("Joe Biden", "2019-09-24", "2019-09-28", "assets/dog.png", False)
get_word_cloud("Joe Biden", "2019-09-24", "2019-09-28", "assets/dog.png", False)