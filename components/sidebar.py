import streamlit as st
import tempfile
import pandas as pd
import os
import glob
from modules.data_loader import load_dataset, get_available_variables, get_time_range

def render_sidebar():
    """Renders the sidebar controls and returns selected values."""
    
    # Custom CSS to reduce sidebar padding
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                padding-top: 1rem;
                padding-bottom: 1rem;
            }
            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
                margin-bottom: 0rem;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize datasets dictionary in session state to handle multiple datasets
    if 'datasets' not in st.session_state:
        st.session_state.datasets = {}
        
        # Scan local data folder for existing datasets
        local_files = glob.glob(os.path.join("data", "*.nc"))
        for file_path in local_files:
            file_name = os.path.basename(file_path)
            ds = load_dataset(file_path)
            if ds is not None:
                st.session_state.datasets[file_name] = ds
    
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # --- DATA SECTION ---
        st.markdown("### 📊 DATA")
        
        # 1. Provide an upload mechanism
        uploaded_file = st.file_uploader("Upload NetCDF file (.nc)", type=['nc'], label_visibility="collapsed")
        
        # Handle file upload and add it to our datasets collection
        if uploaded_file is not None:
            if uploaded_file.name not in st.session_state.datasets:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".nc") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    file_path = tmp.name
                    
                try:
                    ds = load_dataset(file_path)
                    if ds is not None:
                        st.session_state.datasets[uploaded_file.name] = ds
                        st.success(f"Loaded {uploaded_file.name}")
                finally:
                    pass
                    
        # 2. Allow switching between loaded datasets (local and uploaded)
        available_datasets = list(st.session_state.datasets.keys())
        
        if available_datasets:
            selected_dataset_name = st.selectbox("Select Dataset", available_datasets, index=0)
            st.session_state.dataset = st.session_state.datasets[selected_dataset_name]
        else:
            st.info("Upload a dataset or place .nc files in the 'data/' folder.")
            st.session_state.dataset = None

        # Default returned values
        selected_var = None
        selected_time = None
        lat = None
        lon = None

        if st.session_state.dataset is not None:
            st.divider()
            ds = st.session_state.dataset
            
            # --- VARIABLE SECTION ---
            st.markdown("### 🔬 VARIABLE")
            variables = get_available_variables(ds)
            
            if not variables:
                st.warning("No valid variables found.")
            else:
                selected_var = st.selectbox("Select Variable", variables, label_visibility="collapsed")
                
                st.divider()
                
                # --- TIME SECTION ---
                st.markdown("### ⏳ TIME")
                times = get_time_range(ds)
                
                if len(times) > 0:
                    try:
                        formatted_times = pd.to_datetime(times).strftime('%Y-%m-%d %H:%M:%S')
                        selected_time_idx = st.select_slider(
                            "Select Time", 
                            options=range(len(times)), 
                            format_func=lambda x: formatted_times[x],
                            label_visibility="collapsed"
                        )
                        selected_time = times[selected_time_idx]
                    except Exception:
                        selected_time_idx = st.select_slider("Select Time", options=range(len(times)), label_visibility="collapsed")
                        selected_time = times[selected_time_idx]
                
                st.divider()
                
                # --- LOCATION SECTION ---
                st.markdown("### 📍 LOCATION")
                lat_name = 'lat' if 'lat' in ds.dims or 'lat' in ds.coords else 'latitude' if 'latitude' in ds.dims or 'latitude' in ds.coords else None
                lon_name = 'lon' if 'lon' in ds.dims or 'lon' in ds.coords else 'longitude' if 'longitude' in ds.dims or 'longitude' in ds.coords else None
                
                if lat_name and lon_name:
                    lat_min, lat_max = float(ds[lat_name].min()), float(ds[lat_name].max())
                    lon_min, lon_max = float(ds[lon_name].min()), float(ds[lon_name].max())
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        lat = st.number_input("Lat", min_value=lat_min, max_value=lat_max, value=(lat_min+lat_max)/2)
                    with col2:
                        lon = st.number_input("Lon", min_value=lon_min, max_value=lon_max, value=(lon_min+lon_max)/2)
                        
    return selected_var, selected_time, lat, lon
