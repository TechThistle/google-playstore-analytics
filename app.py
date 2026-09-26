from datetime import datetime
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
    np.random.seed(42)
    categories1 = [
        "BEAUTY",
        "BUSINESS",
        "DATING",
        "GAME",
        "COMICS",
        "COMMUNICATION",
        "ENTERTAINMENT",
        "SOCIAL",
        "EVENTS",
    ]
    df1 = pd.DataFrame({
        "App": [f"App {i}" for i in range(1, 501)],
        "Category": np.random.choice(categories1, 500),
        "Rating": np.random.uniform(3.0, 5.0, 500),
        "Installs": np.random.randint(10000, 1000000, 500),
        "Reviews": np.random.randint(100, 50000, 500),
        "Size_MB": np.random.uniform(5, 120, 500),
        "Sentiment_Subjectivity": np.random.uniform(0.1, 1.0, 500),
    })

    cat_map1 = {
        "BEAUTY": "सुंदरता",
        "BUSINESS": "வணிகம்",
        "DATING": "Partnersuche",
        "GAME": "Game",
        "COMICS": "Comics",
        "COMMUNICATION": "Communication",
        "ENTERTAINMENT": "Entertainment",
        "SOCIAL": "Social",
        "EVENTS": "Events",
    }
    df1["Category_Display"] = df1["Category"].map(cat_map1)

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

    game_apps = df1_filtered[df1_filtered["Category"] == "GAME"]
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
    np.random.seed(101)
    countries = ["USA", "India", "Germany", "Brazil", "Japan"]
    categories2 = [
        "BUSINESS",
        "TRAVEL_AND_LOCAL",
        "PRODUCTIVITY",
        "FAMILY",
        "TOOLS",
        "HEALTH_AND_FITNESS",
        "FINANCE",
        "EDUCATION",
        "PHOTOGRAPHY",
    ]
    app_types = ["Free", "Paid"]

    data2 = {
        "App": [f"AppAlpha {i}" for i in range(1, 1001)],
        "Country": np.random.choice(countries, 1000),
        "Category": np.random.choice(categories2, 1000),
        "Type": np.random.choice(app_types, 1000),
        "Rating": np.random.uniform(3.5, 5.0, 1000),
        "Installs": np.random.randint(5000, 5000000, 1000),
        "Reviews": np.random.randint(500, 100000, 1000),
        "Size_MB": np.random.uniform(10, 100, 1000),
    }
    df2 = pd.DataFrame(data2)

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
        ~df2_filtered["Category"].str.upper().str.startswith(("A", "C", "G", "S"))
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
    # Generate Synthetic Monthly Data
    np.random.seed(2024)
    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    categories3 = [
        "EVENTS",
        "ENTERTAINMENT",
        "COMICS",
        "COMMUNICATION",
        "BUSINESS",
        "BEAUTY",
    ]

    records = []
    for cat in categories3:
        for m_idx, m in enumerate(months):
            records.append({
                "App": f"App_{cat}_{m_idx}",
                "Category": cat,
                "Month": m,
                "Month_Num": m_idx + 1,
                "Rating": np.random.uniform(4.0, 5.0),
                "Installs": np.random.randint(15000, 200000),
                "Reviews": np.random.randint(501, 20000),
                "Size_MB": np.random.uniform(15, 80),
                "Sentiment_Subjectivity": np.random.uniform(0.51, 1.0),
            })

    df3 = pd.DataFrame(records)

    # Filtering Criteria
    # 1. Categories starting with E, C, or B
    df3 = df3[
        df3["Category"].str.upper().str.startswith(("E", "C", "B"))
    ]

    # 2. Threshold Filters
    df3_filtered = df3[
        (df3["Rating"] >= 4.0)
        & (df3["Installs"] > 10000)
        & (df3["Reviews"] > 500)
        & (df3["Size_MB"] >= 15)
        & (df3["Size_MB"] <= 80)
        & (df3["Sentiment_Subjectivity"] > 0.5)
    ]

    # 3. Name Exclusions (No starting X,Y,Z and no 'S' anywhere)
    df3_filtered = df3_filtered[
        ~df3_filtered["App"].str.upper().str.startswith(("X", "Y", "Z"))
    ]
    df3_filtered = df3_filtered[
        ~df3_filtered["App"].str.contains("S", case=False, na=False)
    ]

    # Translation Map
    trans_map3 = {
        "BEAUTY": "सुंदरता (Beauty)",
        "BUSINESS": "வணிகம் (Business)",
    }
    df3_filtered["Category_Display"] = df3_filtered["Category"].map(
        lambda x: trans_map3.get(x, x)
    )

    # Dynamic Category Selector
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

        # Calculations
        cat_df["MoM_Growth"] = cat_df["Installs"].pct_change() * 100
        cat_df["3M_Rolling_Avg"] = cat_df["Installs"].rolling(window=3).mean()
        cat_df["High_Growth"] = cat_df["MoM_Growth"] > 20

        # Forecast (Next 3 Months)
        last_3m_avg = cat_df["Installs"].tail(3).mean()
        forecast_months = ["Jan (+1)", "Feb (+1)", "Mar (+1)"]
        forecast_df = pd.DataFrame({
            "Month": forecast_months,
            "Installs": [last_3m_avg] * 3,
            "Status": ["Forecast"] * 3,
            "Reviews": [0] * 3,
            "MoM_Growth": [0] * 3,
            "3M_Rolling_Avg": [last_3m_avg] * 3,
        })
        cat_df["Status"] = "Actual"

        combined_df = pd.concat([cat_df, forecast_df], ignore_index=True)

        # Create Heatmap/Bar Visualization
        fig3 = go.Figure()

        # Actual Installs
        fig3.add_trace(
            go.Bar(
                x=cat_df["Month"],
                y=cat_df["Installs"],
                name="Actual Installs",
                marker_color=np.where(
                    cat_df["High_Growth"], "#2CA02C", "#1F77B4"
                ),
                hovertemplate=(
                    "<b>Month: %{x}</b><br>Installs: %{y:,.0f}<br>MoM Growth:"
                    " %{customdata[0]:.2f}%<br>3M Rolling Avg:"
                    " %{customdata[1]:,.0f}<br>Reviews:"
                    " %{customdata[2]:,.0f}<extra></extra>"
                ),
                customdata=cat_df[
                    ["MoM_Growth", "3M_Rolling_Avg", "Reviews"]
                ].fillna(0),
            )
        )

        # Forecast Line
        fig3.add_trace(
            go.Scatter(
                x=combined_df["Month"],
                y=combined_df["3M_Rolling_Avg"],
                mode="lines+markers",
                name="3M Moving Avg / Forecast",
                line=dict(color="orange", width=3, dash="dash"),
            )
        )

        fig3.update_layout(
            title=(
                f"Monthly Installs Heatmap & 3-Month Forecast for"
                f" {selected_cat}"
            ),
            xaxis_title="Month",
            yaxis_title="Total Installs",
            height=500,
        )

        st.plotly_chart(fig3, use_container_width=True)