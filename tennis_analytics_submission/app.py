"""
Tennis Analytics Explorer - Main Streamlit Application.
Title: "Game Analytics: Unlocking Tennis Data with Sportradar API"
Features 7 comprehensive analytical views, Plotly visualizations, safe SQL console,
and full error resilience.
"""

import os
import sys
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import text

# Configure Streamlit page settings
st.set_page_config(
    page_title="Tennis Analytics Explorer",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import local modules
from db import (
    check_connection,
    execute_query_df,
    execute_read_only_query,
    get_table_names,
    get_table_schema_df,
    sanitize_database_url
)
from config import DATABASE_URL, SPORTRADAR_API_KEY
from run_etl import run_all_etl

# Custom CSS for Premium Sports Analytics Theme
st.markdown("""
<style>
    /* Global styles */
    .stApp {
        background-color: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Hero header */
    .hero-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #064e3b 100%);
        color: white;
        padding: 2.2rem 2.5rem;
        border-radius: 14px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.25);
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin: 0;
        color: #ffffff;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #94a3b8;
        margin-top: 0.5rem;
        margin-bottom: 1rem;
    }
    .badge-live {
        background-color: #065f46;
        color: #34d399;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 9999px;
        display: inline-block;
        border: 1px solid #10b981;
    }
    .badge-ref {
        background-color: #1e3a5f;
        color: #60a5fa;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 9999px;
        display: inline-block;
        border: 1px solid #3b82f6;
    }

    /* Metric Cards */
    .metric-card {
        background: white;
        padding: 1.4rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.06);
    }
    .metric-label {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 0.3rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #0f172a;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #10b981;
        margin-top: 0.2rem;
    }

    /* Custom Table Style */
    div[data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# Application State Initialization
if "last_refresh_time" not in st.session_state:
    st.session_state.last_refresh_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Check Database Connection
db_healthy, db_msg = check_connection()

# Navigation Sidebar
with st.sidebar:
    st.markdown("### 🎾 Tennis Analytics Explorer")
    st.markdown(
        f"<span style='font-size:0.85rem; color:#64748b;'>Sportradar API & SQL College Project</span>", 
        unsafe_allow_html=True
    )
    st.markdown("---")

    selected_page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Competition Explorer",
            "Venues & Complexes",
            "Competitor Search",
            "Country Analysis",
            "Leaderboards",
            "SQL Query Console"
        ],
        index=0
    )

    st.markdown("---")
    st.markdown("#### System & Data Status")
    
    # DB Status Indicator
    if db_healthy:
        st.success("🟢 Database Connected")
    else:
        st.error("🔴 Database Disconnected")
        st.caption(f"Error: {db_msg}")

    # API Key status
    has_api_key = bool(SPORTRADAR_API_KEY and SPORTRADAR_API_KEY != "your_sportradar_api_key_here")
    if has_api_key:
        st.markdown("<span class='badge-live'>LIVE SPORTRADAR API</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span class='badge-ref'>VERIFIED REFERENCE DATA</span>", unsafe_allow_html=True)

    st.caption(f"Last Refreshed: {st.session_state.last_refresh_time}")

    if st.button("🔄 Refresh Data (Run ETL)", use_container_width=True):
        with st.spinner("Running ETL Pipeline..."):
            success = run_all_etl(init_first=False)
            st.session_state.last_refresh_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if success:
                st.success("Data refreshed successfully!")
            else:
                st.warning("Data refresh completed with notices.")
            st.rerun()


# ==============================================================================
# Helper Functions for Data Access
# ==============================================================================
@st.cache_data(ttl=60)
def load_kpis():
    """Fetches high-level metrics safely."""
    try:
        q_counts = """
        SELECT 
            (SELECT COUNT(*) FROM Competitors) AS total_competitors,
            (SELECT COUNT(*) FROM Competitions) AS total_competitions,
            (SELECT COUNT(*) FROM Venues) AS total_venues,
            (SELECT COUNT(*) FROM Complexes) AS total_complexes,
            (SELECT COUNT(DISTINCT country) FROM Competitors WHERE country IS NOT NULL) AS total_countries,
            (SELECT COALESCE(MAX(points), 0) FROM Competitor_Rankings) AS max_points
        """
        df = execute_query_df(q_counts)
        return df.iloc[0].to_dict()
    except Exception as e:
        return {
            "total_competitors": 0, "total_competitions": 0, "total_venues": 0,
            "total_complexes": 0, "total_countries": 0, "max_points": 0
        }

@st.cache_data(ttl=60)
def load_competitions_data():
    """
    CRITICAL FIX for KeyError: 'category_name'.
    Guarantees that category_name is ALWAYS joined and aliased properly.
    """
    query = """
    SELECT 
        c.id AS competition_id,
        c.name AS competition_name,
        COALESCE(cat.name, 'Uncategorized') AS category_name,
        COALESCE(c.gender, 'Unspecified') AS gender,
        COALESCE(c.type, 'Standard') AS competition_type
    FROM Competitions c
    LEFT JOIN Categories cat ON c.category_id = cat.id
    ORDER BY c.name ASC
    """
    try:
        return execute_query_df(query)
    except Exception as e:
        st.error(f"Error querying competitions: {e}")
        return pd.DataFrame(columns=["competition_id", "competition_name", "category_name", "gender", "competition_type"])

@st.cache_data(ttl=60)
def load_complexes_and_venues():
    """Queries complexes and joined venues."""
    query = """
    SELECT 
        v.id AS venue_id,
        v.name AS venue_name,
        c.name AS complex_name,
        COALESCE(v.city_name, 'Unknown City') AS city_name,
        COALESCE(v.country_name, 'Unknown Country') AS country_name,
        COALESCE(v.timezone, 'UTC') AS timezone
    FROM Venues v
    LEFT JOIN Complexes c ON v.complex_id = c.id
    ORDER BY c.name ASC, v.name ASC
    """
    try:
        return execute_query_df(query)
    except Exception as e:
        st.error(f"Error querying venues: {e}")
        return pd.DataFrame(columns=["venue_id", "venue_name", "complex_name", "city_name", "country_name", "timezone"])

@st.cache_data(ttl=60)
def load_rankings_leaderboard():
    """Queries leaderboard rankings."""
    query = """
    SELECT 
        r.rank,
        c.name AS competitor_name,
        COALESCE(c.country, 'Unknown') AS country,
        COALESCE(c.country_code, 'UNK') AS country_code,
        r.points,
        r.movement,
        r.competitions_played,
        r.ranking_type
    FROM Competitor_Rankings r
    JOIN Competitors c ON r.competitor_id = c.id
    ORDER BY r.rank ASC
    """
    try:
        return execute_query_df(query)
    except Exception as e:
        st.error(f"Error querying rankings: {e}")
        return pd.DataFrame(columns=["rank", "competitor_name", "country", "country_code", "points", "movement", "competitions_played", "ranking_type"])


# ==============================================================================
# Page Header Banner Component
# ==============================================================================
def render_header(title: str, subtitle: str):
    source_badge = "<span class='badge-live'>Sportradar Live API</span>" if has_api_key else "<span class='badge-ref'>Verified Reference Dataset</span>"
    st.markdown(f"""
    <div class="hero-container">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
            <div>
                <h1 class="hero-title">{title}</h1>
                <p class="hero-subtitle">{subtitle}</p>
            </div>
            <div>
                {source_badge}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# PAGE 1: DASHBOARD
# ==============================================================================
if selected_page == "Dashboard":
    render_header(
        "Game Analytics: Tennis Data Explorer",
        "Interactive sports intelligence analyzing competitions, venues, and global doubles rankings from Sportradar API"
    )

    if not db_healthy:
        st.error(f"Cannot connect to the database: {db_msg}")
        st.info("Tip: Run `python run_etl.py --init-db` in your terminal to initialize your database.")
    else:
        kpis = load_kpis()

        # KPI Metrics Row
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Competitors</div>
                <div class="metric-value">{kpis['total_competitors']}</div>
                <div class="metric-sub">Ranked Doubles Players</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Competitions</div>
                <div class="metric-value">{kpis['total_competitions']}</div>
                <div class="metric-sub">Grand Slams & Tours</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Venues</div>
                <div class="metric-value">{kpis['total_venues']}</div>
                <div class="metric-sub">Registered Courts</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Complexes</div>
                <div class="metric-value">{kpis['total_complexes']}</div>
                <div class="metric-sub">Tennis Facilities</div>
            </div>
            """, unsafe_allow_html=True)
        with col5:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Countries</div>
                <div class="metric-value">{kpis['total_countries']}</div>
                <div class="metric-sub">Nations Represented</div>
            </div>
            """, unsafe_allow_html=True)
        with col6:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Top Points</div>
                <div class="metric-value">{kpis['max_points']:,}</div>
                <div class="metric-sub">World #1 Ranking Score</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

        # Overview Visuals & Leaderboard Preview
        c_left, c_right = st.columns([1.1, 0.9])

        with c_left:
            st.subheader("Top-Ranked Competitors Preview")
            df_rank = load_rankings_leaderboard()
            if not df_rank.empty:
                display_df = df_rank[["rank", "competitor_name", "country", "points", "movement"]].head(8)
                display_df = display_df.rename(columns={
                    "rank": "Rank",
                    "competitor_name": "Player Name",
                    "country": "Country",
                    "points": "Points",
                    "movement": "Movement"
                })
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                st.info("No competitor ranking data found in database. Run ETL to populate.")

        with c_right:
            st.subheader("Competitions by Category")
            df_comp = load_competitions_data()
            if not df_comp.empty and "category_name" in df_comp.columns:
                cat_counts = df_comp["category_name"].value_counts().reset_index()
                cat_counts.columns = ["Category", "Count"]
                fig = px.pie(
                    cat_counts,
                    names="Category",
                    values="Count",
                    hole=0.45,
                    color_discrete_sequence=px.colors.qualitative.Prism
                )
                fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=300)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No competition categories found. Run ETL to populate.")


