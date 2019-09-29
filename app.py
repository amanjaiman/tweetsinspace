import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from datetime import datetime, timedelta
import pandas as pd
from pandas_datareader import data
import plotly.express as px
import os
import pandas as pd

import utils
import clean_data

mapbox_access_token = open(".mapbox_token").read()

days = 30
DATA_PATH = './data/Donald TrumpGEOresults.csv'
# DATA_PATH = './data/trump_geo.csv'
MODE = 'LOAD' # LOAD existing or QUERY new

# creates stock chart
def generate_stock_graph(ticker, start, end, df2):
    # df2 is a dataframe consisting of tweets with columns: date, sentiment, tweet
    fig = go.Figure()
    df = data.DataReader(ticker, 'iex', start, end)
    df.reset_index(level=0, inplace=True)
    m = df['close'].min()
    df2['y'] = m - 1
    fig.add_trace(go.Scatter(x=df2['date'], y=df2['y'], mode='markers', marker = {"color": df2['sentiment']}, name='', hovertext=df2['tweet'], ))
    fig.add_trace(go.Scatter(x=df['date'], y=df['close'], mode='lines', name=''))
    return fig


# creates map
def create_map(df):

    lat = df['latitude']
    lon = df['longitude']
    text = df['text']
    sentiment = df['sentiment']
    favorites = df['favorites']
    retweets = df['retweets']
    
    # insert breaks in text for display
    for i,s in enumerate(text):
        for j in range(0,len(s),40):
            s = s[:j] + '<br>' + s[j+1:]
        text[i] = s

    fig = go.Figure(go.Scattermapbox(
        lat=lat,
        lon=lon,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=retweets*10,
            opacity=0.8,
            color = sentiment,
        ),
        text=text,
        hoverinfo='text',
        hoverlabel=dict(namelength = -1),
    ))

    fig.update_layout(
        hovermode='closest',
        mapbox=go.layout.Mapbox(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=45,
                lon=-73
            ),
            pitch=0,
            zoom=5,
            style='dark',
        ),
        height=800,
    )

    return fig

def create_table(df, max_rows=20):

    # dataframe = pd.DataFrame(data=data)

    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in df.columns])] +

        # text
        [html.Tr([
            html.Td(df.iloc[i][col]) for col in df.columns
        ]) for i in range(min(len(df), max_rows))]
    )


# App
app = dash.Dash(__name__)

now = datetime.now()

app.layout = html.Div([
    
    dcc.Graph(id='map'),
    dcc.Graph(id='sentiment'),
    # dcc.Graph(id='volume'),

    html.Div(children='''
        Input a query, and a valid ticker symbol.
    '''),
    dcc.Input(id='search_box', value='UMD', type='text'),
    # dcc.Input(id='ticker_search_box', value='AAPL', type='text'),
    # dcc.Input(id='sent_search_box', value='Poison', type='text'),

    html.Button(id='submit-button', n_clicks=0, children='Submit'),

    html.Div(id='tweets'),
    dcc.RangeSlider(
        id='date_range_slider',
        min=0,
        max=days,
        # step=0.5,
        value=[0, days],
        marks = {i: (now - timedelta(days=i)).strftime("%m/%d/%Y") for i in range(days)}
        # marks={i: 'Label {}'.format(i) for i in range(10)},
    ),
    # html.Div(id='docs'),
    # html.Div(id='sentences'),
    # html.Div(id='matches'),
])


'''callback wrapper and function for interactivity'''
@app.callback(
    [Output('map', 'figure'),
    Output('sentiment', 'figure'),
    # Output('volume', 'figure'),
    Output('tweets', 'children'),
    ],

    [Input('submit-button', 'n_clicks'),
    Input('date_range_slider', 'value'),
    ],

    [State('search_box', 'value'),
    # State('ticker_search_box', 'value')
    ])
def update_figure(n_clicks, date_range, query, ticker=None):

    # get data
    if MODE == 'QUERY':
        df = clean_data.scrape_tweets(query, 1)
    elif MODE == 'LOAD':
        df = clean_data.get_data(DATA_PATH)
    # df = pd.DataFrame({'latitude': ['45.5017'], 'longitude':['-73.5673'], 'text': ['Montreal']})
    map_figure = create_map(df)

    sentiment_fig = utils.new_time_series(df)

    start = datetime.now() - timedelta(days=date_range[1])
    end = datetime.now() - timedelta(days=date_range[0])
    
    # chart_fig = generate_stock_graph(ticker, start, end)

    df = df.sort_values(by='retweets', ascending=False)
    tweet_table = create_table(df)
    # tweet_table = None

    return map_figure, sentiment_fig, tweet_table


# @app.callback(
#     dash.dependencies.Output('output-container-range-slider', 'children'),
#     [dash.dependencies.Input('my-range-slider', 'value')])
# def update_output(value):
#     return 'You have selected "{}"'.format(value)

if __name__ == '__main__':
    app.run_server(debug=True)