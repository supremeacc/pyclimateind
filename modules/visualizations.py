import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import pydeck as pdk
import numpy as np
from modules.data_loader import get_spatial_slice, get_location_timeseries

def _prepare_spatial_data(dataset, variable, time_index=None):
    """
    Helper function to extract, subset, and clean spatial data from xarray to pandas.
    Returns the DataFrame and the actual coordinate column names.
    """
    # Handle time slicing using optimized data_loader function
    data = get_spatial_slice(dataset, variable, time_index)
    if data is None:
        return None, None, None
            
    try:
        lat_dim = 'lat' if 'lat' in data.dims else 'latitude' if 'latitude' in data.dims else None
        lon_dim = 'lon' if 'lon' in data.dims else 'longitude' if 'longitude' in data.dims else None
        
        if lat_dim and lon_dim:
            # Downsample the dataset grid to improve map rendering performance
            data = data.isel({lat_dim: slice(None, None, 2), lon_dim: slice(None, None, 2)})
            
        df = data.to_dataframe().reset_index()
        lat_col = 'lat' if 'lat' in df.columns else 'latitude' if 'latitude' in df.columns else None
        lon_col = 'lon' if 'lon' in df.columns else 'longitude' if 'longitude' in df.columns else None
        
        if not lat_col or not lon_col:
            st.error("Dataset missing standard latitude or longitude coordinates ('lat'/'lon' or 'latitude'/'longitude').")
            return None, None, None
            
        df_clean = df.dropna(subset=[variable])
        return df_clean, lat_col, lon_col
    except Exception as e:
        st.error(f"Error extracting spatial data: {e}")
        return None, None, None

def generate_heatmap(dataset, variable, time_index=None, selected_lat=None, selected_lon=None):
    """
    Generate a global heatmap showing climate data distribution using Plotly Heatmap.
    """
    data = get_spatial_slice(dataset, variable, time_index)
    
    if data is None:
        return None
        
    try:
        lat_dim = 'lat' if 'lat' in data.dims else 'latitude' if 'latitude' in data.dims else None
        lon_dim = 'lon' if 'lon' in data.dims else 'longitude' if 'longitude' in data.dims else None
        
        if lat_dim and lon_dim:
            # Downsample the dataset grid to improve map rendering performance
            data = data.isel({lat_dim: slice(None, None, 2), lon_dim: slice(None, None, 2)})
            
        data = data.transpose(lat_dim, lon_dim)
        
        lats = data[lat_dim].values
        lons = data[lon_dim].values
        z_values = data.values
        
        fig = go.Figure(data=go.Heatmap(
            z=z_values,
            x=lons,
            y=lats,
            colorscale='RdBu_r',
            zsmooth='best',
            showscale=True,
            hovertemplate="Latitude: %{y}<br>Longitude: %{x}<br>Value: %{z}<extra></extra>"
        ))
        
        if selected_lat is not None and selected_lon is not None:
            fig.add_trace(go.Scatter(
                x=[selected_lon],
                y=[selected_lat],
                mode='markers',
                marker=dict(
                    color='#38bdf8',  # Contrasting Accent color
                    size=12,
                    line=dict(color='white', width=2)
                ),
                name='Selected Location',
                hovertemplate="Selected: Lat %{y:.2f}, Lon %{x:.2f}<extra></extra>"
            ))
        
        fig.update_layout(
            title=f"Global Heatmap: {variable}",
            xaxis_title="Longitude",
            yaxis_title="Latitude",
            margin={"r": 0, "t": 40, "l": 0, "b": 0}
        )
        return fig
    except Exception as e:
        st.error(f"Error generating Heatmap: {e}")
        return None

