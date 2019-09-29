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

import clean_data

mapbox_access_token = open(".mapbox_token").read()

days = 30

# creates stock chart
def generate_stock_graph(ticker, start, end):
    os.environ["IEX_API_KEY"] = "pk_e198e446a54843a48b90ea9b1c85bf3f"

    df = data.DataReader(ticker, 'iex', start, end)
    df.reset_index(level=0, inplace=True)
    fig = px.line(df, x='date', y='close', title='Stock Price for ' + ticker)
    return fig

# from newsapi.newsapi_client import NewsApiClient
# import pandas as pd

def return_news_df(query, start, end):
    newsapi = NewsApiClient(api_key='4b569ddbefbc4621927cbf78eaed5444')
    articles = newsapi.get_everything(q=query,from_param=start,to=end,language='en',sort_by='relevancy')
    dict_list = []
    if articles['status'] == 'ok':
        for article in articles['articles']:
            dict_list.append({'source':article['source']['name'], 'author': article['author'], 'title': article['title'], 'description':article['description'], 'content':article['description']})
        df = pd.DataFrame(dict_list)
        return df
    return None
    
# creates map
def create_map(df):

    lat = df['latitude']
    lon = df['longitude']
    text = df['body']
    sentiment = df['sentiment']
    
    fig = go.Figure(go.Scattermapbox(
        lat=lat,
        lon=lon,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10,
            opacity=0.8,
            color = sentiment,
        ),
        text=text,
        
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

        # Body
        [html.Tr([
            html.Td(df.iloc[i][col]) for col in df.columns
        ]) for i in range(min(len(df), max_rows))]
    )


# App
app = dash.Dash(__name__)

now = datetime.now()

app.layout = html.Div([
    
    dcc.Graph(id='map'),
    dcc.Graph(id='chart'),
    html.Div(children='''
        Input a query, and a valid ticker symbol.
    '''),
    dcc.Input(id='search_box', value='UMD', type='text'),
    dcc.Input(id='ticker_search_box', value='AAPL', type='text'),
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
    Output('chart', 'figure'),
    Output('tweets', 'children'),
    ],

    [Input('submit-button', 'n_clicks'),
    Input('date_range_slider', 'value'),
    ],

    [State('search_box', 'value'),
    State('ticker_search_box', 'value')
    ])
def update_figure(n_clicks, date_range, query, ticker):

    # call Jagan's module
    df = clean_data.get_data('./data/trump_geo.csv')
    # df = pd.DataFrame({'latitude': ['45.5017'], 'longitude':['-73.5673'], 'body': ['Montreal']})
    map_figure = create_map(df)

    # start = datetime(2005, 1, 1)
    start = datetime.now() - timedelta(days=date_range[1])
    end = datetime.now() - timedelta(days=date_range[0])
    
    chart_fig = generate_stock_graph(ticker, start, end)

    # tweet_data = 
    tweet_table = create_table(df)
    # tweet_table = None

    return map_figure, chart_fig, tweet_table


# @app.callback(
#     dash.dependencies.Output('output-container-range-slider', 'children'),
#     [dash.dependencies.Input('my-range-slider', 'value')])
# def update_output(value):
#     return 'You have selected "{}"'.format(value)

if __name__ == '__main__':
    app.run_server(debug=True)