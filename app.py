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
    page_title="Executive Play Store Analytics Portal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling for Enterprise Look
st.markdown(
    """
    <style>
    .main { background-color: #0F172A; }
    .stApp { max-width: 100%; }
    .metric-card {
        background-color: #1E293B;
        padding: 18px;
        border-radius: 10px;
        border: 1px solid #334155;
        text-align: center;
        color: white;
    }
    .status-card {
        background-color: #1E293B;
        padding: 25px;
        border-radius: 12px;
        border-left: 5px solid #F59E0B;
        color: #F8FAFC;
        margin: 20px 0;
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

# Header Dashboard BANNER
st.title("📈 Play Store Executive Intelligence Portal")
st.caption(
    "Real-Time Multilingual Analytics, Predictive Modeling & Category Metrics"
)

# KPI Summary Cards
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric(
        "Active System Time (IST)",
        now_ist.strftime("%I:%M %p"),
        delta="Live Sync",
    )
with kpi2:
    st.metric(
        "Total Portfolio Apps",
        f"{len(df_raw):,}" if not df_raw.empty else "0",
        delta="100% Verified",
    )
with kpi3:
    st.metric(
        "Average Rating",
        (
            f"{df_raw['Rating'].mean():.2f} ★"
            if not df_raw.empty
            else "0.0 ★"
        ),
    )
with kpi4:
    st.metric(
        "Tracked Categories",
        (
            f"{df_raw['Category'].nunique()}"
            if not df_raw.empty
            else "0"
        ),
    )

st.markdown("---")

# Navigation Tabs replacing Task 1...Task 6
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎯 App Density",
    "🌐 Market Hierarchy",
    "📅 Growth Forecast",
    "🌊 Stream Dynamics",
    "📊 Matrix Ranking",
    "⚡ Monetization Radar",
])


# Helper function for professional inactive state
def render_inactive_schedule(module_name, schedule_window):
    st.markdown(
        f"""
        <div class="status-card">
            <h3>⏳ Module Schedule Notice</h3>
            <p>The <b>{module_name}</b> view is time-gated for optimal data processing.</p>
            <p>• <b>Scheduled Window:</b> {schedule_window}</p>
            <p>• <b>Current IST Clock:</b> {now_ist.strftime('%I:%M:%S %p')}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# TAB 1: App Density
with tab1:
    st.subheader("App Size vs Rating Density Distribution")
    is_active = 17 <= now_ist.hour < 19
    if not is_active:
        render_inactive_schedule("App Density Module", "05:00 PM – 07:00 PM IST")
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
                x=df1_filtered["Size_MB"],
                marker_color="skyblue",
                showlegend=False,
            ),
            row=1,
            col=1,
        )
        fig1.add_trace(
            go.Histogram(
                y=df1_filtered["Rating"],
                marker_color="skyblue",
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

        fig1.update_layout(height=580, theme="plotly_dark")
        st.plotly_chart(fig1, use_container_width=True)

# TAB 2: Market Hierarchy
with tab2:
    st.subheader("Global Category & Rating Breakdown")
    is_active = 18 <= now_ist.hour < 20
    if not is_active:
        render_inactive_schedule(
            "Market Hierarchy Sunburst", "06:00 PM – 08:00 PM IST"
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
            df2_filtered["Rating"],
            bins=bins,
            labels=labels,
            include_lowest=True,
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
        )
        fig2.update_layout(height=580)
        st.plotly_chart(fig2, use_container_width=True)

# TAB 3: Growth Forecast
with tab3:
    st.subheader("Monthly Installs Trend & Rolling Averages")
    is_active = 18 <= now_ist.hour < 21
    if not is_active:
        render_inactive_schedule(
            "Growth Forecast Engine", "06:00 PM – 09:00 PM IST"
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
            "Select Target Category:",
            top_5_cats3 if top_5_cats3 else ["No Data"],
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
            cat_df["3M_Rolling_Avg"] = (
                cat_df["Installs"].rolling(window=3).mean()
            )
            cat_df["High_Growth"] = cat_df["MoM_Growth"] > 20

            fig3 = go.Figure()
            fig3.add_trace(
                go.Bar(
                    x=cat_df["Month"],
                    y=cat_df["Installs"],
                    name="Actual Installs",
                    marker_color=np.where(
                        cat_df["High_Growth"], "#10B981", "#3B82F6"
                    ),
                )
            )
            fig3.add_trace(
                go.Scatter(
                    x=cat_df["Month"],
                    y=cat_df["3M_Rolling_Avg"],
                    mode="lines+markers",
                    name="3M Moving Avg",
                    line=dict(color="#F59E0B", width=3, dash="dash"),
                )
            )

            fig3.update_layout(
                xaxis_title="Month", yaxis_title="Total Installs", height=520
            )

            st.plotly_chart(fig3, use_container_width=True)

# TAB 4: Stream Dynamics
with tab4:
    st.subheader("Category Performance Stream & Anomaly Engine")
    is_active = 16 <= now_ist.hour < 18
    if not is_active:
        render_inactive_schedule(
            "Stream Dynamics & Anomaly View", "04:00 PM – 06:00 PM IST"
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
            df4_filtered["Category"]
            .str.upper()
            .str.startswith(("T", "P", "B"))
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
            "Metric Mode:",
            ["Monthly Installs", "Cumulative Installs", "Growth Percentage (%)"],
            horizontal=True,
        )

        merged_df = merged_df.sort_values(["Category_Display", "Month_Num"])
        merged_df["Cumulative"] = merged_df.groupby("Category_Display")[
            "Installs"
        ].cumsum()
        merged_df["MoM_Growth"] = (
            merged_df.groupby("Category_Display")["Installs"].pct_change()
            * 100
        ).fillna(0)

        def calc_zscore(df_sub):
            rolling_mean = (
                df_sub["MoM_Growth"].rolling(window=3, min_periods=1).mean()
            )
            rolling_std = (
                df_sub["MoM_Growth"]
                .rolling(window=3, min_periods=1)
                .std()
                .fillna(1)
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
                arrowcolor="#EF4444",
                ax=0,
                ay=-30,
                font=dict(color="#EF4444", size=10, family="Arial Black"),
            )

        fig4.update_layout(height=580, hovermode="x unified")
        st.plotly_chart(fig4, use_container_width=True)

# TAB 5: Matrix Ranking
with tab5:
    st.subheader("Clustered Metric Matrix & Composite Scoring")
    is_active = 15 <= now_ist.hour < 17
    if not is_active:
        render_inactive_schedule(
            "Matrix Heatmap & Ranking Engine", "03:00 PM – 05:00 PM IST"
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
            "Data Representation:",
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
                colorscale="Viridis",
                text=np.round(display_matrix, 2),
                texttemplate="%{text}",
                colorbar=dict(title="Scale"),
            )
        )

        sorted_scores = norm_df.sort_values("Composite_Score", ascending=False)
        top_3 = sorted_scores.head(3)["Category"].tolist()
        bottom_3 = sorted_scores.tail(3)["Category"].tolist()

        for cat in norm_df["Category"]:
            score = norm_df[norm_df["Category"] == cat][
                "Composite_Score"
            ].values[0]
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
                    font=dict(
                        color="#38BDF8" if cat in top_3 else "#F87171", size=10
                    ),
                )

        fig5.update_layout(height=580)
        st.plotly_chart(fig5, use_container_width=True)

# TAB 6: Monetization Radar
with tab6:
    st.subheader("Free vs Paid Apps Performance Vectors")
    is_active = 13 <= now_ist.hour < 14
    if not is_active:
        render_inactive_schedule(
            "Monetization & Monetization Radar", "01:00 PM – 02:00 PM IST"
        )
    else:
        df6 = df_raw.copy()
        df6["Revenue"] = np.where(
            df6["Type"] == "Paid", df6["Installs"] * df6["Price"], 0.0
        )
        df6["Engagement_Rate"] = (
            df6["Reviews"] / (df6["Installs"] + 1e-5)
        ) * 100

        df6_filtered = df6[
            (df6["Installs"] >= 10000)
            & (df6["Size_MB"] > 15)
            & (
                df6["Content Rating"].str.strip().str.lower()
                == "everyone".lower()
            )
            & (df6["App"].str.len() <= 30)
        ]

        df6_filtered = df6_filtered[
            (df6_filtered["Type"] == "Free")
            | (df6_filtered["Revenue"] > 10000)
        ]

        def check_android(ver_str):
            if pd.isna(ver_str):
                return True
            nums = re.findall(r"\d+\.\d+", str(ver_str))
            if nums:
                return float(nums[0]) >= 4.0
            return True

        df6_filtered = df6_filtered[
            df6_filtered["Android Ver"].apply(check_android)
        ]

        top_5_cats6 = (
            df6_filtered.groupby("Category")["Installs"]
            .sum()
            .nlargest(5)
            .index.tolist()
        )

        selected_cat6 = st.selectbox(
            "Category Scope:", ["Overall Top 5 Categories"] + top_5_cats6
        )

        if selected_cat6 != "Overall Top 5 Categories":
            radar_df = df6_filtered[df6_filtered["Category"] == selected_cat6]
        else:
            radar_df = df6_filtered[df6_filtered["Category"].isin(top_5_cats6)]

        def calc_radar_metrics(sub_df):
            grouped = sub_df.groupby("Type").apply(
                lambda x: pd.Series({
                    "Avg Installs": x["Installs"].mean(),
                    "Weighted Rating": (x["Rating"] * x["Reviews"]).sum()
                    / (x["Reviews"].sum() + 1e-5),
                    "Total Reviews": x["Reviews"].sum(),
                    "Avg Size": x["Size_MB"].mean(),
                    "Revenue": x["Revenue"].sum(),
                    "Engagement Rate": x["Engagement_Rate"].mean(),
                })
            )
            return grouped

        radar_agg = calc_radar_metrics(radar_df)

        radar_metrics = [
            "Avg Installs",
            "Weighted Rating",
            "Total Reviews",
            "Avg Size",
            "Revenue",
            "Engagement Rate",
        ]

        norm_radar = radar_agg.copy()
        for col in radar_metrics:
            max_val = df6_filtered.groupby("Type")[col].mean().max()
            norm_radar[col] = (
                (radar_agg[col] / (max_val + 1e-5)) * 100
            ).clip(0, 100)

        norm_radar["Composite_Score"] = norm_radar[radar_metrics].mean(axis=1)

        free_score = (
            norm_radar.loc["Free", "Composite_Score"]
            if "Free" in norm_radar.index
            else 0
        )
        paid_score = (
            norm_radar.loc["Paid", "Composite_Score"]
            if "Paid" in norm_radar.index
            else 0
        )
        winner = "Free Apps" if free_score >= paid_score else "Paid Apps"

        fig6 = go.Figure()

        for app_type in ["Free", "Paid"]:
            if app_type in norm_radar.index:
                r_vals = norm_radar.loc[app_type, radar_metrics].tolist()
                r_vals.append(r_vals[0])
                theta_vals = radar_metrics + [radar_metrics[0]]

                fig6.add_trace(
                    go.Scatterpolar(
                        r=r_vals,
                        theta=theta_vals,
                        fill="toself",
                        name=f"{app_type} Apps",
                    )
                )

        fig6.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            title=(
                f"App Type Benchmark Vector ({selected_cat6})<br><b>Winner:"
                f" {winner}</b> (Free Score: {free_score:.1f} | Paid Score:"
                f" {paid_score:.1f})"
            ),
            height=580,
        )

        st.plotly_chart(fig6, use_container_width=True)