# ==============================================================================
# PAGE 2: COMPETITION EXPLORER
# ==============================================================================
elif selected_page == "Competition Explorer":
    render_header(
        "Competition Explorer",
        "Browse Grand Slams, Masters 1000, and Tour events with safe category and gender filters"
    )

    df_comp = load_competitions_data()

    if df_comp.empty:
        st.warning("No competitions currently loaded. Click 'Refresh Data' in the sidebar to populate.")
    else:
        # Search & Filters
        f1, f2, f3 = st.columns([1.5, 1, 1])
        with f1:
            search_query = st.text_input("🔍 Search Competition Name", "").strip().lower()
        with f2:
            categories = ["All Categories"] + sorted(list(df_comp["category_name"].dropna().unique()))
            selected_cat = st.selectbox("Category Filter", categories)
        with f3:
            genders = ["All Genders"] + sorted(list(df_comp["gender"].dropna().unique()))
            selected_gender = st.selectbox("Gender Filter", genders)

        # Apply filtering
        filtered_df = df_comp.copy()
        if search_query:
            filtered_df = filtered_df[filtered_df["competition_name"].str.lower().str.contains(search_query)]
        if selected_cat != "All Categories":
            filtered_df = filtered_df[filtered_df["category_name"] == selected_cat]
        if selected_gender != "All Genders":
            filtered_df = filtered_df[filtered_df["gender"] == selected_gender]

        st.markdown(f"**Showing {len(filtered_df)} of {len(df_comp)} competitions**")

        # Table Display
        st.dataframe(
            filtered_df.rename(columns={
                "competition_id": "Sportradar ID",
                "competition_name": "Competition Name",
                "category_name": "Category",
                "gender": "Gender",
                "competition_type": "Format"
            }),
            use_container_width=True,
            hide_index=True
        )

        # Visual Distribution
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        st.subheader("Tournament Distribution by Category & Gender")
        
        grouped = filtered_df.groupby(["category_name", "gender"]).size().reset_index(name="Count")
        if not grouped.empty:
            fig = px.bar(
                grouped,
                x="category_name",
                y="Count",
                color="gender",
                barmode="group",
                color_discrete_map={"men": "#0f766e", "women": "#0284c7", "mixed": "#f59e0b", "unspecified": "#64748b"},
                labels={"category_name": "Tournament Category", "Count": "Number of Events"}
            )
            fig.update_layout(margin=dict(t=20, b=40, l=20, r=20), height=350)
            st.plotly_chart(fig, use_container_width=True)