def generate_3d_globe(dataset, variable, time_index=None):
    """
    Generate a 3D Earth visualization of climate data using PyDeck.
    Plots data points as colored scatter points on a 3D globe.
    Uses blue for cold values and red for hot values.
    
    Args:
        dataset (xr.Dataset): The climate dataset object.
        variable (str): The climate variable to plot.
        time_index (int or str, optional): The specific time slice to plot.
        
    Returns:
        pdk.Deck: The PyDeck rendering object.
    """
    if dataset is None or variable not in dataset:
        st.error(f"Variable '{variable}' not found in the dataset.")
        return None
        
    data = get_spatial_slice(dataset, variable, time_index)
    if data is None:
        return None

    # 1. Extract latitudes and longitudes
    # 5. Downsample the grid to reduce point count (every 5th point)
    lat_dim = 'lat' if 'lat' in data.dims else 'latitude' if 'latitude' in data.dims else None
    lon_dim = 'lon' if 'lon' in data.dims else 'longitude' if 'longitude' in data.dims else None
    
    if lat_dim and lon_dim:
        data = data.isel(**{lat_dim: slice(None, None, 5), lon_dim: slice(None, None, 5)})
        
    try:
        # 3. Convert to pandas dataframe
        df = data.to_dataframe().reset_index()
        lat_col = lat_dim
        lon_col = lon_dim
        
        if not lat_col or not lon_col:
            st.error("Dataset missing standard latitude or longitude coordinates.")
            return None
            
        # 4. Drop NaN values
        df_clean = df.dropna(subset=[variable]).copy()
        
        # Standardize lon to [-180, 180] for pydeck
        if df_clean[lon_col].max() > 180:
            df_clean[lon_col] = np.where(df_clean[lon_col] > 180, df_clean[lon_col] - 360, df_clean[lon_col])
            
        # Normalize the variable data for styling
        var_min = df_clean[variable].min()
        var_max = df_clean[variable].max()
        # Scale to 0-1 range
        if var_max > var_min:
            df_clean['norm_val'] = (df_clean[variable] - var_min) / (var_max - var_min)
        else:
            df_clean['norm_val'] = 0.5
            
        # Create an RGB color column based on normalized value: Blue(low) -> Red(high)
        df_clean['r'] = (df_clean['norm_val'] * 255).astype(int)
        df_clean['g'] = 50 # Small green injection for midtones
        df_clean['b'] = ((1.0 - df_clean['norm_val']) * 255).astype(int)
        
        # Configure initial PyDeck 3D View (Globe)
        initial_view_state = pdk.ViewState(
            latitude=float(df_clean[lat_col].mean()),
            longitude=float(df_clean[lon_col].mean()),
            zoom=0,
            pitch=45,
            bearing=0
        )
        
        # Configure exactly 1 map visualization view type as "GlobeView"
        view = {"type": "GlobeView", "controller": True}
        
        # Create the ScatterplotLayer
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_clean,
            get_position=[lon_col, lat_col],
            get_fill_color=["r", "g", "b", 200], # With optional transparency
            get_radius=50000, # Controls point size based on map scale
            pickable=True,
            auto_highlight=True,
        )
        
        tooltip = {
            "html": f"<b>{variable}:</b> {{{variable}}}<br/><b>Lat:</b> {{{lat_col}}}<br/><b>Lon:</b> {{{lon_col}}}",
            "style": {"backgroundColor": "steelblue", "color": "white"}
        }
        
        # Render the PyDeck globe
        r = pdk.Deck(
            layers=[layer],
            initial_view_state=initial_view_state,
            views=[view],
            tooltip=tooltip,
            map_style="mapbox://styles/mapbox/dark-v11",
        )
        
        return r
    except Exception as e:
        st.error(f"Error generating 3D Globe: {e}")
        return None

def generate_time_series(dataset, variable, lat, lon):
    """
    Generate a line graph showing how a variable changes over time at a given location.
    """
    ts_data = get_location_timeseries(dataset, variable, lat, lon)
    if ts_data is None:
        return None
        
    try:
        lat_name = 'lat' if 'lat' in ts_data.coords else 'latitude' if 'latitude' in ts_data.coords else None
        lon_name = 'lon' if 'lon' in ts_data.coords else 'longitude' if 'longitude' in ts_data.coords else None
        
        actual_lat = float(ts_data[lat_name].values) if lat_name else lat
        actual_lon = float(ts_data[lon_name].values) if lon_name else lon
        
        df = ts_data.to_dataframe().reset_index()
        
        # Format time for cleaner hovers
        if pd.api.types.is_datetime64_any_dtype(df['time']):
            df['time_str'] = df['time'].dt.strftime('%Y-%m-%d')
        else:
            df['time_str'] = df['time'].astype(str)
            
        fig = px.line(
            df, 
            x='time', 
            y=variable,
            title=f"{variable} Trend at Latitude: {actual_lat:.2f}, Longitude: {actual_lon:.2f}",
            markers=True,
            hover_data={variable: True, 'time': False, 'time_str': True}
        )
        
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title=variable,
            template="plotly_white",
            hovermode="x unified"
        )
        return fig
    except Exception as e:
        st.error(f"Error generating time series: {e}")
        return None

