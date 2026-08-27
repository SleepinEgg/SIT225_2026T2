import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os

# Ensure we are looking in the same directory as the logging script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
COMBINED_FILE = os.path.join(SCRIPT_DIR, "accelerometer_combined.csv")

# Initialize the plot
fig, ax = plt.subplots(figsize=(10, 5))

def animate(i):
    try:
        # Check if file exists to prevent crash on startup
        if not os.path.exists(COMBINED_FILE):
            return

        # Read the latest data
        df = pd.read_csv(COMBINED_FILE, names=["time", "x", "y", "z"])
        
        if df.empty:
            return

        # Convert timestamp to a relative time in seconds for a cleaner X-axis
        df['time'] = pd.to_datetime(df['time'])
        df['seconds'] = (df['time'] - df['time'].iloc[0]).dt.total_seconds()

        # Keep only the last 100 readings for a moving "oscilloscope" effect
        df_recent = df.tail(100)

        # Clear the axis and replot
        ax.clear()
        ax.plot(df_recent['seconds'], df_recent['x'], label='X-axis', color='red', linewidth=2)
        ax.plot(df_recent['seconds'], df_recent['y'], label='Y-axis', color='green', linewidth=2)
        ax.plot(df_recent['seconds'], df_recent['z'], label='Z-axis', color='blue', linewidth=2)

        # Apply formatting
        ax.set_title('Live Smartphone Accelerometer Stream')
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Acceleration (m/s²)')
        ax.legend(loc='upper right')
        ax.grid(True, linestyle='--', alpha=0.6)

    except (pd.errors.EmptyDataError, PermissionError):
        # Ignore errors if the file is being written to at the exact moment of reading
        pass

# Update the chart every 200 milliseconds (0.2 seconds) for near-instant rendering
ani = animation.FuncAnimation(fig, animate, interval=200, cache_frame_data=False)

plt.tight_layout()
plt.show()