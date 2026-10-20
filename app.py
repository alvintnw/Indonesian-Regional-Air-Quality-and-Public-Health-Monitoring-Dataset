import os
import pandas as pd
import plotly.express as px
import streamlit as st

# Konfigurasi Halaman Dashboard (Bersih tanpa logo)
st.set_page_config(
    page_title="Indonesian Air Quality & Health Dashboard", layout="wide"
)

st.title("Indonesian Regional Air Quality & Public Health Monitoring")
st.markdown(
    "Interactive analytics dashboard tracking Air Quality Index (AQI), pollutant"
    " concentrations (PM2.5, PM10, CO, NO2), and public health status across"
    " urban centers in Indonesia."
)


# Fungsi untuk memuat dataset CSV
@st.cache_data
def load_air_data():
  filename = "indonesia_air_quality_health.csv"
  if os.path.exists(filename):
    df = pd.read_csv(filename)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df
  else:
    return pd.DataFrame()


df = load_air_data()

if df.empty:
  st.warning(
      "Dataset file (`indonesia_air_quality_health.csv`) not found. Please"
      " ensure the CSV file is uploaded."
  )
else:
  # Sidebar Filters
  st.sidebar.header("Filter Options")

  cities = sorted(df["city"].unique())
  selected_cities = st.sidebar.multiselect(
      "Select Cities:", options=cities, default=cities
  )

  statuses = sorted(df["air_quality_status"].unique())
  selected_statuses = st.sidebar.multiselect(
      "Select Air Quality Status:", options=statuses, default=statuses
  )

  pollutants = sorted(df["dominant_pollutant"].unique())
  selected_pollutants = st.sidebar.multiselect(
      "Select Dominant Pollutants:", options=pollutants, default=pollutants
  )

  # Filter DataFrame
  filtered_df = df[
      (df["city"].isin(selected_cities))
      & (df["air_quality_status"].isin(selected_statuses))
      & (df["dominant_pollutant"].isin(selected_pollutants))
  ]

  # Executive Metrics Overview
  st.subheader("Executive Summary Metrics")
  col1, col2, col3, col4 = st.columns(4)

  avg_aqi = (
      filtered_df["aqi_score"].mean() if not filtered_df.empty else 0
  )
  max_pm25 = (
      filtered_df["pm25_ug_m3"].max() if not filtered_df.empty else 0
  )
  avg_pm10 = (
      filtered_df["pm10_ug_m3"].mean() if not filtered_df.empty else 0
  )
  total_records = len(filtered_df)

  with col1:
    st.metric(label="Avg. AQI Score", value=f"{avg_aqi:.1f}")
  with col2:
    st.metric(label="Max PM2.5 Level", value=f"{max_pm25} µg/m³")
  with col3:
    st.metric(label="Avg. PM10 Level", value=f"{avg_pm10:.1f} µg/m³")
  with col4:
    st.metric(label="Monitored Entries", value=f"{total_records:,}")

  st.markdown("---")

  # Visualizations Layout
  col_a, col_b = st.columns(2)

  with col_a:
    st.subheader("Average AQI Score by City")
    if not filtered_df.empty:
      city_aqi = (
          filtered_df.groupby("city")["aqi_score"].mean().reset_index()
      )
      fig_city = px.bar(
          city_aqi,
          x="city",
          y="aqi_score",
          color="city",
          title="Mean AQI Score per City",
          labels={"city": "City", "aqi_score": "Average AQI"},
      )
      st.plotly_chart(fig_city, use_container_width=True)

  with col_b:
    st.subheader("Air Quality Status Breakdown")
    if not filtered_df.empty:
      status_counts = (
          filtered_df["air_quality_status"].value_counts().reset_index()
      )
      status_counts.columns = ["Status", "Count"]
      fig_status = px.pie(
          status_counts,
          names="Status",
          values="Count",
          title="Proportion of Air Quality Status",
          hole=0.4,
      )
      st.plotly_chart(fig_status, use_container_width=True)

  # Scatter / Correlation Analysis
  st.subheader("PM2.5 vs PM10 Concentration Correlation")
  if not filtered_df.empty:
    fig_scatter = px.scatter(
        filtered_df,
        x="pm25_ug_m3",
        y="pm10_ug_m3",
        color="air_quality_status",
        symbol="dominant_pollutant",
        title="Relationship Between PM2.5 and PM10 Levels",
        labels={
            "pm25_ug_m3": "PM2.5 (µg/m³)",
            "pm10_ug_m3": "PM10 (µg/m³)",
        },
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

  # Raw Data Expander
  with st.expander("View Raw Air Quality Dataset"):
    st.dataframe(df, use_container_width=True)