def generate_climate_animation(dataset, variable):
    """
    Generate an animated heatmap showing climate change over the entire time dimension.
    Uses a blue -> red color scale to represent cold to hot values.
    
    Args:
        dataset (xr.Dataset): The climate dataset object.
        variable (str): The climate variable to plot.
        
    Returns:
        plotly.graph_objs._figure.Figure: The Plotly animated figure object.
    """
    if dataset is None or variable not in dataset:
        st.error(f"Variable '{variable}' not found in the dataset.")
        return None
        
    data = dataset[variable]
    
    if 'time' not in data.dims:
        st.warning(f"Variable '{variable}' does not have a time dimension to animate.")
        return None
        
    try:
        # Downsample time if there are too many frames to prevent browser crashes
        time_vals = data.time.values
        time_len = len(time_vals)
        step = max(1, time_len // 50)  # Target ~50 frames max
        
        # Select times at the specified step
        sampled_times = time_vals[0::step]
        data_sampled = data.sel(time=sampled_times, method='nearest')
        
        lat_col = 'lat' if 'lat' in data_sampled.dims else 'latitude' if 'latitude' in data_sampled.dims else None
        lon_col = 'lon' if 'lon' in data_sampled.dims else 'longitude' if 'longitude' in data_sampled.dims else None
        
        if not lat_col or not lon_col:
            st.error("Dataset missing standard latitude or longitude coordinates.")
            return None
            
        # Downsample spatial grid to improve animation rendering performance
        data_sampled = data_sampled.isel({lat_col: slice(None, None, 2), lon_col: slice(None, None, 2)})
            
        # Format the time strings for frame names
        try:
            time_strs = pd.to_datetime(data_sampled.time.values).strftime('%Y-%m-%d').tolist()
        except:
            time_strs = [str(t).split(' ')[0] for t in data_sampled.time.values]
            
        lats = data_sampled[lat_col].values
        lons = data_sampled[lon_col].values
        
        zmin = float(data_sampled.min())
        zmax = float(data_sampled.max())
        
        # Extract first frame
        first_time = data_sampled.time.values[0]
        first_frame = data_sampled.sel(time=first_time, method='nearest').transpose(lat_col, lon_col).values
        
        # 1. Base figure with Heatmap
        fig = go.Figure(
            data=[go.Heatmap(
                z=first_frame,
                x=lons,
                y=lats,
                colorscale='Bluered',
                zmin=zmin,
                zmax=zmax,
                hovertemplate="Latitude: %{y}<br>Longitude: %{x}<br>Value: %{z}<extra></extra>"
            )]
        )
        
        # 2. Build Frames
        frames = []
        for i, t_str in enumerate(time_strs):
            frame_time = data_sampled.time.values[i]
            frame_data = data_sampled.sel(time=frame_time, method='nearest').transpose(lat_col, lon_col).values
            frames.append(
                go.Frame(
                    data=[go.Heatmap(z=frame_data)],
                    name=t_str
                )
            )
        fig.frames = frames
        
        # 3. Add Play Button and Sliders
        fig.update_layout(
            title=f"Climate Animation: {variable} Over Time",
            xaxis_title="Longitude",
            yaxis_title="Latitude",
            margin={"r": 0, "t": 40, "l": 0, "b": 0},
            updatemenus=[dict(
                type="buttons",
                buttons=[
                    dict(label="Play",
                         method="animate",
                         args=[None, {"frame": {"duration": 500, "redraw": True}, "fromcurrent": True}]),
                    dict(label="Pause",
                         method="animate",
                         args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}])
                ],
                showactive=False,
                x=0.1, y=0, xanchor="right", yanchor="top"
            )],
            sliders=[dict(
                active=0,
                yanchor="top", xanchor="left",
                currentvalue={"font": {"size": 20}, "prefix": "Time: ", "visible": True, "xanchor": "right"},
                transition={"duration": 300, "easing": "cubic-in-out"},
                pad={"b": 10, "t": 50},
                len=0.9, x=0.1, y=0,
                steps=[dict(
                    method='animate',
                    args=[[f.name], {"frame": {"duration": 500, "redraw": True}, "mode": "immediate"}],
                    label=f.name
                ) for f in frames]
            )]
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error generating climate animation: {e}")
        return None

