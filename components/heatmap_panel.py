import streamlit as st
from modules.visualizations import generate_heatmap

def render_heatmap_panel(ds, selected_var, selected_time, lat=None, lon=None):
    """Renders the central heatmap visualization."""
    st.markdown('<div class="section-header">🌍 Global Heatmap</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-desc">Spatial distribution of **{selected_var}** at the selected time slice.</div>', unsafe_allow_html=True)
    with st.spinner("Generating 2D heatmap..."):
        fig_map = generate_heatmap(ds, selected_var, time_index=selected_time, selected_lat=lat, selected_lon=lon)
        if fig_map:
            st.plotly_chart(fig_map, use_container_width=True, config={"displaylogo": False, "scrollZoom": True, "responsive": True})
