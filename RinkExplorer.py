import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc,html, Input, Output 
import urllib.request
from PIL import Image
from dash import dash_table

urllib.request.urlretrieve(
  'https://github.com/Dustin-Tang/RinkExplorer/raw/main/rink.png',
   "rink.png")
  
img = Image.open("rink.png")

app = Dash(__name__)

# A function to figure out if an event was PP, SH or even strength... Used when the data is first loaded
def applyStrength(row):
    if row['Home Team Skaters'] == row['Away Team Skaters']:
        val = 'Even'
    elif (row['Home Team Skaters'] > row['Away Team Skaters']) & (row['Home Team'] == row['Team']):
        val = 'Power Play'
    elif (row['Home Team Skaters'] < row['Away Team Skaters']) & (row['Home Team'] == row['Team']):
        val = 'Shorthanded'
    elif (row['Home Team Skaters'] < row['Away Team Skaters']) & (row['Away Team'] == row['Team']):        
        val = 'Power Play'
    elif (row['Home Team Skaters'] > row['Away Team Skaters']) & (row['Away Team'] == row['Team']):
        val = 'Shorthanded'
    return val

# This function is used to make scatter plots to plot on the rink with multiple types. Plot the colour
def makeTrace(df, pType, pHover_text):
    scat = go.Scatter(x=df[df["Detail 1"] == pType]['X Coordinate'], y=df[df["Detail 1"] == pType]['Y Coordinate'], mode = 'markers', name=pType, opacity=0.9,
                       marker=dict(size=9, line=dict(width=2, color='DarkSlateGrey')),
                       hoverinfo ='text', hovertemplate = pHover_text
                       )
    return scat

# This function is used to plot pass events and broken passes. These are hadnled differently because they are lines
def makePassPlot(df, pType, pColour, pLines, pHover_text):
    direct_pass = []
    direct_pass_end = []
        
    for index, row in df.iterrows():
        direct_pass.append([row['Player'], row['X Coordinate'], row['Y Coordinate'], row['Period'], row['Clock'], row['Team'], row['Event'], row['Detail 1']])
        direct_pass.append([row['Player 2'], row['X Coordinate 2'], row['Y Coordinate 2'], row['Period'], row['Clock'], row['Team'], row['Event'], row['Detail 1']])
        direct_pass.append([None, None, None, None, None, None, None, None])
        direct_pass_end.append([row['Player 2'], row['X Coordinate 2'], row['Y Coordinate 2'], row['Period'], row['Clock'], row['Team'], row['Event'], row['Detail 1']])

    df_direct_pass = pd.DataFrame(direct_pass, columns=['Player', 'X Coordinate', 'Y Coordinate', 'Period', 'Clock', 'Team', 'Event', 'Detail 1'])
    df_direct_pass_end = pd.DataFrame(direct_pass_end, columns=['Player', 'X Coordinate', 'Y Coordinate', 'Period', 'Clock', 'Team', 'Event', 'Detail 1'])
        
        
    scat_pass = go.Scatter(x=df_direct_pass['X Coordinate'], y=df_direct_pass['Y Coordinate'], mode = 'lines', name=pType, opacity=0.9,
                       marker=dict(size=9,color=pColour,symbol='diamond-open', line=pLines),
                       hoverinfo ='text', hovertext=pHover_text
                  )
        
    scat_pass_end = go.Scatter(x=df_direct_pass_end['X Coordinate'], y=df_direct_pass_end['Y Coordinate'], mode = 'markers', name=pType, opacity=0.9,
                       marker=dict(size=9,color=pColour,symbol='diamond-open', line=dict(width=2, color='DarkSlateGrey')),
                       hoverinfo ='text', hovertext=pHover_text
                  )
    return scat_pass, scat_pass_end

#Load the data
df = pd.read_csv("https://raw.githubusercontent.com/bigdatacup/Big-Data-Cup-2021/main/hackathon_womens.csv")

#Wrangle the data to make the team names shorter
df = df.replace('Olympic (Women) - Canada', 'Canada')
df = df.replace('Olympic (Women) - Olympic Athletes from Russia', 'Olympic Athletes from Russia')
df = df.replace('Olympic (Women) - Finland', 'Finland')
df = df.replace('Olympic (Women) - United States', 'United States')

#Wrangle the data to make new columns
df['Matchup'] = df['Home Team'] + ' vs ' + df['Away Team']
df['Strength'] = df.apply(applyStrength, axis=1)
df['Event'] = df['Event'].replace({'Play':'Pass', 'Incomplete Play':'Broken Pass'})

#Populate the drop down boxes
df_games = df[["game_date", 'Matchup']].drop_duplicates() 

