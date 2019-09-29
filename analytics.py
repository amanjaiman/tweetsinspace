import spacy
import geocoder
from spacy.pipeline import EntityRecognizer

nlp = spacy.load('en_core_web_sm')

def ner(tweets: list):
    people = {}
    organizations = {}
    locations = {}
    for tweet in tweets:
        doc = nlp(tweet)
        for ent in doc.ent:
            if ent.label_ == 'PERSON':
                people.add(ent.text)
            elif ent.label == 'GPE':
                locations.add(ent.text)
            elif ent.label == 'ORG':
                locations.add(ent.text)
    return {'people':           [*people],
            'organizations':    [*organizations],
            'locations':        [*locations]}

def geocode_locations(locations):
    coords = []
    for location in locations:
        response = geocoder.arcgis(location)
        coords.append([response['lat'], response['long']])
    return coords