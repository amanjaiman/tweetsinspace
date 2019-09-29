import spacy
import geocoder
from spacy.pipeline import EntityRecognizer
from pandas import DataFrame

nlp = spacy.load('en_core_web_sm')

def geocode_location(location):
    response = geocoder.arcgis(location)
    if not response['error']:
        return [response.json['lat'], response.json['long']]


def ner(tweets: list):
    columns = [[], [], [], [], []]
    for tweet in tweets:
        doc = nlp(tweet)
        for column in columns:
            column.append([])
        for ent in doc.ent:
            if ent.label_ == 'PERSON':
                columns[0][-1].append(ent.text)
            elif ent.label == 'ORG':
                columns[1][-1].append(ent.text)
            elif ent.label == 'GPE':
                columns[2][-1].append(ent.text)
                coords = geocode_location(ent.text)
                if coords is not None:
                    columns[3][-1].append(coords[0])
                    columns[4][-1].append(coords[1])

    return DataFrame(data=columns, columns=['people', 'organizations', 'locations', 'loclats', 'loclongs'])