games = df_games['Matchup'].tolist()

lt_dates = df['game_date'].drop_duplicates().tolist()
lt_teams = sorted(df['Team'].drop_duplicates().tolist())
lt_event = sorted(df['Event'].drop_duplicates().tolist())
lt_strength = df['Strength'].drop_duplicates().tolist()
lt_player = sorted(df['Player'].drop_duplicates().tolist())

# App layout
app.layout = html.Div([
    html.H1(children="Rink Explorer", className="header-title"),
    html.Div([
    
    
    html.Div(children=[    
        html.Label('Game Date'),
        dcc.Dropdown(id="slct_date",
                 options=[{'label':date, 'value':date} for date in lt_dates],
                 multi=False,
                 value=lt_dates[0],
                 style={'width': "70%", 'text-align': 'left'}
                 ),
    
        html.Label('Game'),
        dcc.Dropdown(id="slct_game",
                 options=[{'label':game, 'value':game} for game in games],
                 multi=False,
                 style={'width': "70%"}
                 ),
    
        html.Label('Team'),
        dcc.Dropdown(id="slct_team",
                 options=[{'label':team, 'value':team} for team in lt_teams],
                 multi=False,
                 #value=lt_teams[0],
                 style={'width': "70%"}
                 ),
        ], style={'padding': 10, 'flex': 1}),
    
    html.Div(children=[
    html.Label('Event'),
    dcc.Dropdown(id="slct_event",
                 options=[{'label':event, 'value':event} for event in lt_event],
                 multi=False,
                 #value=lt_event[0],
                 style={'width': "70%"}
                 ),
    
    html.Label('Strength'),
    dcc.Dropdown(id="slct_strength",
                 options=[{'label':strength, 'value':strength} for strength in lt_strength],
                 multi=False,
                 #value=lt_event[0],
                 style={'width': "70%"}
                 ),
    
    html.Label('Player'),
    dcc.Dropdown(id="slct_player",
                 options=[{'label':player, 'value':player} for player in lt_player],
                 multi=False,
                 #value=lt_event[0],
                 style={'width': "70%"}
                 ),
    html.Label('Period'),
    dcc.Checklist(
            id="box_period",
            options=[
                {'label': '1', 'value': 1},
                {'label': '2', 'value': 2},
                {'label': '3', 'value': 3},
                {'label': 'Overtime', 'value': 4}
            ],
            value=[1, 2, 3, 4]
        )], style={'padding': 10, 'flex': 1}),
    
    html.Div(children=[
        html.Label('Leaderboard'),
    html.Br(),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in ['Player', 'Count']],
        data=[],
        style_cell={'fontSize':14, 'font-family':'arial'},
        style_cell_conditional=[
            {'if': {'column_id': 'Player'},
             'width': '30%'},
            {'if': {'column_id': 'Count'},
             'width': '30%'},
            ]
    ),
    ], style={'padding': 10, 'flex': 1}),
    ], style={'display': 'flex', 'flex-direction': 'row', 'font-family':'arial'}    ),
    
    dcc.Graph(id='rink', figure={})])


# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='rink', component_property='figure'),
     Output(component_id='slct_date', component_property='options'),
     Output(component_id='slct_game', component_property='options'),
     Output(component_id='slct_team', component_property='options'),
     Output(component_id='slct_player', component_property='options'),
     Output(component_id='table', component_property='columns'),
     Output(component_id='table', component_property='data'),
     ],
    [
     Input(component_id='slct_date', component_property='value'),
     Input(component_id='slct_game', component_property='value'),
     Input(component_id='slct_team', component_property='value'),
     Input(component_id='slct_event', component_property='value'),
     Input(component_id='slct_strength', component_property='value'),
     Input(component_id='slct_player', component_property='value'),
     Input(component_id='box_period', component_property='value'),
     ]
)
def update_graph(option_date, option_game, option_team, option_event, option_strength, option_player, box_period):

    df_display = df.copy()
    df_table = pd.DataFrame([], columns=['Player', 'Count'])
 
    # Apply the filtered data for the Rink
    if option_date is not None:
        df_display = df_display[df_display["game_date"] == option_date]       
   
    if option_game is not None:
        df_display = df_display[df_display["Matchup"] == option_game]
    
    if option_team is not None:
        df_display = df_display[df_display["Team"] == option_team]
          
    if option_event is not None:
        df_display = df_display[df_display["Event"] == option_event]
          
    if option_strength is not None:
        df_display = df_display[df_display["Strength"] == option_strength]
        
    if option_player is not None:
        df_display = df_display[df_display["Player"] == option_player]
        
    if box_period is not None:
        df_display = df_display[df_display["Period"].isin(box_period)]        

    #Update the combolist with the newest values        
    opt_date = [{'label':date, 'value':date} for date in df_display[["game_date"]].drop_duplicates()['game_date'].tolist()]        
    opt_game = [{'label':game, 'value':game} for game in df_display[["game_date", 'Matchup']].drop_duplicates()['Matchup'].tolist()]
    opt_team = [{'label':team, 'value':team} for team in sorted(df_display[['Team']].drop_duplicates()['Team'].tolist()) ]
    opt_player = [{'label':player, 'value':player} for player in sorted(df_display[['Player']].drop_duplicates()['Player'].tolist())]


    fig = go.Figure()
    
    #An Event option must be selected
    if option_event:
        
        #declare the hover text for the chart
        hover_text = "Name: "+ df_display['Player'] +"<br>Game: " + df_display['Matchup'].astype(str) +"<br>Period: " + df_display['Period'].astype(str) + "</br>Time: " + df_display['Clock'].astype(str)            
        #Populate the Leaderboard
        df_table = df_display.groupby(['Player'])['Player'].agg(['count']).nlargest(3, 'count').reset_index()
        
        #create the scatter plot for a Goal
        if (option_event == 'Goal'):
                
            scat = go.Scatter(x=df_display['X Coordinate'], y=df_display['Y Coordinate'], mode = 'markers', name='Goal', 
                                  marker=dict(size=9,color='rgba(0, 206, 0, 0.5)', line=dict(width=2, color='DarkSlateGrey')),
                                  hoverinfo ='text', hovertemplate = hover_text
                   
                    )
            fig.add_trace(scat)
                    
        #create the scatter plot for a Shot
        if option_event == 'Shot':
        
            lt_typeShot = df_display['Detail 1'].drop_duplicates().tolist()
        
            for x in lt_typeShot:
                scat = makeTrace(df_display, x, hover_text)
                fig.add_trace(scat)
        #create the scatter plot for a passes    
        if option_event == 'Pass' or option_event == 'Broken Pass':
            df_pass_direct = df_display.loc[(df_display["Detail 1"] == 'Direct')]  
            scat_line, scat_point = makePassPlot(df_pass_direct, 'Direct', 'rgba(50, 50, 170, 0.5)', dict(width=2, color='DarkSlateGrey'), hover_text)
            fig.add_trace(scat_line)
            fig.add_trace(scat_point)
        
            df_pass_indirect = df_display.loc[(df_display["Detail 1"] == 'Indirect')]  
            scat_line_indirect, scat_point_indirect = makePassPlot(df_pass_indirect, 'Indirect', 'rgba(168, 100, 50, 0.5)', dict(width=2, color='DarkSlateGrey'), hover_text)
            fig.add_trace(scat_line_indirect)
            fig.add_trace(scat_point_indirect)

        #Plot faceoff wins
        if option_event == 'Faceoff Win':
        
            lt_typeFaceOff = df_display['Detail 1'].drop_duplicates().tolist()
        
            for x in lt_typeFaceOff:
                scat = makeTrace(df_display, x, hover_text)
                fig.add_trace(scat)
        #Plot ZE, D I/O and Penalty    
        if option_event == 'Zone Entry' or option_event == 'Dump In/Out' or option_event == 'Penalty Taken':
        
            lt_typeZoneEntry = df_display['Detail 1'].drop_duplicates().tolist()
        
            for x in lt_typeZoneEntry:
                scat = makeTrace(df_display, x, hover_text)
                fig.add_trace(scat)
                
        #Puck Recovery and takeaways        
        if option_event == 'Puck Recovery' or option_event == 'Takeaway':
        
            scat = go.Scatter(x=df_display['X Coordinate'], y=df_display['Y Coordinate'], mode = 'markers', name=option_event, opacity=0.9,
                       marker=dict(size=9, line=dict(width=2, color='DarkSlateGrey')),
                       hoverinfo ='text', hovertemplate = hover_text
                       )
            fig.add_trace(scat)            

    #Plots the picture of the rink
    fig.add_layout_image(
            dict(
                source=img,
                xref="x",
                yref="y",
                x=-5,
                y=87,
                sizex=210,
                sizey=90,
                sizing="stretch",
                opacity=1,
                layer="below")
            )

    fig.update_xaxes(visible=False, range = [-5, 205])
    fig.update_yaxes(visible=False, range = [-3, 87])
    
    fig.update_layout(
        autosize=False,
        width=1100,
        height=700
        )

    lt_table_columns = [{"name": i, "id": i} for i in df_table.columns]
    data_table = df_table.to_dict('records')
    
    return fig, opt_date, opt_game, opt_team, opt_player, lt_table_columns, data_table

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)