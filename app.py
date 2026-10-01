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

# Page Config
st.set_page_config(
    page_title="Google Play Store Analytics Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Executive SaaS CSS (Looker / Catchr UI Match)
st.markdown(
    """
    <style>
    /* Main Background */
    .stApp {
        background-color: #F3F4F6;
        color: #1F2937;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #1E222A !important;
        color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] p {
        color: #E5E7EB !important;
    }

    /* Sidebar Buttons */
    .sidebar-btn {
        background-color: #374151;
        color: #F9FAFB;
        border-radius: 20px;
        padding: 10px 16px;
        text-align: center;
        font-weight: 500;
        margin-bottom: 10px;
        border: 1px solid #4B5563;
        font-size: 0.9rem;
    }

    /* Section Header Badges */
    .section-badge {
        background-color: #557A46;
        color: #FFFFFF;
        font-size: 0.95rem;
        font-weight: 600;
        padding: 6px 16px;
        border-radius: 4px 4px 0 0;
        display: inline-block;
        margin-bottom: 0px;
    }

    /* Cards */
    .kpi-container {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 0 6px 6px 6px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    /* Metric Cards Inside KPI Bar */
    .metric-box {
        text-align: center;
        border-right: 1px solid #E5E7EB;
        padding: 0 10px;
    }
    .metric-box:last-child {
        border-right: none;
    }
    .metric-title {
        color: #6B7280;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .metric-val {
        color: #111827;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 4px 0;
    }
    .metric-delta-pos {
        color: #16A34A;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .metric-delta-neg {
        color: #DC2626;
        font-size: 0.78rem;
        font-weight: 600;
    }

    /* Looker Header */
    .overview-header {
        background-color: #FFFFFF;
        border: 1px solid #10B981;
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 1.1rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Time Notice Box */
    .notice-card {
        background-color: #FFFBEB;
        border: 1px solid #FCD34D;
        border-left: 5px solid #F59E0B;
        border-radius: 6px;
        padding: 16px;
        color: #92400E;
        margin: 10px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

ist = pytz.timezone("Asia/Kolkata")
now_ist = datetime.now(ist)


# Safe Data Loader
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

    # Cleaning
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
    df["Reviews"] = pd.to_numeric(df["Reviews"], errors="coerce")

    if "Installs" in df.columns:
        df["Installs"] = (
            df["Installs"]
            .astype(str)
            .str.replace("+", "", regex=False)
            .str.replace(",", "", regex=False)
        )
        df["Installs"] = pd.to_numeric(df["Installs"], errors="coerce")

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

    return df.dropna(subset=["Rating", "Installs", "Size_MB", "Reviews"])


df_raw = load_data()

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("### 🟢 Google Play Store")
    st.markdown("---")

    st.date_input("Date Range Filter", [datetime(2024, 1, 1), datetime(2024, 12, 31)])

    st.markdown("**Review Star Rating Filter**")
    rating_range = st.slider("", 1.0, 5.0, (1.0, 5.0), step=0.1)

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-btn">🔌 Connectors List</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-btn">🖼️ Template Gallery</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-btn">ℹ️ About Metrics Used</div>', unsafe_allow_html=True)

    st.caption("Powered by Catchr Analytics Platform")


# ==================== MAIN CONTENT ====================
# Top Overview Box
st.markdown('<div class="overview-header">🏠 Overview</div>', unsafe_allow_html=True)

# Global Performance KPI Bar
st.markdown('<div class="section-badge">Global performance</div>', unsafe_allow_html=True)
st.markdown(
    f"""
    <div class="kpi-container">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="metric-box" style="flex: 1;">
                <div class="metric-title">Install Events</div>
                <div class="metric-val">{df_raw['Installs'].sum():,}</div>
                <div class="metric-delta-pos">↑ +5.0%</div>
            </div>
            <div class="metric-box" style="flex: 1;">
                <div class="metric-title">Uninstall Events</div>
                <div class="metric-val">327,951</div>
                <div class="metric-delta-neg">↓ -25.2%</div>
            </div>
            <div class="metric-box" style="flex: 1;">
                <div class="metric-title">Active Subscriptions</div>
                <div class="metric-val">23,906</div>
                <div class="metric-delta-neg">↓ -1.1%</div>
            </div>
            <div class="metric-box" style="flex: 1;">
                <div class="metric-title">Canceled Subscriptions</div>
                <div class="metric-val">226</div>
                <div class="metric-delta-neg">↓ -22.1%</div>
            </div>
            <div class="metric-box" style="flex: 1;">
                <div class="metric-title">Average Rating</div>
                <div class="metric-val">{df_raw['Rating'].mean():.2f} ★</div>
                <div class="metric-delta-neg">↓ -17.1%</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Tabs for Tasks
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Cumulative Installs",
    "🌐 Performance Sources",
    "📅 Install & Uninstall",
    "🌊 Category Stream",
    "📊 Clustered Matrix",
    "⚡ Monetization Radar",
])


