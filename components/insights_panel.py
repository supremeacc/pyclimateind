import streamlit as st
from modules.analysis import compute_climate_insights

def render_insights_panel(ds, selected_var):
    """Renders formatted summary statistics for the selected climate variable."""
    st.markdown('<div class="section-header">📊 Climate Insights</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Global summary statistics for the selected variable.</div>', unsafe_allow_html=True)
    with st.spinner("Computing global statistics..."):
        insights = compute_climate_insights(ds, selected_var)
        
    if insights is None:
        st.warning("Could not compute insights for this variable.")
        return
        
    st.markdown(f"""
- 🌍 **Global Average**: `{insights['global_avg']:.4f}`
- 🔺 **Maximum Value**: `{insights['max_value']:.4f}` at **{insights['max_location']}**
- 🔻 **Minimum Value**: `{insights['min_value']:.4f}` at **{insights['min_location']}**
""")
    
    if insights.get('largest_change') is not None:
        change = insights['largest_change']
        direction = "📈 Increase" if change > 0 else "📉 Decrease"
        st.markdown(f"- ⚡ **Largest Step Change**: `{change:+.4f}` ({direction}) between **{insights['largest_change_times']}**")
    else:
        st.markdown("- ⚡ **Largest Step Change**: _No time dimension available_")
