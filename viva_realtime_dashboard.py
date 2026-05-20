import streamlit as st
import pandas as pd
import plotly.express as px
import time
import pymongo
import os

# ==========================================
# PAGE CONFIG & DYNAMIC DESIGN
# ==========================================
st.set_page_config(
    page_title="RAINWISE | MongoDB Live Dashboard",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #FAFAFA; }
    .metric-card {
        background-color: #1E212B; padding: 20px; border-radius: 10px;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2); border-left: 5px solid #00FF88;
        margin-bottom: 20px;
    }
    .metric-title { font-size: 1.1rem; color: #A0AAB2; margin-bottom: 5px; }
    .metric-value { font-size: 2.2rem; font-weight: bold; color: #00FF88; }
    .header-style {
        text-align: center; background: -webkit-linear-gradient(#00FF88, #00A6FF);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 3.5rem; font-weight: 900; margin-bottom: 0px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="header-style">🍃 MongoDB Live Analytics</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #A0AAB2; font-size: 1.2rem;'>Real-Time Data Visualization directly from MongoDB NoSQL</p>", unsafe_allow_html=True)
st.markdown("---")

# ==========================================
# MONGODB CONNECTION
# ==========================================
@st.cache_resource
def get_mongo_client():
    try:
        return pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
    except:
        return None

client = get_mongo_client()

if not client:
    st.error("MongoDB is currently offline or unreachable at localhost:27017.")
    st.stop()

db = client['rainwise_db']
col_cities = db['city_summaries']

# ==========================================
# LIVE REFRESH LOGIC (Only refreshes UI if new data arrives)
# ==========================================
if 'last_updated_time' not in st.session_state:
    st.session_state.last_updated_time = None

# Create an empty container for the entire UI
ui_container = st.empty()

def render_dashboard():
    # Fetch all data from Mongo
    cursor = col_cities.find({}, {"_id": 0})
    df = pd.DataFrame(list(cursor))
    
    if df.empty:
        st.warning("MongoDB is currently empty. Waiting for live data from pipeline...")
        return
        
    with ui_container.container():
        # Top Metrics
        c1, c2, c3, c4 = st.columns(4)
        latest_time = df['last_updated'].max() if 'last_updated' in df.columns else "N/A"
        avg_risk = df['Flood_Risk_Score'].mean() if 'Flood_Risk_Score' in df.columns else 0
        critical_cities = len(df[df['Risk_Level'] == 'Critical']) if 'Risk_Level' in df.columns else 0
        
        c1.markdown(f'<div class="metric-card"><div class="metric-title">Active MongoDB Docs</div><div class="metric-value">{len(df)}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card"><div class="metric-title">Last Live Sync</div><div class="metric-value" style="font-size: 1.5rem; margin-top: 10px;">{latest_time}</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-card"><div class="metric-title">Avg State Flood Risk</div><div class="metric-value">{avg_risk:.1f}</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="metric-card"><div class="metric-title">Critical Cities</div><div class="metric-value" style="color:#FF007F;">{critical_cities}</div></div>', unsafe_allow_html=True)

        st.markdown("---")
        
        # Row 1 Visuals
        colA, colB = st.columns(2)
        
        with colA:
            st.markdown("#### 🌧️ Live Rainfall radar (MongoDB)")
            if 'latitude' in df.columns and 'longitude' in df.columns and 'rain_mm' in df.columns:
                df_geo = df.dropna(subset=['latitude', 'longitude', 'rain_mm'])
                if not df_geo.empty:
                    fig1 = px.scatter_mapbox(
                        df_geo, lat="latitude", lon="longitude", color="rain_mm", size="rain_mm", 
                        hover_name="city", color_continuous_scale=px.colors.sequential.Tealgrn,
                        size_max=20, zoom=5.5, mapbox_style="carto-darkmatter"
                    )
                    fig1.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="#0E1117", font_color="#FAFAFA")
                    st.plotly_chart(fig1, use_container_width=True)

        with colB:
            st.markdown("#### 🎯 Real-Time Flood Risk Treemap")
            if 'Risk_Level' in df.columns:
                risk_counts = df['Risk_Level'].value_counts().reset_index()
                risk_counts.columns = ['Risk_Level', 'Count']
                fig2 = px.treemap(
                    risk_counts, path=['Risk_Level'], values='Count',
                    color='Risk_Level', color_discrete_map={'Low': '#00FF88', 'Warning': '#FFC107', 'Critical': '#FF007F', 'Unknown': '#555555'},
                    template="plotly_dark"
                )
                fig2.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="#0E1117")
                st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        
        # Row 2 Visuals
        colC, colD = st.columns(2)
        
        with colC:
            st.markdown("#### 💥 Projected Population vs Live Risk")
            st.markdown("*Demonstrating how NoSQL effortlessly merges static demographics with live telemetry.*")
            if 'projected_pop_2026' in df.columns and 'Flood_Risk_Score' in df.columns:
                df_pop = df.dropna(subset=['projected_pop_2026', 'Flood_Risk_Score'])
                if not df_pop.empty:
                    fig3 = px.scatter(
                        df_pop, x='projected_pop_2026', y='Flood_Risk_Score', hover_name='city', 
                        color='Flood_Risk_Score', color_continuous_scale="Inferno", size='projected_pop_2026'
                    )
                    fig3.update_layout(xaxis_title="Projected Population (2026)", yaxis_title="Current Flood Risk Score", 
                                       plot_bgcolor="#0E1117", paper_bgcolor="#0E1117", margin={"r":0,"t":0,"l":0,"b":0})
                    st.plotly_chart(fig3, use_container_width=True)
                    
        with colD:
            st.markdown("#### 📈 Top 10 Most Vulnerable Fast-Growing Cities")
            if 'projected_pop_2026' in df.columns and 'Flood_Risk_Score' in df.columns:
                df_top = df.sort_values(by=['Flood_Risk_Score', 'projected_pop_2026'], ascending=[False, False]).head(10)
                if not df_top.empty:
                    fig4 = px.bar(
                        df_top, x='Flood_Risk_Score', y='city', orientation='h', 
                        color='projected_pop_2026', color_continuous_scale="Oranges"
                    )
                    fig4.update_layout(yaxis={'categoryorder':'total ascending'}, plot_bgcolor="#0E1117", paper_bgcolor="#0E1117", margin={"r":0,"t":0,"l":0,"b":0})
                    st.plotly_chart(fig4, use_container_width=True)

# Main Polling Loop
while True:
    # 1. Check MongoDB for the latest update timestamp
    try:
        latest_doc = col_cities.find_one({}, sort=[("last_updated", pymongo.DESCENDING)])
        current_latest_time = latest_doc.get("last_updated") if latest_doc else None
    except:
        current_latest_time = None
        
    # 2. If new data has arrived (timestamp changed), rerender the dashboard
    if current_latest_time != st.session_state.last_updated_time:
        st.session_state.last_updated_time = current_latest_time
        render_dashboard()
        
    # 3. Sleep briefly before checking again (keeps app responsive without flickering)
    time.sleep(2)