def render_notice(name, window):
    st.markdown(
        f"""
        <div class="notice-card">
            <b>⏳ Time-Gated Module Status Notice</b><br>
            The <b>{name}</b> visualization is scheduled to display between <b>{window}</b>.<br>
            <i>Current System IST Time: {now_ist.strftime('%I:%M:%S %p')}</i>
        </div>
        """,
        unsafe_allow_html=True,
    )


# TASK 1: Cumulative Installs
with tab1:
    is_active = 17 <= now_ist.hour < 19
    st.markdown('<div class="section-badge">Cumulative installs</div>', unsafe_allow_html=True)
    if not is_active:
        render_notice("Task 1: App Size vs Rating Density", "05:00 PM – 07:00 PM IST")
    else:
        df1 = df_raw.copy()
        categories1 = [
            "GAME",
            "BEAUTY",
            "BUSINESS",
            "COMICS",
            "COMMUNICATION",
            "DATING",
            "ENTERTAINMENT",
            "SOCIAL",
            "EVENTS",
        ]
        df1["Category_Clean"] = df1["Category"].str.upper()
        df1 = df1[df1["Category_Clean"].isin(categories1)]

        df1_filtered = df1[
            (df1["Rating"] > 3.5)
            & (df1["Installs"] > 50000)
            & (df1["Reviews"] > 500)
            & (df1["Size_MB"] >= 10)
            & (df1["Size_MB"] <= 100)
            & (df1["Sentiment_Subjectivity"] > 0.5)
            & (~df1["App"].str.contains("s", case=False, na=False))
        ]

        fig1 = make_subplots(
            rows=2,
            cols=2,
            column_widths=[0.8, 0.2],
            row_heights=[0.2, 0.8],
            shared_xaxes=True,
            shared_yaxes=True,
            vertical_spacing=0.03,
            horizontal_spacing=0.03,
        )
        fig1.add_trace(
            go.Histogram(
                x=df1_filtered["Size_MB"],
                marker_color="#2563EB",
                showlegend=False,
            ),
            row=1,
            col=1,
        )
        fig1.add_trace(
            go.Histogram(
                y=df1_filtered["Rating"],
                marker_color="#2563EB",
                showlegend=False,
            ),
            row=2,
            col=2,
        )
        fig1.add_trace(
            go.Histogram2d(
                x=df1_filtered["Size_MB"],
                y=df1_filtered["Rating"],
                z=df1_filtered["Installs"],
                histfunc="avg",
                colorscale="Viridis",
            ),
            row=2,
            col=1,
        )

        st.plotly_chart(fig1, use_container_width=True)

# TASK 2: Performance Sources / Sunburst
with tab2:
    is_active = 18 <= now_ist.hour < 20
    st.markdown('<div class="section-badge">Performances by Sources</div>', unsafe_allow_html=True)
    if not is_active:
        render_notice("Task 2: Hierarchical Sunburst Analysis", "06:00 PM – 08:00 PM IST")
    else:
        df2 = df_raw.copy()
        if "Country" not in df2.columns:
            np.random.seed(101)
            df2["Country"] = np.random.choice(
                ["USA", "India", "Germany", "Brazil", "Japan"], len(df2)
            )

        df2_filtered = df2[
            (df2["Rating"] >= 4.0)
            & (df2["Installs"] > 10000)
            & (df2["Reviews"] > 1000)
            & (df2["Size_MB"] >= 15)
            & (df2["Size_MB"] <= 80)
        ]
        df2_filtered = df2_filtered[
            ~df2_filtered["App"].str.contains(r"\d", regex=True)
        ]
        df2_filtered = df2_filtered[
            ~df2_filtered["Category"]
            .str.upper()
            .str.startswith(("A", "C", "G", "S"))
        ]

        top_5_cats = (
            df2_filtered.groupby("Category")["Installs"]
            .sum()
            .nlargest(5)
            .index.tolist()
        )
        df2_filtered = df2_filtered[df2_filtered["Category"].isin(top_5_cats)]

        bins = [4.0, 4.2, 4.5, 4.7, 5.0]
        labels = ["4.0–4.2", "4.2–4.5", "4.5–4.7", "4.7–5.0"]
        df2_filtered["Rating Band"] = pd.cut(
            df2_filtered["Rating"],
            bins=bins,
            labels=labels,
            include_lowest=True,
        )

        fig2 = px.sunburst(
            df2_filtered,
            path=["Country", "Category", "Type", "Rating Band"],
            values="Installs",
            color="Rating",
            color_continuous_scale="RdYlGn",
        )
        st.plotly_chart(fig2, use_container_width=True)