# ==============================================================================
# PAGE 3: VENUES & COMPLEXES
# ==============================================================================
elif selected_page == "Venues & Complexes":
    render_header(
        "Tennis Venues & Stadium Complexes",
        "Relational exploration of major international tennis facilities and individual courts"
    )

    df_venues = load_complexes_and_venues()
    if df_venues.empty:
        st.warning("No complexes or venues loaded. Click 'Refresh Data' in the sidebar.")
    else:
        v_col1, v_col2 = st.columns([1.5, 1])
        with v_col1:
            venue_search = st.text_input("🔍 Search Venue or Complex Name", "").strip().lower()
        with v_col2:
            complex_filter = ["All Complexes"] + sorted(list(df_venues["complex_name"].dropna().unique()))
            sel_complex = st.selectbox("Filter by Complex", complex_filter)

        filtered_v = df_venues.copy()
        if venue_search:
            filtered_v = filtered_v[
                filtered_v["venue_name"].str.lower().str.contains(venue_search) |
                filtered_v["complex_name"].str.lower().str.contains(venue_search)
            ]
        if sel_complex != "All Complexes":
            filtered_v = filtered_v[filtered_v["complex_name"] == sel_complex]

        c1, c2 = st.columns([1.2, 0.8])
        with c1:
            st.subheader(f"Registered Courts & Venues ({len(filtered_v)})")
            st.dataframe(
                filtered_v.rename(columns={
                    "venue_name": "Court / Venue",
                    "complex_name": "Parent Facility / Complex",
                    "city_name": "City",
                    "country_name": "Country",
                    "timezone": "Timezone"
                })[["Court / Venue", "Parent Facility / Complex", "City", "Country", "Timezone"]],
                use_container_width=True,
                hide_index=True
            )

        with c2:
            st.subheader("Venues per Complex")
            venues_per_complex = df_venues["complex_name"].value_counts().reset_index()
            venues_per_complex.columns = ["Complex", "Venues"]
            fig_v = px.bar(
                venues_per_complex,
                x="Venues",
                y="Complex",
                orientation="h",
                color="Venues",
                color_continuous_scale="Viridis"
            )
            fig_v.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(t=10, b=20, l=10, r=10), height=350)
            st.plotly_chart(fig_v, use_container_width=True)