def generate_difference_heatmap(dataset, variable, time1, time2):
    """
    Generate a heatmap showing the difference (time2 - time1) for a climate variable.
    """
    data1 = get_spatial_slice(dataset, variable, time1)
    data2 = get_spatial_slice(dataset, variable, time2)
    
    if data1 is None or data2 is None:
        return None
        
    try:
        # Calculate difference
        diff_data = data2 - data1
        
        lat_col = 'lat' if 'lat' in diff_data.dims else 'latitude' if 'latitude' in diff_data.dims else None
        lon_col = 'lon' if 'lon' in diff_data.dims else 'longitude' if 'longitude' in diff_data.dims else None
        
        if not lat_col or not lon_col:
            st.error("Dataset missing standard latitude or longitude coordinates.")
            return None
            
        # Downsample the dataset grid to improve map rendering performance
        diff_data = diff_data.isel({lat_col: slice(None, None, 2), lon_col: slice(None, None, 2)})
            
        diff_data = diff_data.transpose(lat_col, lon_col)
        
        lats = diff_data[lat_col].values
        lons = diff_data[lon_col].values
        z_values = diff_data.values
        
        # Determine max absolute value for symmetric color scale centered at 0
        z_max_abs = np.nanmax(np.abs(z_values))
        
        fig = go.Figure(data=go.Heatmap(
            z=z_values,
            x=lons,
            y=lats,
            colorscale='RdBu_r', # Blue for negative (cooling), Red for positive (warming), centered at white
            zmid=0,
            zmin=-z_max_abs if z_max_abs > 0 else -1,
            zmax=z_max_abs if z_max_abs > 0 else 1,
            hovertemplate=
            "Latitude: %{y}<br>" +
            "Longitude: %{x}<br>" +
            "Difference: %{z:+.2f}<extra></extra>"
        ))
        
        # Format times for title
        try:
            t1_str = pd.to_datetime(time1).strftime('%Y-%m-%d')
            t2_str = pd.to_datetime(time2).strftime('%Y-%m-%d')
        except:
            t1_str = str(time1)
            t2_str = str(time2)
            
        fig.update_layout(
            title=f"Anomaly: {variable} Change ({t2_str} minus {t1_str})",
            xaxis_title="Longitude",
            yaxis_title="Latitude",
            margin={"r": 0, "t": 40, "l": 0, "b": 0},
        )
        return fig
    except Exception as e:
        st.error(f"Error generating difference heatmap: {e}")
        return None

def generate_scattergeo(dataset, variable, time_index=None):
    """
    Generate a global climate visualization using Plotly ScatterGeo.
    """
    df_clean, lat_col, lon_col = _prepare_spatial_data(dataset, variable, time_index)
    
    if df_clean is None:
        return None
        
    try:
        fig = px.scatter_geo(
            df_clean,
            lat=lat_col,
            lon=lon_col,
            color=variable,
            projection="natural earth",
            color_continuous_scale="Bluered",
            hover_data={lat_col: True, lon_col: True, variable: True}
        )
        
        fig.update_layout(
            title=f"Global ScatterGeo: {variable}",
            margin={"r": 0, "t": 40, "l": 0, "b": 0}
        )
        return fig
    except Exception as e:
        st.error(f"Error generating ScatterGeo map: {e}")
        return None
