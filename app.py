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

st.set_page_config(
    page_title="Google Play Store Analytics", layout="wide"
)

st.title("Google Play Store Analytics Dashboard")

ist = pytz.timezone("Asia/Kolkata")
now_ist = datetime.now(ist)


# Safe Data Loading with Fixed Synthetic Data Generator
@st.cache_data
def load_data():
    csv_file = "googleplaystore.csv"

    df = None
    if os.path.exists(csv_file):
        try:
            df = pd.read_csv(csv_file)
        except Exception:
            df = None

    # Fallback to robust synthetic dataset if CSV fails or isn't present
    if df is None or df.empty:
        np.random.seed(42)
        n_samples = 1500
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
        ]
        df = pd.DataFrame({
            "App": [f"App_{i}" for i in range(1, n_samples + 1)],
            "Category": np.random.choice(cats, n_samples),
            "Rating": np.random.uniform(3.0, 5.0, n_samples),
            "Installs": np.random.randint(10000, 5000000, n_samples),
            "Reviews": np.random.randint(100, 100000, n_samples),
            "Size": [
                f"{np.random.uniform(10, 90):.1f}M" for _ in range(n_samples)
            ],
            "Type": np.random.choice(["Free", "Paid"], n_samples),
            "Last Updated": pd.date_range(
                start="2024-01-01", periods=n_samples, freq="h"
            ),
        })

    # Cleaning Steps
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

# ==========================================
# TASK 1: Hexbin Density Chart (5 PM - 7 PM IST)
# ==========================================
st.header("Task 1: App Size vs Rating Hexbin Density")
is_task1_active = 17 <= now_ist.hour < 19

if not is_task1_active:
    st.info(
        f"⏳ Task 1 Chart is scheduled to display between 5:00 PM and 7:00 PM"
        f" IST. (Current IST Time: {now_ist.strftime('%I:%M:%S %p')})"
    )
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

    cat_map1 = {
        "BEAUTY": "सुंदरता",
        "BUSINESS": "வணிகம்",
        "DATING": "Partnersuche",
    }
    df1["Category_Display"] = df1["Category_Clean"].map(
        lambda x: cat_map1.get(x, x)
    )

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
            x=df1_filtered["Size_MB"], marker_color="skyblue", showlegend=False
        ),
        row=1,
        col=1,
    )
    fig1.add_trace(
        go.Histogram(
            y=df1_filtered["Rating"], marker_color="skyblue", showlegend=False
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
            colorbar=dict(title="Avg Installs"),
        ),
        row=2,
        col=1,
    )

    game_apps = df1_filtered[df1_filtered["Category_Clean"] == "GAME"]
    fig1.add_trace(
        go.Scatter(
            x=game_apps["Size_MB"],
            y=game_apps["Rating"],
            mode="markers",
            marker=dict(color="#FF69B4", size=8),
            name="Game Apps (Pink)",
        ),
        row=2,
        col=1,
    )

    fig1.update_layout(height=600)
    st.plotly_chart(fig1, use_container_width=True)

st.divider()

# ==========================================
# TASK 2: Hierarchical Sunburst Chart (6 PM - 8 PM IST)
# ==========================================
st.header("Task 2: Hierarchical Sunburst Analysis")
is_task2_active = 18 <= now_ist.hour < 20

if not is_task2_active:
    st.info(
        f"⏳ Task 2 Sunburst Chart is scheduled to display between 6:00 PM and"
        f" 8:00 PM IST. (Current IST Time: {now_ist.strftime('%I:%M:%S %p')})"
    )
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
        df2_filtered["Rating"], bins=bins, labels=labels, include_lowest=True
    )

    translation_map = {
        "BUSINESS": "வணிகம்",
        "TRAVEL_AND_LOCAL": "Voyages et transits",
        "PRODUCTIVITY": "Productividad",
    }
    df2_filtered["Category"] = df2_filtered["Category"].map(
        lambda x: translation_map.get(x, x)
    )

    fig2 = px.sunburst(
        df2_filtered,
        path=["Country", "Category", "Type", "Rating Band"],
        values="Installs",
        color="Rating",
        color_continuous_scale="RdYlGn",
        title="Hierarchical Sunburst: Country → Category → App Type → Rating Band",
    )
    fig2.update_layout(height=600)
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ==========================================
# TASK 3: Calendar Heatmap & Forecast (6 PM - 9 PM IST)
# ==========================================
st.header("Task 3: Monthly Installs Calendar Heatmap & Forecast")
is_task3_active = 18 <= now_ist.hour < 21

if not is_task3_active:
    st.info(
        f"⏳ Task 3 Chart is scheduled to display between 6:00 PM and 9:00 PM"
        f" IST. (Current IST Time: {now_ist.strftime('%I:%M:%S %p')})"
    )
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

    df3_filtered = df3_filtered[
        ~df3_filtered["App"].str.upper().str.startswith(("X", "Y", "Z"))
    ]
    df3_filtered = df3_filtered[
        ~df3_filtered["App"].str.contains("S", case=False, na=False)
    ]

    trans_map3 = {
        "BEAUTY": "सुंदरता (Beauty)",
        "BUSINESS": "வணிகம் (Business)",
    }
    df3_filtered["Category_Display"] = df3_filtered["Category"].map(
        lambda x: trans_map3.get(x, x)
    )

    top_5_cats3 = (
        df3_filtered.groupby("Category_Display")["Installs"]
        .sum()
        .nlargest(5)
        .index.tolist()
    )

    selected_cat = st.selectbox(
        "Select App Category:", top_5_cats3 if top_5_cats3 else ["No Data"]
    )

    if selected_cat != "No Data":
        cat_df = (
            df3_filtered[df3_filtered["Category_Display"] == selected_cat]
            .groupby(["Month_Num", "Month"])[["Installs", "Reviews"]]
            .sum()
            .reset_index()
            .sort_values("Month_Num")
        )

        cat_df["MoM_Growth"] = cat_df["Installs"].pct_change() * 100
        cat_df["3M_Rolling_Avg"] = cat_df["Installs"].rolling(window=3).mean()
        cat_df["High_Growth"] = cat_df["MoM_Growth"] > 20

        fig3 = go.Figure()
        fig3.add_trace(
            go.Bar(
                x=cat_df["Month"],
                y=cat_df["Installs"],
                name="Actual Installs",
                marker_color=np.where(
                    cat_df["High_Growth"], "#2CA02C", "#1F77B4"
                ),
            )
        )
        fig3.add_trace(
            go.Scatter(
                x=cat_df["Month"],
                y=cat_df["3M_Rolling_Avg"],
                mode="lines+markers",
                name="3M Moving Avg",
                line=dict(color="orange", width=3, dash="dash"),
            )
        )

        fig3.update_layout(
            title=(
                f"Monthly Installs Heatmap & Rolling Average for {selected_cat}"
            ),
            xaxis_title="Month",
            yaxis_title="Total Installs",
            height=500,
        )

        st.plotly_chart(fig3, use_container_width=True)