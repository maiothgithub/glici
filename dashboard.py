import sqlite3
from datetime import datetime, timedelta

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

DB_FILE = "sensor_data.db"

# --- Helper: read data from SQLite ---
def read_data(since_hours=1):
    """ Read sensor data from the database for the last `since_hours` hours. """
    conn = sqlite3.connect(DB_FILE)
    since_time = (datetime.now() - timedelta(hours=since_hours)).strftime("%Y-%m-%d %H:%M:%S")
    query = f"SELECT timestamp, temperature, humidity, sensor FROM readings WHERE timestamp >= '{since_time}' ORDER BY timestamp ASC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


app = dash.Dash(__name__)
app.title = "Glici Sensor Monitor"

app.layout = html.Div([
    html.H1("🌡️ Sensor Dashboard", style={'textAlign': 'center'}),

    html.Div(id='current-data', style={'fontSize': 24, 'textAlign': 'center', 'marginBottom': 20}),

    html.Div([
        html.Label("Time Range:"),
        dcc.Dropdown(
            id='range-dropdown',
            options=[
                {'label': 'Last Hour', 'value': 1},
                {'label': 'Last 24 Hours', 'value': 24},
                {'label': 'Last 7 Days', 'value': 24*7},
            ],
            value=1,
            clearable=False,
            style={'width': '200px'}
        ),
    ], style={'textAlign': 'left'}),

    dcc.Graph(id='sensor-graph'),
    dcc.Interval(id='interval-refresh', interval=10*1000, n_intervals=0)  # refresh every 10s
])

# --- Callbacks ---

@app.callback(
    Output('current-data', 'children'),
    Output('sensor-graph', 'figure'),
    Input('range-dropdown', 'value'),
    Input('interval-refresh', 'n_intervals')
)
def update_dashboard(hours, _):
    """ Updates the dashboard based on selected time range and refresh interval """
    df = read_data(hours)
    if df.empty:
        return "No data yet.", px.scatter()

    latest = df.iloc[-1]
    current = (
        f"Current → Temp: {latest['temperature']:.2f} °C | "
        f"Humidity: {latest['humidity']:.2f} % | "
        f"Sensor: {latest['sensor']:5} units"
    )

    # --- Create 3 vertically stacked subplots ---
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=("Temperature (°C)", "Humidity (%)", "Sensor (units)")
    )

    # Temperature
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"], y=df["temperature"],
            name="Temperature (°C)", line=dict(color="orange")
        ),
        row=1, col=1
    )

    # Humidity
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"], y=df["humidity"],
            name="Humidity (%)", line=dict(color="deepskyblue")
        ),
        row=2, col=1
    )

    # Sensor
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"], y=df["sensor"],
            name="Sensor (units)", line=dict(color="limegreen")
        ),
        row=3, col=1
    )

    # Layout
    fig.update_layout(
        height=500,
        template="plotly_dark",
        title_text=f"Sensor Measurements (last {hours} h)",
        showlegend=False,
        margin=dict(t=80, b=50, l=80, r=30)
    )

    # Axis labels
    fig.update_yaxes(title_text="°C", range=[23,27], row=1, col=1)
    fig.update_yaxes(title_text="%", range=[38,43], row=2, col=1)
    fig.update_yaxes(title_text="units",range=[220,280] , row=3, col=1)
    fig.update_xaxes(title_text="Time", row=3, col=1)

    return current, fig

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090,debug=True)
