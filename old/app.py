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

mapbox_access_token = open(".mapbox_token").read()

# creates stock chart
def generate_stock_graph(ticker, start, end, df2):
    # df2 is a dataframe consisting of tweets with columns: date, sentiment, tweet
    fig = go.Figure()
    df = data.DataReader(ticker, 'iex', start, end)
    df.reset_index(level=0, inplace=True)
    df2['y'] = df['close'].min()
    fig.add_trace(go.Scatter(x=df2['date'], y=df2['y'], mode='markers', marker = {"color": df2['sentiment']}, name='', hovertext=df2['tweet'], ))
    fig.add_trace(go.Scatter(x=df['date'], y=df['close'], mode='lines', name=''))
    return fig

# creates map
def create_map(df):

    lat = df['latitude']
    lon = df['longitude']
    text = df['body']
    
    fig = go.Figure(go.Scattermapbox(
        lat=lat,
        lon=lon,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=14
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
            zoom=5
        ),
        height=600,
    )

    return fig

def create_table(data, max_rows=20):

    dataframe = pd.DataFrame(data=data)

    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )


# App
app = dash.Dash(__name__)

now = datetime.now()

app.layout = html.Div([
    dcc.RangeSlider(
        id='date_range_slider'
        min=0,
        max=10,
        step=0.5,
        value=[0, 8],
        marks = {i: (now - timedelta(days=i)).strftime("%m/%d/%Y") for i in range(7)}
    ),
    dcc.Graph(id='map'),
    dcc.Graph(id='chart'),
    html.Div(children='''
        Input a query, and a valid ticker symbol.
    '''),
    dcc.Input(id='search_box', value='UMD', type='text'),
    dcc.Input(id='ticker_search_box', value='AAPL', type='text'),
    # dcc.Input(id='sent_search_box', value='Poison', type='text'),

    html.Button(id='submit-button', n_clicks=0, children='Submit'),

    html.Div(id='Tweets'),
    # html.Div(id='docs'),
    # html.Div(id='sentences'),
    # html.Div(id='matches'),
])


'''callback wrapper and function for interactivity'''
@app.callback(
    [Output('map', 'figure'),
    Output('chart', 'figure'),
    Output('text', 'children'),
    ],

    [Input('submit-button', 'n_clicks')],

    [State('search_box', 'value'),
    State('ticker_search_box', 'value')
    ])
def update_figure(n_clicks, query, ticker):

    # call Jagan's module
    df = pd.DataFrame({'latitude': ['45.5017'], 'longitude':['-73.5673'], 'body': ['Montreal']})
    map_figure = create_map(df)

    start = datetime(2005, 1, 1)
    end = datetime.now()
    
    chart_fig = generate_stock_graph(ticker, start, end)

    # tweet_data = 
    # tweet_table = create_table(tweet_data):
    tweet_table = None

    return map_figure, chart_fig, tweet_table


# @app.callback(
#     Output('relayout-data', 'children'),
#     [Input('basic-interactions', 'relayoutData')])
# def display_selected_data(relayoutData):
#     return json.dumps(relayoutData, indent=2)

if __name__ == '__main__':
    app.run_server(debug=True)