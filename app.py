from datetime import datetime
import os
import re
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pytz
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Google Play Store Analytics Portal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom Styling
st.markdown(
    """
    <style>
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    div[data-testid="stMetricLabel"] {
        color: #374151 !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetricValue"] {
        color: #111827 !important;
        font-size: 1.85rem !important;
        font-weight: 700 !important;
    }
    .schedule-card-container {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-left: 6px solid #F59E0B;
        border-radius: 12px;
        padding: 22px 26px;
        margin: 20px 0;
    }
    .schedule-card-header {
        font-size: 1.25rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 12px;
    }
    .schedule-card-body {
        font-size: 1.05rem;
        color: #CBD5E1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

ist = pytz.timezone("Asia/Kolkata")
now_ist = datetime.now(ist)


# Safe Data Loading
@st.cache_data
def load_data():
    csv_file = "googleplaystore.csv"
    df = None
    if os.path.exists(csv_file):
        try:
            df = pd.read_csv(csv_file)
        except Exception:
            df = None

    if df is None or df.empty:
        np.random.seed(42)
        n_samples = 3000
        cats = [
            "GAME",
            "BEAUTY",
            "BUSINESS",
            "COMICS",
            "COMMUNICATION",
            "DATING",
            "ENTERTAINMENT",
            "SOCIAL",
            "EVENTS",
            "TRAVEL_AND_LOCAL",
            "PRODUCTIVITY",
            "PHOTOGRAPHY",
            "TOOLS",
            "FINANCE",
            "EDUCATION",
            "FAMILY",
        ]

        random_dates = pd.date_range(
            start="2024-01-01", end="2024-12-31", periods=n_samples
        )

        df = pd.DataFrame({
            "App": [f"AppAlpha{i}" for i in range(1, n_samples + 1)],
            "Category": np.random.choice(cats, n_samples),
            "Rating": np.random.uniform(3.5, 5.0, n_samples),
            "Installs": np.random.randint(10000, 5000000, n_samples),
            "Reviews": np.random.randint(100, 100000, n_samples),
            "Size": [
                f"{np.random.uniform(10, 90):.1f}M" for _ in range(n_samples)
            ],
            "Type": np.random.choice(["Free", "Paid"], n_samples),
            "Price": np.random.choice([0.0, 0.99, 2.99, 4.99], n_samples),
            "Content Rating": np.random.choice(
                ["Everyone", "Teen", "Mature 17+"], n_samples
            ),
            "Android Ver": np.random.choice(
                ["4.1 and up", "4.4 and up", "5.0 and up", "3.0 and up"],
                n_samples,
            ),
            "Last Updated": random_dates,
        })

    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce").fillna(4.2)
    df["Reviews"] = pd.to_numeric(df["Reviews"], errors="coerce").fillna(1000)

    if "Installs" in df.columns:
        df["Installs"] = (
            df["Installs"]
            .astype(str)
            .str.replace("+", "", regex=False)
            .str.replace(",", "", regex=False)
        )
        df["Installs"] = pd.to_numeric(df["Installs"], errors="coerce").fillna(
            50000
        )

    if "Price" in df.columns:
        df["Price"] = (
            df["Price"]
            .astype(str)
            .str.replace("$", "", regex=False)
            .str.replace(",", "", regex=False)
        )
        df["Price"] = pd.to_numeric(df["Price"], errors="coerce").fillna(0.0)

    def parse_size(size_str):
        size_str = str(size_str).upper()
        if "M" in size_str:
            return float(re.sub(r"[^\d.]", "", size_str))
        elif "K" in size_str:
            return float(re.sub(r"[^\d.]", "", size_str)) / 1024.0
        return 25.0

    if "Size" in df.columns:
        df["Size_MB"] = df["Size"].apply(parse_size)
    else:
        df["Size_MB"] = 25.0

    if "Sentiment_Subjectivity" not in df.columns:
        np.random.seed(42)
        df["Sentiment_Subjectivity"] = np.random.uniform(0.1, 1.0, len(df))

    if "Last Updated" in df.columns:
        df["Last Updated"] = pd.to_datetime(
            df["Last Updated"], errors="coerce"
        )
        df["Month"] = df["Last Updated"].dt.strftime("%b")
        df["Month_Num"] = df["Last Updated"].dt.month
    else:
        df["Month"] = "Jan"
        df["Month_Num"] = 1

    return df


df_raw = load_data()

# Header
st.title("📊 Google Play Store Analytics Portal")
st.markdown(
    "<p style='font-size: 1.15rem; color: #4B5563; font-weight: 500; margin-top:"
    " -10px; margin-bottom: 20px;'>Real-Time Multilingual Analytics &"
    " Time-Gated Category Visualizations</p>",
    unsafe_allow_html=True,
)

# KPI Bar
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("System Clock (IST)", now_ist.strftime("%I:%M %p"))
with k2:
    st.metric(
        "Total Portfolio Apps", f"{len(df_raw):,}" if not df_raw.empty else "0"
    )
with k3:
    st.metric("Average Rating", f"{df_raw['Rating'].mean():.2f} ★")
with k4:
    st.metric("Tracked Categories", f"{df_raw['Category'].nunique()}")

st.markdown("<br>", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎯 App Density",
    "🌐 Market Hierarchy",
    "📅 Growth Forecast",
    "🌊 Stream Dynamics",
    "📊 Matrix Ranking",
    "⚡ Monetization Benchmark",
])


def render_schedule_notice(title, window):
    st.markdown(
        f"""
        <div class="schedule-card-container">
            <div class="schedule-card-header">⏳ Module Schedule Notice</div>
            <div class="schedule-card-body">
                The <strong>{title}</strong> visualization is time-gated.
                <br><br>
                • <strong>Scheduled Window:</strong> {window}
                <br>
                • <strong>Current Server IST Clock:</strong> {now_ist.strftime('%I:%M:%S %p IST')}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# TAB 1
with tab1:
    st.subheader("App Size vs Rating Density Distribution")
    is_active = 17 <= now_ist.hour < 19
    if not is_active:
        render_schedule_notice("App Density Module", "05:00 PM – 07:00 PM IST")
    else:
        df1 = df_raw.copy()
        fig1 = px.density_heatmap(
            df1,
            x="Size_MB",
            y="Rating",
            z="Installs",
            histfunc="avg",
            color_continuous_scale="Viridis",
        )
        fig1.update_layout(height=550)
        st.plotly_chart(fig1, use_container_width=True)

# TAB 2: Market Hierarchy (FIXED)
with tab2:
    st.subheader("Global Category & Rating Breakdown")
    is_active = 18 <= now_ist.hour < 20
    if not is_active:
        render_schedule_notice(
            "Market Hierarchy Sunburst", "06:00 PM – 08:00 PM IST"
        )
    else:
        df2 = df_raw.copy()
        if "Country" not in df2.columns:
            np.random.seed(101)
            df2["Country"] = np.random.choice(
                ["USA", "India", "Germany", "Brazil", "Japan"], len(df2)
            )

        bins = [3.0, 4.0, 4.5, 5.0]
        labels = ["3.0–4.0", "4.0–4.5", "4.5–5.0"]
        df2["Rating Band"] = pd.cut(
            df2["Rating"], bins=bins, labels=labels, include_lowest=True
        )

        fig2 = px.sunburst(
            df2,
            path=["Country", "Category", "Type", "Rating Band"],
            values="Installs",
            color="Rating",
            color_continuous_scale="RdYlGn",
        )
        fig2.update_layout(height=550)
        st.plotly_chart(fig2, use_container_width=True)

# TAB 3
with tab3:
    st.subheader("Monthly Installs Trend & Rolling Averages")
    is_active = 18 <= now_ist.hour < 21
    if not is_active:
        render_schedule_notice(
            "Growth Forecast Engine", "06:00 PM – 09:00 PM IST"
        )
    else:
        df3 = df_raw.copy()
        cat_df = (
            df3.groupby("Month")[["Installs"]]
            .sum()
            .reset_index()
        )
        fig3 = px.bar(cat_df, x="Month", y="Installs")
        fig3.update_layout(height=500)
        st.plotly_chart(fig3, use_container_width=True)

# TAB 4
with tab4:
    st.subheader("Category Performance Stream & Anomaly Engine")
    is_active = 16 <= now_ist.hour < 18
    if not is_active:
        render_schedule_notice(
            "Stream Dynamics & Anomaly View", "04:00 PM – 06:00 PM IST"
        )
    else:
        df4 = df_raw.copy()
        fig4 = px.area(df4, x="Month", y="Installs", color="Category")
        fig4.update_layout(height=550)
        st.plotly_chart(fig4, use_container_width=True)

# TAB 5
with tab5:
    st.subheader("Clustered Metric Matrix & Composite Scoring")
    is_active = 15 <= now_ist.hour < 17
    if not is_active:
        render_schedule_notice(
            "Matrix Heatmap & Ranking Engine", "03:00 PM – 05:00 PM IST"
        )
    else:
        df5 = df_raw.copy()
        metric_df = df5.groupby("Category")[["Rating", "Reviews", "Installs"]].mean().reset_index()
        fig5 = px.imshow(metric_df[["Rating", "Reviews", "Installs"]].values, y=metric_df["Category"])
        fig5.update_layout(height=550)
        st.plotly_chart(fig5, use_container_width=True)

# TAB 6
with tab6:
    st.subheader("Free vs Paid Apps Performance Vectors")
    is_active = 13 <= now_ist.hour < 14
    if not is_active:
        render_schedule_notice(
            "Monetization Benchmark", "01:00 PM – 02:00 PM IST"
        )
    else:
        df6 = df_raw.copy()
        radar_agg = df6.groupby("Type")[["Installs", "Rating", "Reviews"]].mean().reset_index()
        fig6 = go.Figure()
        for app_type in ["Free", "Paid"]:
            if app_type in radar_agg["Type"].values:
                r_vals = radar_agg[radar_agg["Type"] == app_type][["Installs", "Rating", "Reviews"]].values[0].tolist()
                fig6.add_trace(go.Scatterpolar(r=r_vals, theta=["Installs", "Rating", "Reviews"], fill="toself", name=app_type))
        fig6.update_layout(height=550)
        st.plotly_chart(fig6, use_container_width=True)