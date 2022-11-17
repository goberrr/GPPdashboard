# 1. Import Dash
import dash
from dash import dcc
from dash import html
from dash import Dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import pandas as pd
import plotly
import plotly.express as px

import statistics as st
from statistics import mode


# 2. Creat a Dash app instance
app = dash.Dash(
    external_stylesheets=[dbc.themes.LUX],
    name = 'Global Power Plant'
)

app.title = 'Power Plant Dashboard Analytics'

# Navbar

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="https://www.google.com/")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Page 2", href="#"),
                dbc.DropdownMenuItem("Page 3", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="Global Power Plant Dashboard",
    brand_href="#",
    color="primary",
    dark=True,
)

# IMPORT DATA GPP

gpp = pd.read_csv('power_plant.csv')

# CARD CONTENT

total_country = [
    dbc.CardHeader('Number of Country', style={"color":"black"}),
    dbc.CardBody([
        html.H1(gpp['country_long'].nunique())
    ]),
]

total_power_plant = [
    dbc.CardHeader('Total Power Plant', style={"color":"white"}),
    dbc.CardBody([
        html.H1(gpp['name of powerplant'].nunique(), style={"color":"white"})
    ]),
]
#a = mode(gpp['primary_fuel'])
total_fuel = [
    dbc.CardHeader('Most Used Fuel', style={"color":"black"}),
    dbc.CardBody([
        html.H1(f"{mode(gpp['primary_fuel'])} = {len(gpp[gpp['primary_fuel']==(gpp.describe(include='object')).loc['top','primary_fuel']])}")
        # mode(gpp['primary_fuel'])
        # f'''{a} = {gpp[gpp['primary_fuel']==a].shape(0)}'''
        # (gpp['primary_fuel'].value_counts().head(1))
        # {gpp['primary_fuel'].value_counts().head(1)}
        # {gpp[gpp['primary_fuel']==((gpp.describe(include='object')).loc['top','primary_fuel'])].shape(0)}
    ])
]

#gppidn = gpp[gpp['country_long'] == 'Indonesia']

#topidn = gppidn.sort_values('capacity in MW').tail(10)

#ppidn = [
#    dbc.CardBody([
#        px.bar(
#            topidn,
#            x = 'capacity in MW',
#            y = 'name of powerplant',
#            template = 'ggplot2',
#            title = 'Rangking of Overall Power Plants in Indonesia'
#        )
#    ])
#]



## --- Visualization

#### CHOROPLETH
# Data aggregation
agg1 = pd.crosstab(
    index=[gpp['country code'], gpp['start_year']],
    columns='No of Power Plant'
).reset_index()

# Visualization
plot_map = px.choropleth(agg1.sort_values(by="start_year"),
             locations='country code',
              color_continuous_scale='tealgrn',
             color='No of Power Plant',
             animation_frame='start_year',
             template='ggplot2')


# LAYOUT

app.layout = html.Div(children=[
    navbar,

    html.Br(),

    # Component Main Page

    html.Div([

        # ROW 1
        dbc.Row([

            # ROW 1 - COL 1
            dbc.Col(
                [
                    html.Br(),
                    dbc.Card(total_country, color='blue',),
                    html.Br(),
                    dbc.Card(total_power_plant, color='green',),
                    html.Br(),
                    dbc.Card(total_fuel, color='yellow',),
                ],
                width=3,),
            
            # ROW 1 - COL 2
            dbc.Col(
                [
                    dcc.Graph(figure=plot_map),
                ],
                width=9),
        ]),

        html.Hr(),

        # ROW 2
        dbc.Row([

            # ROW 2 - COL 1
            dbc.Col([
                html.H1('Analysis by Country'),
                dbc.Tabs([
                    ## --- TAB 1: RANKING
                    dbc.Tab(
                        dcc.Graph(
                            id='plotranking',
                        ),
                        label='Ranking'),

                    ## --- TAB 2: DISTRIBUTION
                    dbc.Tab(
                        dcc.Graph(
                            id='plotdistribut',
                       ),
                        label='Distribution'),
                ]),
            ],width=7),

            # ROW 2 - COL 2
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader('Select Country'),
                    dbc.CardBody(
                        dcc.Dropdown(
                            id='choose_country',
                            options=gpp['country_long'].unique(),
                            value='Indonesia',
                        ),
                    ),
                ]),
                dcc.Graph(
                    id='plotpie',
                ),
            ], width=5),
        ]),

    ], style={
        'paddingLeft':'30px',
        'paddingRight':'30px',
    }),
])

# CALLBACK PLOT RANKING

@app.callback(
    Output(component_id='plotranking', component_property='figure'),
    Input(component_id='choose_country', component_property='value')
)
def update_output(country_name):
    gpp_indo = gpp[gpp['country_long'] == country_name]
    top_indo = gpp_indo.sort_values('capacity in MW').tail(10)

    # Visualize
    plot_ranking = px.bar(
        top_indo,
        x = 'capacity in MW',
        y = 'name of powerplant',
        template = 'ggplot2',
        title = f'Rank of Overall Power Plants in {country_name}'
    )

    return plot_ranking

@app.callback(
    Output(component_id='plotdistribut', component_property='figure'),
    Input(component_id='choose_country', component_property='value')
)
def update_output2(country_name):
    gpp_indo = gpp[gpp['country_long'] == country_name]
    plot_distribut = px.box(
        gpp_indo,
        color='primary_fuel',
        y='capacity in MW',
        template='ggplot2',
        title=f'Distribution of capacity in MW in each fuel in {country_name}',
        labels={
            'primary_fuel': 'Type of Fuel'
        }
    ).update_xaxes(visible=False)

    return plot_distribut

@app.callback(
    Output(component_id='plotpie', component_property='figure'),
    Input(component_id='choose_country', component_property='value')
)
def update_output2(country_name):
    gpp_indo = gpp[gpp['country_long'] == country_name]
    agg2=pd.crosstab(
        index=gpp_indo['primary_fuel'],
        columns='No of Power Plant'
    ).reset_index()

    # visualize
    plot_pie = px.pie(
        agg2,
        values='No of Power Plant',
        names='primary_fuel',
        color_discrete_sequence=['aquamarine', 'salmon', 'plum', 'grey', 'slateblue'],
        template='ggplot2',
        hole=0.4,
        title=f'Distribution of Fuel Type in {country_name}',
        labels={
            'primary_fuel': 'Type of Fuel'
        }
    )

    return plot_pie

# 3. Start the Dash server
if __name__ == "__main__":
    app.run_server()
