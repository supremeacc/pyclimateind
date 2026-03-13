import streamlit as st

from components.sidebar import render_sidebar
from components.heatmap_panel import render_heatmap_panel
from components.timeseries_panel import render_timeseries_panel
from components.comparison_panel import render_comparison_panel
from components.insights_panel import render_insights_panel
from components.story_panel import render_story_panel
from modules.visualizations import generate_climate_animation

# ── Page Config ──
st.set_page_config(
    page_title="PyClimaExplorer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Dark‑Theme Custom CSS ──
st.markdown("""
<style>
    /* ---- Global overrides ---- */
    [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
    }
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #21262d;
    }
    /* Section card wrapper */
    .section-card {
        background: #161b22;
        border: 1px solid #21262d;
        border-radius: 12px;
        padding: 1.5rem 1.8rem;
        margin-bottom: 1.6rem;
    }
    /* Header accent bar */
    .accent-bar {
        height: 3px;
        width: 100%;
        background: linear-gradient(90deg, transparent, #00d2ff, #3a7bd5, transparent);
        box-shadow: 0 0 8px #00d2ff, 0 0 16px #3a7bd5;
        margin-bottom: 2rem;
        border-radius: 2px;
    }
    /* Title styling */
    .hero-title {
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .hero-title h1 {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .hero-title p.subtitle {
        font-size: 1.15rem;
        color: #8b949e;
        margin-top: 0.3rem;
        font-weight: 300;
    }
    .hero-title p.tagline {
        font-size: 0.85rem;
        color: #484f58;
        font-style: italic;
        margin-top: 0;
    }
    /* Section headers */
    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: #e6edf3;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .section-header .icon {
        font-size: 1.4rem;
    }
    /* Subtle dividers */
    hr {
        border: none;
        border-top: 1px solid #21262d;
        margin: 1.5rem 0;
    }
    /* Tab styling tweaks */
    [data-testid="stTabs"] button {
        color: #8b949e !important;
        font-weight: 500;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        color: #00d2ff !important;
        border-bottom-color: #00d2ff !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Hero Header ──
st.title("PYCLIMAEXPLORER")
st.subheader("Climate Intelligence Dashboard")
st.markdown("---")

# ── Session State ──
if 'dataset' not in st.session_state:
    st.session_state.dataset = None

# ── Sidebar Controls ──
selected_var, selected_time, lat, lon = render_sidebar()

# ── Main Content ──
if st.session_state.dataset is not None and selected_var is not None:
    ds = st.session_state.dataset

    # ── Row 1: Global Climate Map ──
    with st.container():
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        render_heatmap_panel(ds, selected_var, selected_time)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Row 2: Time Series and Insights ──
    col1, col2 = st.columns([2, 1])
    with col1:
        with st.container():
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            render_timeseries_panel(ds, selected_var, lat, lon)
            st.markdown('</div>', unsafe_allow_html=True)
            
    with col2:
        with st.container():
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            render_insights_panel(ds, selected_var)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── Row 3: Comparison Mode ──
    with st.container():
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        render_comparison_panel(ds, selected_var)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Row 4: Climate Animation ──
    with st.container():
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header"><span class="icon">⏳</span> Climate Animation</div>', unsafe_allow_html=True)
        st.caption("Animated playback of the dataset over all available time slices.")
        if st.button("▶ Generate Animation", key="anim_btn"):
            with st.spinner("Generating animation frames…"):
                fig_anim = generate_climate_animation(ds, selected_var)
                if fig_anim:
                    st.plotly_chart(fig_anim, use_container_width=True, config={"displaylogo": False, "scrollZoom": True, "responsive": True})
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Footer: Dataset Metadata ──
    with st.expander("📄 Dataset Metadata"):
        st.code(str(ds), language=None)

else:
    # Empty state
    st.markdown("""
    <div style="text-align: center; padding: 6rem 2rem;">
        <p style="font-size: 3rem; margin-bottom: 0.5rem;">🌐</p>
        <h3 style="color: #8b949e; font-weight: 400;">No dataset loaded</h3>
        <p style="color: #484f58;">Upload a <code>.nc</code> file in the sidebar to start exploring climate data.</p>
    </div>
    """, unsafe_allow_html=True)
