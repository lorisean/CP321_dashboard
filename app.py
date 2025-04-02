import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State

df = pd.read_csv('fifa_world_cup_finals.csv')

country_codes = {
    'Argentina': 'ARG', 'Brazil': 'BRA', 'England': 'GBR', 'France': 'FRA',
    'Germany': 'DEU', 'Italy': 'ITA', 'Netherlands': 'NLD', 'Spain': 'ESP',
    'Uruguay': 'URY', 'Czechoslovakia': 'CZE', 'Hungary': 'HUN', 'Sweden': 'SWE',
    'Croatia': 'HRV'
}

# Calculate number of wins per country
wins = df['Winner'].value_counts().reset_index()
wins.columns = ['Country', 'Wins']
wins['Code'] = wins['Country'].map(country_codes)

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div([
    html.H1("FIFA World Cup Winners Dashboard", style={'textAlign': 'center'}),

    # First row with two columns
    html.Div([
        # Left column - Choropleth map
        html.Div([
            dcc.Graph(id='world-map'),
            dcc.RadioItems(
                id='map-type',
                options=[
                    {'label': 'Show Winners', 'value': 'winners'},
                    {'label': 'Show Runner-ups', 'value': 'runner-ups'}
                ],
                value='winners',
                labelStyle={'display': 'inline-block', 'margin-right': '10px'}
            )
        ], style={'width': '60%', 'display': 'inline-block'}),

        # Right column - Country selector and info
        html.Div([
            html.H3("Country Information"),
            dcc.Dropdown(
                id='country-selector',
                options=[{'label': country, 'value': country} for country in wins['Country']],
                value='Brazil',
                clearable=False
            ),
            html.Div(id='country-info'),
            html.Hr(),
            html.H3("Year Information"),
            dcc.Dropdown(
                id='year-selector',
                options=[{'label': year, 'value': year} for year in df['Year']],
                value=2022,
                clearable=False
            ),
            html.Div(id='year-info')
        ], style={'width': '35%', 'display': 'inline-block', 'vertical-align': 'top', 'padding-left': '20px'})
    ]),

    # Second row with data table
    html.Div([
        html.H3("Complete World Cup Finals Data"),
        html.Table(
            # Header
            [html.Tr([html.Th(col) for col in df.columns])] +
            # Body
            [html.Tr([
                html.Td(df.iloc[i][col]) for col in df.columns
            ]) for i in range(len(df))],
            style={'margin': 'auto', 'border': '1px solid black', 'border-collapse': 'collapse'}
        )
    ], style={'margin-top': '30px', 'text-align': 'center'})
], style={'padding': '20px'})


# Define callbacks for interactivity
@app.callback(
    Output('world-map', 'figure'),
    Input('map-type', 'value')
)
def update_map(map_type):
    if map_type == 'winners':
        fig = px.choropleth(
            wins,
            locations="Code",
            color="Wins",
            hover_name="Country",
            projection="natural earth",
            title="Number of World Cup Wins by Country",
            color_continuous_scale=px.colors.sequential.Plasma
        )
    else:
        runner_ups = df['Runner-up'].value_counts().reset_index()
        runner_ups.columns = ['Country', 'Runner-ups']
        runner_ups['Code'] = runner_ups['Country'].map(country_codes)

        fig = px.choropleth(
            runner_ups,
            locations="Code",
            color="Runner-ups",
            hover_name="Country",
            projection="natural earth",
            title="Number of Times as Runner-up by Country",
            color_continuous_scale=px.colors.sequential.Plasma
        )

    fig.update_layout(margin={"r": 0, "t": 30, "l": 0, "b": 0})
    return fig


@app.callback(
    Output('country-info', 'children'),
    Input('country-selector', 'value')
)
def update_country_info(selected_country):
    country_wins = wins[wins['Country'] == selected_country]['Wins'].values[0]
    wins_years = df[df['Winner'] == selected_country]['Year'].tolist()
    runner_up_years = df[df['Runner-up'] == selected_country]['Year'].tolist()

    return html.Div([
        html.P(f"Total World Cup Wins: {country_wins}"),
        html.P(f"Years Won: {', '.join(map(str, wins_years))}" if wins_years else "Never won the World Cup"),
        html.P(f"Years as Runner-up: {', '.join(map(str, runner_up_years))}" if runner_up_years else "Never runner-up")
    ])


@app.callback(
    Output('year-info', 'children'),
    Input('year-selector', 'value')
)
def update_year_info(selected_year):
    year_data = df[df['Year'] == selected_year].iloc[0]
    return html.Div([
        html.P(f"Winner: {year_data['Winner']}"),
        html.P(f"Runner-up: {year_data['Runner-up']}"),
        html.P(f"Final Score: {year_data['Score']}")
    ])

if __name__ == '__main__':
    app.run(debug=False)