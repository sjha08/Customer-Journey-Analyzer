import pandas as pd

DATA_PATH = "sample_data/events.csv"
FUNNEL = ["acquired", "activated", "converted"]  # extend with "retained" if you add events

def load_events(path: str = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["event_date"])
    return df

def funnel_summary(df: pd.DataFrame) -> pd.DataFrame:
    stage_users = {}
    for stage in FUNNEL:
        users = df.loc[df["stage"] == stage, "user_id"].unique()
        stage_users[stage] = set(users)

    rows = []
    base = len(stage_users[FUNNEL[0]]) if FUNNEL[0] in stage_users else 0
    prev_users = stage_users[FUNNEL[0]] if FUNNEL[0] in stage_users else set()
    for i, stage in enumerate(FUNNEL):
        users = stage_users.get(stage, set())
        count = len(users)
        if i == 0:
            conv_from_prev = 1.0
        else:
            conv_from_prev = (count / max(1, len(prev_users)))
        conv_from_base = (count / max(1, base))
        rows.append({
            "stage": stage,
            "users": count,
            "conv_from_prev_%": round(conv_from_prev * 100, 1),
            "conv_from_base_%": round(conv_from_base * 100, 1)
        })
        prev_users = users
    return pd.DataFrame(rows)

def top_channel_for_stage(df: pd.DataFrame, stage: str) -> pd.DataFrame:
    stage_df = df[df["stage"] == stage]
    return (stage_df.groupby("channel")["user_id"]
            .nunique()
            .sort_values(ascending=False)
            .rename("unique_users")
            .reset_index())

def print_report(df: pd.DataFrame):
    print("Customer Journey — Funnel Summary\n")
    fs = funnel_summary(df)
    print(fs.to_string(index=False))

    print("\n🏷️ Top Channels by Stage")
    for s in FUNNEL:
        top = top_channel_for_stage(df, s)
        if top.empty:
            continue
        winner = top.iloc[0]
        print(f"- {s.title()}: {winner['channel']} ({int(winner['unique_users'])} users)")

    # Simple insight example
    acquired = df[df["stage"] == "acquired"]["user_id"].nunique()
    converted = df[df["stage"] == "converted"]["user_id"].nunique()
    conv_rate = round((converted / acquired) * 100, 1) if acquired else 0.0
    print(f"\n Overall conversion rate: {conv_rate}%")

if __name__ == "__main__":
    events = load_events()
    print_report(events)
6) app.py (Streamlit dashboard with charts)
python
Copy code
"""
Customer Journey Analyzer — Streamlit App
Run: streamlit run app.py
"""

import pandas as pd
import plotly.express as px
import streamlit as st

DATA_PATH = "sample_data/events.csv"
FUNNEL = ["acquired", "activated", "converted"]

st.set_page_config(page_title="Customer Journey Analyzer", layout="wide")
st.title("Customer Journey Analyzer")
st.caption("Analyze funnel drop-offs, retention by cohort (basic), and channel impact.")

@st.cache_data
def load_events(path: str = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["event_date"])
    df["month"] = df["event_date"].dt.to_period("M").astype(str)
    return df

def funnel_table(df: pd.DataFrame) -> pd.DataFrame:
    stage_users = {}
    for stage in FUNNEL:
        users = df.loc[df["stage"] == stage, "user_id"].unique()
        stage_users[stage] = set(users)

    rows = []
    base = len(stage_users[FUNNEL[0]]) if FUNNEL[0] in stage_users else 0
    prev_users = stage_users[FUNNEL[0]] if FUNNEL[0] in stage_users else set()
    for i, stage in enumerate(FUNNEL):
        users = stage_users.get(stage, set())
        count = len(users)
        conv_from_prev = 1.0 if i == 0 else (count / max(1, len(prev_users)))
        conv_from_base = (count / max(1, base))
        rows.append({
            "stage": stage,
            "users": count,
            "conv_from_prev_%": round(conv_from_prev * 100, 1),
            "conv_from_base_%": round(conv_from_base * 100, 1)
        })
        prev_users = users
    return pd.DataFrame(rows)

def channel_breakdown(df: pd.DataFrame, stage: str) -> pd.DataFrame:
    stage_df = df[df["stage"] == stage]
    return (stage_df.groupby(["channel"])["user_id"]
            .nunique()
            .rename("unique_users")
            .reset_index()
            .sort_values("unique_users", ascending=False))

df = load_events()

# KPIs
col1, col2, col3 = st.columns(3)
acq = df[df["stage"] == "acquired"]["user_id"].nunique()
act = df[df["stage"] == "activated"]["user_id"].nunique()
conv = df[df["stage"] == "converted"]["user_id"].nunique()
conv_rate = round((conv / acq) * 100, 1) if acq else 0.0
col1.metric("Acquired", acq)
col2.metric("Activated", act)
col3.metric("Converted", conv, f"{conv_rate}% of acquired")

# Funnel table
st.subheader("Funnel Summary")
ft = funnel_table(df)
st.dataframe(ft, use_container_width=True)

# Channel charts
st.subheader("Channel Contribution by Stage")
stage = st.selectbox("Choose stage", FUNNEL, index=0)
cb = channel_breakdown(df, stage)
fig = px.bar(cb, x="channel", y="unique_users", title=f"Unique Users Reaching '{stage}' by Channel")
st.plotly_chart(fig, use_container_width=True)

# Simple cohort view (by acquisition month → retention to converted)
st.subheader("Simple Cohort View (Acquisition Month → Converted)")
acq_users = (df[df["stage"] == "acquired"][["user_id", "month"]]
             .rename(columns={"month": "acq_month"}))
converted_users = df[df["stage"] == "converted"][["user_id", "month"]].rename(columns={"month": "conv_month"})
cohort = acq_users.merge(converted_users, on="user_id", how="left")
cohort["converted_flag"] = cohort["conv_month"].notna().astype(int)
cohort_view = cohort.groupby("acq_month")["converted_flag"].mean().reset_index()
cohort_view["converted_flag"] = (cohort_view["converted_flag"] * 100).round(1)

fig2 = px.line(cohort_view, x="acq_month", y="converted_flag",
               markers=True, title="Conversion % by Acquisition Month")
fig2.update_yaxes(title="Conversion %")
fig2.update_xaxes(title="Acquisition Month")
st.plotly_chart(fig2, use_container_width=True)

st.info("Tip: Extend events.csv with more rows and stages (e.g., retained) to deepen the analysis.")