# ==============================================================================
# PAGE 4: COMPETITOR SEARCH
# ==============================================================================
elif selected_page == "Competitor Search":
    render_header(
        "Competitor Search & Profile Inspector",
        "Look up tennis athletes, inspect world ranking stats, points, and ranking movement"
    )

    df_rank = load_rankings_leaderboard()
    if df_rank.empty:
        st.warning("No competitor ranking data found.")
    else:
        cs1, cs2 = st.columns([2, 1])
        with cs1:
            player_query = st.text_input("🔍 Search Competitor Name", "").strip().lower()
        with cs2:
            country_options = ["All Countries"] + sorted(list(df_rank["country"].dropna().unique()))
            sel_country = st.selectbox("Country Filter", country_options)

        df_filtered = df_rank.copy()
        if player_query:
            df_filtered = df_filtered[df_filtered["competitor_name"].str.lower().str.contains(player_query)]
        if sel_country != "All Countries":
            df_filtered = df_filtered[df_filtered["country"] == sel_country]

        st.markdown(f"Found **{len(df_filtered)}** competitors matching criteria.")

        if not df_filtered.empty:
            for _, player in df_filtered.iterrows():
                with st.expander(f"🏅 #{player['rank']} - {player['competitor_name']} ({player['country']})", expanded=False):
                    p1, p2, p3, p4 = st.columns(4)
                    with p1:
                        st.metric("World Rank", f"#{player['rank']}")
                    with p2:
                        st.metric("Ranking Points", f"{player['points']:,}")
                    with p3:
                        mov = player["movement"]
                        st.metric("Weekly Movement", f"{mov:+d}" if mov != 0 else "0", delta=mov if mov != 0 else None)
                    with p4:
                        st.metric("Tournaments Played", player.get("competitions_played", "N/A"))
        else:
            st.info("No competitors found matching your search terms.")


# ==============================================================================
# PAGE 5: COUNTRY ANALYSIS
# ==============================================================================
elif selected_page == "Country Analysis":
    render_header(
        "Country Performance Analytics",
        "Examine national tennis representation, total points, and average player strength"
    )

    try:
        q_country = """
        SELECT 
            COALESCE(c.country, 'Unknown') AS country,
            c.country_code,
            COUNT(c.id) AS competitor_count,
            SUM(r.points) AS total_points,
            ROUND(AVG(r.points), 1) AS avg_points,
            MIN(r.rank) AS best_rank
        FROM Competitors c
        JOIN Competitor_Rankings r ON c.id = r.competitor_id
        GROUP BY c.country, c.country_code
        ORDER BY total_points DESC
        """
        df_country = execute_query_df(q_country)

        if df_country.empty:
            st.warning("No country data available. Run ETL to populate.")
        else:
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Total Ranking Points by Nation")
                fig_pts = px.bar(
                    df_country.head(10),
                    x="country",
                    y="total_points",
                    color="total_points",
                    color_continuous_scale="Emrld",
                    labels={"country": "Country", "total_points": "Total Ranking Points"}
                )
                fig_pts.update_layout(margin=dict(t=20, b=40, l=20, r=20), height=350)
                st.plotly_chart(fig_pts, use_container_width=True)

            with c2:
                st.subheader("Competitor Count by Nation")
                fig_cnt = px.bar(
                    df_country.head(10),
                    x="country",
                    y="competitor_count",
                    color="competitor_count",
                    color_continuous_scale="Blues",
                    labels={"country": "Country", "competitor_count": "Players"}
                )
                fig_cnt.update_layout(margin=dict(t=20, b=40, l=20, r=20), height=350)
                st.plotly_chart(fig_cnt, use_container_width=True)

            st.markdown("### Country Summary Table")
            st.dataframe(
                df_country.rename(columns={
                    "country": "Country",
                    "country_code": "Code",
                    "competitor_count": "Players Count",
                    "total_points": "Total Points",
                    "avg_points": "Average Points",
                    "best_rank": "Best World Rank"
                }),
                use_container_width=True,
                hide_index=True
            )
    except Exception as e:
        st.error(f"Error loading country analysis: {e}")


