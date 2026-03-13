# PyClimaExplorer – Climate Data Visualization Dashboard

PyClimaExplorer is an interactive, web-based tool designed to help researchers, students, and the general public visualize and analyze NetCDF (`.nc`) climate datasets.

## Project Structure

```text
pyclimaexplorer/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependency list
├── README.md              # Project documentation
├── data/
│   └── sample.nc          # Directory to place sample NetCDF data
├── modules/
│   ├── data_loader.py     # Functions to load and parse NetCDF datasets using xarray
│   └── visualizer.py      # Functions to generate Plotly spatial/temporal visualizations
└── utils/
    └── helpers.py         # Utility functions (unit conversions, anomalies, etc.)
```

## Features
- **Dataset Loading:** Easily upload or access NetCDF data.
- **Variable Selector:** Dynamically choose available variables (e.g., surface temperature, precipitation, wind speed).
- **Time Range Slider:** Browse data variations across different time slices.
- **Spatial Visualization:** View a global interactive heatmap using Plotly.
- **Temporal Visualization:** Select specific coordinates to generate a time series line chart.

## Prerequisites
- **Python 3.9+**
- Visual Studio Code or any modern code editor.

## Installation

1. **Clone or download** this repository.
2. Navigate to the project folder (`pyclimaexplorer/`).
3. **Optional:** Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate       # macOS/Linux
   venv\Scripts\activate          # Windows
   ```
4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the Streamlit server:
   ```bash
   streamlit run app.py
   ```
2. The application will open automatically in your browser (usually at `http://localhost:8501`).
3. **Upload** a `.nc` dataset via the sidebar. If you don't have one, you can place test files in the `data/` directory and modify the loader to read them directly.
4. Select a variable, adjust the time slider, and explore the global map! Switch to the **Time Series Trend** tab to analyze specific location data over time.

## Data Details
- Ensure your NetCDF files contain standard spatial and temporal dimension structures: `time`, `latitude`/`lat`, and `longitude`/`lon`.

## Author
Developed during hackathon.
