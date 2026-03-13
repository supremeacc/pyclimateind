import streamlit as st
from modules.visualizations import generate_time_series

def render_timeseries_panel(ds, selected_var, lat, lon):
    """Renders the right visualization panel for time series analysis."""
    st.markdown('<div class="section-header">📈 Time Series</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-desc">Temporal evolution of **{selected_var}** at the selected location.</div>', unsafe_allow_html=True)
    
    if lat is not None and lon is not None:
        fig_ts = generate_time_series(ds, selected_var, lat, lon)
        if fig_ts:
            st.plotly_chart(fig_ts, use_container_width=True, config={"displaylogo": False, "scrollZoom": True, "responsive": True})
    else:
        st.warning("Missing latitude/longitude coordinates.")
