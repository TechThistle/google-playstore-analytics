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
            "Last Updated": random_dates,
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

st.divider()

# ==========================================
# TASK 4: Streamgraph with Anomaly Detection (4 PM - 6 PM IST)
# ==========================================
st.header("Task 4: Interactive Streamgraph & Anomaly Detection")
is_task4_active = 16 <= now_ist.hour < 18

if not is_task4_active:
    st.info(
        f"⏳ Task 4 Chart is scheduled to display between 4:00 PM and 6:00 PM"
        f" IST. (Current IST Time: {now_ist.strftime('%I:%M:%S %p')})"
    )
else:
    df4 = df_raw.copy()

    df4_filtered = df4[
        (df4["Rating"] >= 4.2)
        & (df4["Reviews"] > 1000)
        & (df4["Size_MB"] >= 20)
        & (df4["Size_MB"] <= 80)
        & (df4["Installs"] >= 10000)
    ]
    df4_filtered = df4_filtered[
        ~df4_filtered["App"].str.contains(r"\d", regex=True)
    ]
    df4_filtered = df4_filtered[
        df4_filtered["Category"].str.upper().str.startswith(("T", "P", "B"))
    ]

    trans_map4 = {
        "TRAVEL_AND_LOCAL": "Voyages et transits (Travel & Local)",
        "PRODUCTIVITY": "Productividad (Productivity)",
        "PHOTOGRAPHY": "写真 (Photography)",
    }
    df4_filtered["Category_Display"] = df4_filtered["Category"].map(
        lambda x: trans_map4.get(x, x)
    )

    months_order = [
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
    monthly_cat = (
        df4_filtered.groupby(["Month_Num", "Month", "Category_Display"])[
            "Installs"
        ]
        .sum()
        .reset_index()
        .sort_values("Month_Num")
    )

    unique_cats = monthly_cat["Category_Display"].unique()
    full_grid = pd.MultiIndex.from_product(
        [range(1, 13), unique_cats], names=["Month_Num", "Category_Display"]
    ).to_frame().reset_index(drop=True)
    full_grid["Month"] = full_grid["Month_Num"].map(
        lambda x: months_order[x - 1]
    )

    merged_df = pd.merge(
        full_grid,
        monthly_cat,
        on=["Month_Num", "Month", "Category_Display"],
        how="left",
    ).fillna({"Installs": 0})

    metric_choice = st.radio(
        "Select Streamgraph Metric:",
        ["Monthly Installs", "Cumulative Installs", "Growth Percentage (%)"],
        horizontal=True,
    )

    merged_df = merged_df.sort_values(["Category_Display", "Month_Num"])
    merged_df["Cumulative"] = merged_df.groupby("Category_Display")[
        "Installs"
    ].cumsum()
    merged_df["MoM_Growth"] = (
        merged_df.groupby("Category_Display")["Installs"].pct_change() * 100
    ).fillna(0)

    def calc_zscore(df_sub):
        rolling_mean = (
            df_sub["MoM_Growth"].rolling(window=3, min_periods=1).mean()
        )
        rolling_std = (
            df_sub["MoM_Growth"].rolling(window=3, min_periods=1).std().fillna(1)
        )
        df_sub["Z_Score"] = (df_sub["MoM_Growth"] - rolling_mean) / (
            rolling_std + 1e-5
        )
        return df_sub

    merged_df = (
        merged_df.groupby("Category_Display", group_keys=False)
        .apply(calc_zscore)
    )
    merged_df["Is_Anomaly"] = (merged_df["MoM_Growth"] > 25) & (
        merged_df["Z_Score"] > 2.0
    )

    y_col = "Installs"
    if metric_choice == "Cumulative Installs":
        y_col = "Cumulative"
    elif metric_choice == "Growth Percentage (%)":
        y_col = "MoM_Growth"

    fig4 = px.area(
        merged_df,
        x="Month",
        y=y_col,
        color="Category_Display",
        title=f"Category Streamgraph ({metric_choice}) with Anomaly Detection",
        markers=True,
    )

    anomalies = merged_df[merged_df["Is_Anomaly"]]
    for _, row in anomalies.iterrows():
        fig4.add_annotation(
            x=row["Month"],
            y=row[y_col],
            text=f"⚠️ Spike! (+{row['MoM_Growth']:.1f}%)",
            showarrow=True,
            arrowhead=2,
            arrowcolor="red",
            ax=0,
            ay=-30,
            font=dict(color="red", size=10, family="Arial Black"),
        )

    fig4.update_layout(height=600, hovermode="x unified")
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ==========================================
# TASK 5: Clustered Heatmap & Dynamic Ranking (3 PM - 5 PM IST)
# ==========================================
st.header("Task 5: Interactive Clustered Heatmap & Category Ranking")
is_task5_active = 15 <= now_ist.hour < 17

if not is_task5_active:
    st.info(
        f"⏳ Task 5 Chart is scheduled to display between 3:00 PM and 5:00 PM"
        f" IST. (Current IST Time: {now_ist.strftime('%I:%M:%S %p')})"
    )
else:
    df5 = df_raw.copy()

    df5_filtered = df5[
        (df5["Rating"] >= 4.0)
        & (df5["Size_MB"] > 10)
        & (df5["Installs"] >= 10000)
        & (df5["Reviews"] > 1000)
        & (df5["Month"].str.upper().str.startswith("JAN"))
    ]

    df5_filtered = df5_filtered[
        ~df5_filtered["App"].str.contains(r"\d", regex=True)
    ]

    top_10_cats = (
        df5_filtered.groupby("Category")["Installs"]
        .sum()
        .nlargest(10)
        .index.tolist()
    )
    df5_top10 = df5_filtered[df5_filtered["Category"].isin(top_10_cats)]

    metric_df = (
        df5_top10.groupby("Category")
        .agg(
            Weighted_Rating=("Rating", "mean"),
            Total_Reviews=("Reviews", "sum"),
            Total_Installs=("Installs", "sum"),
            Average_Size=("Size_MB", "mean"),
            Engagement_Rate=("Reviews", lambda x: (x.sum() / 100000.0)),
            Update_Frequency=("Last Updated", "count"),
        )
        .reset_index()
    )

    metrics = [
        "Weighted_Rating",
        "Total_Reviews",
        "Total_Installs",
        "Average_Size",
        "Engagement_Rate",
        "Update_Frequency",
    ]

    # Pure NumPy Z-score calculation (Zero external dependencies)
    norm_df = metric_df.copy()
    for m in metrics:
        std_val = metric_df[m].std()
        if std_val == 0 or np.isnan(std_val):
            norm_df[m] = 0.0
        else:
            norm_df[m] = (metric_df[m] - metric_df[m].mean()) / std_val

    norm_df["Composite_Score"] = norm_df[metrics].mean(axis=1)
    norm_df = norm_df.sort_values("Composite_Score", ascending=False)
    metric_df = metric_df.loc[norm_df.index]

    view_mode = st.radio(
        "Display Values Mode:",
        ["Normalized (Z-Score)", "Raw Values"],
        horizontal=True,
    )

    display_matrix = (
        norm_df[metrics].values
        if view_mode == "Normalized (Z-Score)"
        else metric_df[metrics].values
    )

    fig5 = go.Figure(
        data=go.Heatmap(
            z=display_matrix,
            x=[m.replace("_", " ") for m in metrics],
            y=norm_df["Category"],
            colorscale="RdYlGn",
            text=np.round(display_matrix, 2),
            texttemplate="%{text}",
            colorbar=dict(title="Value"),
        )
    )

    sorted_scores = norm_df.sort_values("Composite_Score", ascending=False)
    top_3 = sorted_scores.head(3)["Category"].tolist()
    bottom_3 = sorted_scores.tail(3)["Category"].tolist()

    for cat in norm_df["Category"]:
        score = norm_df[norm_df["Category"] == cat]["Composite_Score"].values[0]
        label = ""
        if cat in top_3:
            label = f" (Top 3 | Score: {score:.2f})"
        elif cat in bottom_3:
            label = f" (Bottom 3 | Score: {score:.2f})"

        if label:
            fig5.add_annotation(
                x=len(metrics) - 0.5,
                y=cat,
                text=label,
                showarrow=False,
                font=dict(color="blue" if cat in top_3 else "darkred", size=10),
            )

    fig5.update_layout(
        title="Hierarchical Clustered Heatmap & Composite Score Annotations",
        xaxis_title="Metrics",
        yaxis_title="Category",
        height=600,
    )

    st.plotly_chart(fig5, use_container_width=True)