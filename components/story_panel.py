import streamlit as st
import pandas as pd
from modules.visualizations import generate_heatmap, generate_difference_heatmap, generate_time_series
from modules.data_loader import get_time_range

def render_story_panel(ds, selected_var, lat, lon):
    """
    Renders a guided 3-step Climate Story walkthrough.
    
    Step 1: Show global heatmap (earliest time)
    Step 2: Highlight warming regions (difference map between earliest and latest)
    Step 3: Show time trend at user-selected location
    """
    st.header("📖 Climate Story")
    st.caption("A guided walkthrough of the climate data in three steps.")
    
    times = get_time_range(ds)
    has_time = times is not None and len(times) > 0
    
    # ============================
    # STEP 1: Global Heatmap
    # ============================
    with st.expander("Step 1: Global Snapshot & Temperature Distribution", expanded=True):
        st.markdown(f"""
This heatmap shows the spatial distribution of **{selected_var}** across the globe. 
Blue regions indicate colder values, while red regions indicate warmer values.
This gives us a sense of the baseline global temperature distribution.
""")
        
        if has_time:
            first_time = times[0]
            try:
                label = pd.to_datetime(first_time).strftime('%Y-%m-%d')
            except:
                label = str(first_time)
            st.info(f"Showing baseline snapshot at: **{label}**")
            fig = generate_heatmap(ds, selected_var, time_index=first_time, selected_lat=lat, selected_lon=lon)
        else:
            fig = generate_heatmap(ds, selected_var, selected_lat=lat, selected_lon=lon)
            
        if fig:
            st.plotly_chart(fig, use_container_width=True, key="story_fig1", config={"displaylogo": False, "scrollZoom": True, "responsive": True})
    
    # ============================
    # STEP 2: Warming Regions
    # ============================
    with st.expander("Step 2: Climate Anomaly & Polar Regions", expanded=False):
        if not has_time or len(times) < 2:
            st.warning("Need at least two time steps to compute warming regions.")
        else:
            first_time = times[0]
            last_time = times[-1]
            
            try:
                t1_label = pd.to_datetime(first_time).strftime('%Y-%m-%d')
                t2_label = pd.to_datetime(last_time).strftime('%Y-%m-%d')
            except:
                t1_label = str(first_time)
                t2_label = str(last_time)
            
            st.markdown(f"""
This **difference map** compares the latest time step ({t2_label}) against the earliest ({t1_label}). 
It highlights climate anomalies, particularly how **polar regions** often experience amplified warming compared to other latitudes.

- 🔴 **Red areas** indicate **warming** (values increased over time)
- 🔵 **Blue areas** indicate **cooling** (values decreased over time)
""")
            
            fig_diff = generate_difference_heatmap(ds, selected_var, first_time, last_time)
            if fig_diff:
                st.plotly_chart(fig_diff, use_container_width=True, key="story_fig2", config={"displaylogo": False, "scrollZoom": True, "responsive": True})
    
    # ============================
    # STEP 3: Time Trend
    # ============================
    with st.expander("Step 3: Time Series Trend", expanded=False):
        if not has_time:
            st.warning("No time dimension available for trend analysis.")
        else:
            st.markdown(f"""
This line chart tracks **{selected_var}** over the entire available time range at a single 
geographic point. It reveals long-term trends, seasonal cycles, and abrupt shifts at that specific location.

The location is controlled by the **Latitude** and **Longitude** selectors in the sidebar.
""")
            
            if lat is not None and lon is not None:
                st.info(f"Showing trend at: **Lat {lat:.2f}°, Lon {lon:.2f}°**")
                fig_ts = generate_time_series(ds, selected_var, lat, lon)
                if fig_ts:
                    st.plotly_chart(fig_ts, use_container_width=True, key="story_fig3", config={"displaylogo": False, "scrollZoom": True, "responsive": True})
            else:
                st.warning("Please set Latitude and Longitude in the sidebar to view the time trend.")
