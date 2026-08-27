import csv
from datetime import datetime
import os
import time
from collections import deque
import threading
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
from arduino_iot_cloud import ArduinoCloudClient

# ==========================================
# 1. ARDUINO IOT CLOUD CONFIGURATION
# ==========================================
DEVICE_ID = "98d93ae9-1ddc-42fa-818c-2720a66c493a"
SECRET_KEY = "GbyR0MHokilIKyAQMwu3jsGv@"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
START_TIME = time.time()

# ==========================================
# 2. SHARED IN-MEMORY RAM BUFFERS
# ==========================================
MAX_POINTS = 100
time_buffer = deque(maxlen=MAX_POINTS)
x_buffer = deque(maxlen=MAX_POINTS)
y_buffer = deque(maxlen=MAX_POINTS)
z_buffer = deque(maxlen=MAX_POINTS)
data_lock = threading.Lock()

latest_readings = {"x": None, "y": None, "z": None}

def on_axis_update(client, value, axis_name):
    timestamp = datetime.now().isoformat()
    elapsed_sec = round(time.time() - START_TIME, 2)
    latest_readings[axis_name] = value

    # Save to individual CSV file
    file_path_indiv = os.path.join(SCRIPT_DIR, f"accelerometer_{axis_name}.csv")
    with open(file_path_indiv, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, value])
        f.flush()

    # When all 3 axes have updated, save to combined CSV AND push to shared RAM
    if all(val is not None for val in latest_readings.values()):
        file_path_comb = os.path.join(SCRIPT_DIR, "accelerometer_combined.csv")
        with open(file_path_comb, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                latest_readings["x"],
                latest_readings["y"],
                latest_readings["z"],
            ])
            f.flush()

        # Push to shared thread-safe RAM buffer
        with data_lock:
            time_buffer.append(elapsed_sec)
            x_buffer.append(latest_readings["x"])
            y_buffer.append(latest_readings["y"])
            z_buffer.append(latest_readings["z"])

        print(f"Logged Stream -> X: {latest_readings['x']} | Y: {latest_readings['y']} | Z: {latest_readings['z']}")

def start_arduino_client():
    client = ArduinoCloudClient(
        device_id=DEVICE_ID, username=DEVICE_ID, password=SECRET_KEY
    )
    client.register("python_x", on_write=lambda c, v: on_axis_update(c, v, "x"))
    client.register("python_y", on_write=lambda c, v: on_axis_update(c, v, "y"))
    client.register("python_z", on_write=lambda c, v: on_axis_update(c, v, "z"))
    print("Listening for smartphone stream...")
    client.start()

# ==========================================
# 3. DASH WEB DASHBOARD API
# ==========================================
def create_smooth_dash_app(update_interval_ms=100, max_points=100):
    app = Dash(__name__)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[], y=[], mode='lines', name='X-axis', line=dict(color='#EF553B', width=2)))
    fig.add_trace(go.Scatter(x=[], y=[], mode='lines', name='Y-axis', line=dict(color='#00CC96', width=2)))
    fig.add_trace(go.Scatter(x=[], y=[], mode='lines', name='Z-axis', line=dict(color='#636EFA', width=2)))

    fig.update_layout(
        title="Real-Time Smartphone Accelerometer Dashboard",
        xaxis=dict(title="Time (seconds)", showgrid=True),
        yaxis=dict(title="Acceleration (m/s²)", showgrid=True),
        margin=dict(l=40, r=40, t=50, b=40),
        uirevision='constant'
    )

    app.layout = html.Div([
        html.H2("Real-Time Smartphone Accelerometer Dashboard", style={'textAlign': 'center', 'fontFamily': 'sans-serif'}),
        dcc.Graph(id='realtime-graph', figure=fig),
        dcc.Interval(id='fast-interval', interval=update_interval_ms, n_intervals=0)
    ])

    @app.callback(
        Output('realtime-graph', 'extendData'),
        Input('fast-interval', 'n_intervals')
    )
    def update_graph_realtime(n):
        with data_lock:
            if not time_buffer:
                return [dict(x=[], y=[]), [0, 1, 2], max_points]
            
            latest_t = time_buffer[-1]
            latest_x = x_buffer[-1]
            latest_y = y_buffer[-1]
            latest_z = z_buffer[-1]

        return [
            dict(
                x=[[latest_t], [latest_t], [latest_t]],
                y=[[latest_x], [latest_y], [latest_z]]
            ),
            [0, 1, 2],
            max_points
        ]

    return app

# ==========================================
# 4. EXECUTION
# ==========================================
if __name__ == "__main__":
    # Launch Arduino Cloud listener in a background thread
    cloud_thread = threading.Thread(target=start_arduino_client, daemon=True)
    cloud_thread.start()

    # Launch Dash Server on main thread
    dash_app = create_smooth_dash_app(update_interval_ms=100)
    dash_app.run(debug=False, port=8050)