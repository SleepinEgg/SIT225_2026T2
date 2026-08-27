import os
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go

def create_smooth_dash_app(
    data_source_path,
    columns=['x', 'y', 'z'],
    time_col='time',
    max_points=50,
    update_interval_ms=200,
    title="Live Accelerometer Stream"
):
    app = Dash(__name__)

    app.layout = html.Div([
        html.H2(title, style={'textAlign': 'center', 'fontFamily': 'sans-serif'}),
        dcc.Graph(id='live-stream-graph'),
        dcc.Interval(
            id='graph-update-interval',
            interval=update_interval_ms,
            n_intervals=0
        )
    ])

    @app.callback(
        Output('live-stream-graph', 'figure'),
        Input('graph-update-interval', 'n_intervals')
    )
    def update_graph_smoothly(n):
        fig = go.Figure()

        # Check if file exists
        if not os.path.exists(data_source_path):
            fig.add_annotation(text=f"Waiting for CSV: {os.path.basename(data_source_path)}...",
                               showarrow=False, font=dict(size=16))
            return fig

        try:
            # Read CSV file
            df = pd.read_csv(data_source_path, names=[time_col] + columns)
            if df.empty or len(df) == 0:
                fig.add_annotation(text="CSV is empty. Waiting for sensor data...", showarrow=False)
                return fig

            # Convert timestamps safely
            df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
            df = df.dropna(subset=[time_col])
            
            # Calculate elapsed time in seconds
            df['elapsed_sec'] = (df[time_col] - df[time_col].iloc[0]).dt.total_seconds()
            
            # Keep sliding window of latest points
            df_recent = df.tail(max_points)

            # Add continuous lines
            color_map = {'x': '#EF553B', 'y': '#00CC96', 'z': '#636EFA'}
            for col in columns:
                if col in df_recent.columns:
                    fig.add_trace(go.Scatter(
                        x=df_recent['elapsed_sec'],
                        y=pd.to_numeric(df_recent[col], errors='coerce'),
                        mode='lines',
                        name=col.upper(),
                        line=dict(width=2, color=color_map.get(col, None))
                    ))

            fig.update_layout(
                xaxis=dict(title="Time (seconds)", showgrid=True),
                yaxis=dict(title="Acceleration (m/s²)", showgrid=True),
                margin=dict(l=40, r=40, t=30, b=40),
                uirevision='constant'  # Prevents zoom/pan resetting on every live update
            )

        except Exception as e:
            print(f"Error reading stream: {e}")
            fig.add_annotation(text=f"Data Error: {e}", showarrow=False)

        return fig

    return app

if __name__ == "__main__":
    # Ensure relative path resolution matches your folder execution
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
    csv_file = os.path.join(SCRIPT_DIR, "accelerometer_combined.csv")
    
    dash_app = create_smooth_dash_app(
        data_source_path=csv_file,
        columns=['x', 'y', 'z'],
        update_interval_ms=100
    )
    dash_app.run(debug=True, port=8050)