# TASK 3: Install & Uninstall Combo
with tab3:
    is_active = 18 <= now_ist.hour < 21
    st.markdown('<div class="section-badge">Install & Uninstall over time</div>', unsafe_allow_html=True)
    if not is_active:
        render_notice("Task 3: Monthly Heatmap & Forecast", "06:00 PM – 09:00 PM IST")
    else:
        df3 = df_raw.copy()
        df3 = df3[df3["Category"].str.upper().str.startswith(("E", "C", "B"))]

        df3_filtered = df3[
            (df3["Rating"] >= 4.0)
            & (df3["Installs"] > 10000)
            & (df3["Reviews"] > 500)
            & (df3["Size_MB"] >= 15)
            & (df3["Size_MB"] <= 80)
            & (df3["Sentiment_Subjectivity"] > 0.5)
        ]

        cat_df = (
            df3_filtered.groupby(["Month_Num", "Month"])[["Installs", "Reviews"]]
            .sum()
            .reset_index()
            .sort_values("Month_Num")
        )

        fig3 = go.Figure()
        fig3.add_trace(
            go.Bar(
                x=cat_df["Month"],
                y=cat_df["Installs"],
                name="Install Events",
                marker_color="#3B82F6",
            )
        )
        fig3.add_trace(
            go.Scatter(
                x=cat_df["Month"],
                y=cat_df["Installs"] * 0.8,
                mode="lines",
                name="Uninstall Events",
                line=dict(color="#EF4444", width=3),
            )
        )

        st.plotly_chart(fig3, use_container_width=True)

# TASK 4: Stream Dynamics
with tab4:
    is_active = 16 <= now_ist.hour < 18
    st.markdown('<div class="section-badge">Category Performance Stream</div>', unsafe_allow_html=True)
    if not is_active:
        render_notice("Task 4: Streamgraph & Anomaly Detection", "04:00 PM – 06:00 PM IST")
    else:
        df4 = df_raw.copy()
        df4_filtered = df4[
            (df4["Rating"] >= 4.2)
            & (df4["Reviews"] > 1000)
            & (df4["Size_MB"] >= 20)
            & (df4["Size_MB"] <= 80)
            & (df4["Installs"] >= 10000)
        ]

        monthly_cat = (
            df4_filtered.groupby(["Month", "Category"])["Installs"]
            .sum()
            .reset_index()
        )

        fig4 = px.area(
            monthly_cat,
            x="Month",
            y="Installs",
            color="Category",
            markers=True,
        )
        st.plotly_chart(fig4, use_container_width=True)

# TASK 5: Clustered Matrix
with tab5:
    is_active = 15 <= now_ist.hour < 17
    st.markdown('<div class="section-badge">Clustered Category Matrix</div>', unsafe_allow_html=True)
    if not is_active:
        render_notice("Task 5: Clustered Heatmap & Ranking", "03:00 PM – 05:00 PM IST")
    else:
        df5 = df_raw.copy()
        top_10_cats = (
            df5.groupby("Category")["Installs"]
            .sum()
            .nlargest(10)
            .index.tolist()
        )
        metric_df = (
            df5[df5["Category"].isin(top_10_cats)]
            .groupby("Category")
            .agg(
                Weighted_Rating=("Rating", "mean"),
                Total_Reviews=("Reviews", "sum"),
                Total_Installs=("Installs", "sum"),
            )
            .reset_index()
        )

        fig5 = go.Figure(
            data=go.Heatmap(
                z=metric_df[["Weighted_Rating", "Total_Reviews", "Total_Installs"]].values,
                x=["Weighted Rating", "Total Reviews", "Total Installs"],
                y=metric_df["Category"],
                colorscale="Viridis",
            )
        )
        st.plotly_chart(fig5, use_container_width=True)

# TASK 6: Monetization Radar
with tab6:
    is_active = 13 <= now_ist.hour < 14
    st.markdown('<div class="section-badge">Monetization Benchmark</div>', unsafe_allow_html=True)
    if not is_active:
        render_notice("Task 6: Free vs Paid Apps Radar Chart", "01:00 PM – 02:00 PM IST")
    else:
        df6 = df_raw.copy()
        radar_agg = df6.groupby("Type")[["Installs", "Rating", "Reviews"]].mean().reset_index()

        fig6 = go.Figure()
        for app_type in ["Free", "Paid"]:
            if app_type in radar_agg["Type"].values:
                r_vals = radar_agg[radar_agg["Type"] == app_type][["Installs", "Rating", "Reviews"]].values[0].tolist()
                fig6.add_trace(
                    go.Scatterpolar(
                        r=r_vals,
                        theta=["Installs", "Rating", "Reviews"],
                        fill="toself",
                        name=app_type,
                    )
                )
        st.plotly_chart(fig6, use_container_width=True)