# ==============================================================================
# PAGE 6: LEADERBOARDS
# ==============================================================================
elif selected_page == "Leaderboards":
    render_header(
        "Doubles World Leaderboard",
        "Official rankings standings with filtering, podium highlights, and CSV export"
    )

    df_rank = load_rankings_leaderboard()
    if df_rank.empty:
        st.warning("No ranking data found in database. Run ETL.")
    else:
        lb1, lb2, lb3 = st.columns([1, 1.5, 1])
        with lb1:
            tier_limit = st.selectbox("Display Tier", [10, 25, 50, 100], index=1)
        with lb2:
            lb_search = st.text_input("Filter by Player Name", "")
        with lb3:
            lb_country = st.selectbox("Filter Country", ["All Countries"] + sorted(list(df_rank["country"].unique())))

        df_display = df_rank.copy()
        if lb_search:
            df_display = df_display[df_display["competitor_name"].str.lower().str.contains(lb_search.lower())]
        if lb_country != "All Countries":
            df_display = df_display[df_display["country"] == lb_country]

        df_display = df_display.head(tier_limit)

        # Highlight Top 3 Podium Cards if in top 10
        if tier_limit >= 3 and len(df_display) >= 3 and not lb_search and lb_country == "All Countries":
            p1, p2, p3 = st.columns(3)
            with p1:
                top1 = df_display.iloc[0]
                st.markdown(f"""
                <div class="metric-card" style="border-top: 4px solid #f59e0b;">
                    <div class="metric-label">🥇 World #1</div>
                    <div style="font-size: 1.3rem; font-weight: 700; color: #0f172a;">{top1['competitor_name']}</div>
                    <div style="color: #64748b; font-size: 0.9rem;">{top1['country']} • {top1['points']:,} pts</div>
                </div>
                """, unsafe_allow_html=True)
            with p2:
                top2 = df_display.iloc[1]
                st.markdown(f"""
                <div class="metric-card" style="border-top: 4px solid #94a3b8;">
                    <div class="metric-label">🥈 World #2</div>
                    <div style="font-size: 1.3rem; font-weight: 700; color: #0f172a;">{top2['competitor_name']}</div>
                    <div style="color: #64748b; font-size: 0.9rem;">{top2['country']} • {top2['points']:,} pts</div>
                </div>
                """, unsafe_allow_html=True)
            with p3:
                top3 = df_display.iloc[2]
                st.markdown(f"""
                <div class="metric-card" style="border-top: 4px solid #b45309;">
                    <div class="metric-label">🥉 World #3</div>
                    <div style="font-size: 1.3rem; font-weight: 700; color: #0f172a;">{top3['competitor_name']}</div>
                    <div style="color: #64748b; font-size: 0.9rem;">{top3['country']} • {top3['points']:,} pts</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

        st.dataframe(
            df_display.rename(columns={
                "rank": "Rank",
                "competitor_name": "Player Name",
                "country": "Country",
                "country_code": "Code",
                "points": "Ranking Points",
                "movement": "Movement",
                "competitions_played": "Events Played"
            })[["Rank", "Player Name", "Country", "Code", "Ranking Points", "Movement", "Events Played"]],
            use_container_width=True,
            hide_index=True
        )

        # CSV Download Button
        csv_bytes = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Leaderboard as CSV",
            data=csv_bytes,
            file_name=f"tennis_doubles_rankings_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )


# ==============================================================================
# PAGE 7: SQL QUERY CONSOLE
# ==============================================================================
elif selected_page == "SQL Query Console":
    render_header(
        "Interactive SQL Analytics Console",
        "Direct SQL execution against relational tables. Read-only guardrails enforce security."
    )

    # 1. Schema Browser
    with st.expander("📁 View Database Schema & Relational Tables", expanded=False):
        tables = get_table_names()
        if tables:
            st.write(f"**Available Tables ({len(tables)}):** `{', '.join(tables)}`")
            sel_table = st.selectbox("Inspect Table Columns", tables)
            if sel_table:
                schema_df = get_table_schema_df(sel_table)
                st.dataframe(schema_df, use_container_width=True, hide_index=True)
        else:
            st.warning("No tables detected in database.")

    # 2. Predefined Analytical Queries
    predefined_queries = {
        "1. Competitions by Category": """SELECT 
    COALESCE(cat.name, 'Uncategorized') AS category_name,
    COUNT(comp.id) AS total_competitions
FROM Competitions comp
LEFT JOIN Categories cat ON comp.category_id = cat.id
GROUP BY cat.name
ORDER BY total_competitions DESC;""",

        "2. Competition Counts by Gender and Type": """SELECT 
    COALESCE(gender, 'Unspecified') AS competition_gender,
    COALESCE(type, 'Standard') AS competition_type,
    COUNT(id) AS competition_count
FROM Competitions
GROUP BY gender, type
ORDER BY competition_count DESC;""",

        "3. Venue Counts per Complex": """SELECT 
    c.id AS complex_id,
    c.name AS complex_name,
    COUNT(v.id) AS total_venues
FROM Complexes c
LEFT JOIN Venues v ON c.id = v.complex_id
GROUP BY c.id, c.name
ORDER BY total_venues DESC, c.name ASC;""",

        "4. Competitor Counts by Country": """SELECT 
    COALESCE(country, 'Unknown') AS country_name,
    country_code,
    COUNT(id) AS competitor_count
FROM Competitors
GROUP BY country, country_code
ORDER BY competitor_count DESC;""",

        "5. Top-Ranked Competitors by Points": """SELECT 
    r.rank,
    c.name AS competitor_name,
    COALESCE(c.country, 'N/A') AS country,
    r.points,
    r.movement
FROM Competitor_Rankings r
JOIN Competitors c ON r.competitor_id = c.id
ORDER BY r.rank ASC
LIMIT 25;""",

        "6. Total Ranking Points by Country": """SELECT 
    COALESCE(c.country, 'Unknown') AS country_name,
    SUM(r.points) AS total_ranking_points,
    COUNT(c.id) AS ranked_players_count
FROM Competitor_Rankings r
JOIN Competitors c ON r.competitor_id = c.id
GROUP BY c.country
ORDER BY total_ranking_points DESC;""",

        "7. Average Points per Competitor by Country": """SELECT 
    COALESCE(c.country, 'Unknown') AS country_name,
    ROUND(AVG(r.points), 1) AS average_points,
    COUNT(c.id) AS competitor_count
FROM Competitor_Rankings r
JOIN Competitors c ON r.competitor_id = c.id
GROUP BY c.country
HAVING COUNT(c.id) >= 1
ORDER BY average_points DESC;""",

        "8. Ranking Movement Analysis": """SELECT 
    c.name AS competitor_name,
    c.country,
    r.rank AS current_rank,
    r.movement AS rank_movement,
    r.points
FROM Competitor_Rankings r
JOIN Competitors c ON r.competitor_id = c.id
WHERE r.movement != 0
ORDER BY ABS(r.movement) DESC
LIMIT 20;"""
    }

    st.markdown("#### Predefined Analytical Query Templates")
    chosen_template = st.selectbox("Select a query to load into editor:", list(predefined_queries.keys()))

    # Text Area for Query
    query_text = st.text_area(
        "SQL Query Editor (Read-Only SELECT permitted)",
        value=predefined_queries[chosen_template],
        height=180
    )

    r1, r2 = st.columns([1, 4])
    with r1:
        execute_clicked = st.button("▶️ Execute Query", use_container_width=True)

    if execute_clicked:
        if not query_text.strip():
            st.error("Please enter a SQL query.")
        else:
            with st.spinner("Executing query..."):
                ok, df_res, msg = execute_read_only_query(query_text)
                if ok and df_res is not None:
                    st.success(msg)
                    st.dataframe(df_res, use_container_width=True)
                else:
                    st.error(msg)
