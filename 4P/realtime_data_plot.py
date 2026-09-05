import random
import time
from collections import deque
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# Initialize Dash application
app = dash.Dash(__name__)

# Fixed-size deques to simulate data retention limits (e.g., last 100 points)
MAX_POINTS = 100
time_series = deque(maxlen=MAX_POINTS)
accel_x = deque(maxlen=MAX_POINTS)
accel_y = deque(maxlen=MAX_POINTS)
accel_z = deque(maxlen=MAX_POINTS)
pir_data = deque(maxlen=MAX_POINTS)

start_time = time.time()


def fetch_sensor_data():
    """Simulates reading incoming data from a serial stream or database."""
    current_time = round(time.time() - start_time, 2)

    # Simulated 10 Hz accelerometer readings (in g)
    ax = round(random.uniform(-0.1, 0.1), 3)
    ay = round(random.uniform(-0.1, 0.1), 3)
    az = round(1.0 + random.uniform(-0.05, 0.05), 3)

    # Simulated PIR motion binary state (0 or 1)
    pir = 1 if random.random() > 0.85 else 0

    return current_time, ax, ay, az, pir


# Application Layout
app.layout = html.Div(
    style={
        "fontFamily": "Arial, sans-serif",
        "padding": "20px",
        "backgroundColor": "#f4f6f9",
    },
    children=[
        html.H2(
            "Real-Time Multi-Sensor Security Dashboard",
            style={"textAlign": "center"},
        ),
        # Live Graph Component
        dcc.Graph(id="live-sensor-graph"),
        # Interval Component: Triggers updates every 100ms (10 Hz rate)
        dcc.Interval(id="graph-update-interval", interval=100, n_intervals=0),
    ],
)


@app.callback(
    Output("live-sensor-graph", "figure"),
    Input("graph-update-interval", "n_intervals"),
)
def update_graph_scatter(n):
    # Fetch new sensor sample
    t, ax, ay, az, pir = fetch_sensor_data()

    # Append to rolling queues
    time_series.append(t)
    accel_x.append(ax)
    accel_y.append(ay)
    accel_z.append(az)
    pir_data.append(pir)

    # Build Plotly traces
    fig = go.Figure()

    # Accelerometer X, Y, Z Traces
    fig.add_trace(
        go.Scatter(
            x=list(time_series),
            y=list(accel_x),
            name="Accel X",
            mode="lines",
            line=dict(color="#1f77b4"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=list(time_series),
            y=list(accel_y),
            name="Accel Y",
            mode="lines",
            line=dict(color="#2ca02c"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=list(time_series),
            y=list(accel_z),
            name="Accel Z",
            mode="lines",
            line=dict(color="#ff7f0e"),
        )
    )

    # PIR Motion Trace
    fig.add_trace(
        go.Scatter(
            x=list(time_series),
            y=list(pir_data),
            name="PIR Motion",
            mode="lines",
            line=dict(color="#d62728", dash="dash"),
            yaxis="y2",
        )
    )

    # Layout configuration with dual Y-axes
    fig.update_layout(
        title="Live Sensor Feeds (10 Hz Accelerometer & PIR)",
        xaxis=dict(title="Elapsed Time (s)"),
        yaxis=dict(title="Acceleration (g)"),
        yaxis2=dict(
            title="PIR Motion State (0/1)",
            overlaying="y",
            side="right",
            range=[-0.1, 1.1],
        ),
        margin=dict(l=40, r=40, t=40, b=40),
        hovermode="x unified",
        template="plotly_white",
    )

    return fig


if __name__ == "__main__":
    app.run(debug=True)