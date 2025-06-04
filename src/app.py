import json
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import openai
import streamlit as st
import os
from streamlit_option_menu import option_menu
from aggregator import Aggregator
from trade_tracer import TradeTracer
import re


# Azure OpenAI Setup
AZURE_OPENAI_ENDPOINT = "https://bh-us-openai-mindhackzombies.openai.azure.com/"
AZURE_OPENAI_API_KEY = "fa798078d083440bbc77c87a9fa29025"
AZURE_DEPLOYMENT_NAME = "gpt-4.1"
AZURE_MODEL_NAME = "gpt-4.1"

openai.api_type = "azure"
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_key = AZURE_OPENAI_API_KEY
openai.api_version = "2023-07-01-preview"  # Use the version that supports GPT-4o


# Streamlit Setup
st.set_page_config(page_title="Trade Aggregator + Forecast", layout="wide")

# Sidebar with custom menu and title
with st.sidebar:
    st.markdown("<h2 style='color:black; text-align:center;'>Next Gen 6G</h2>", unsafe_allow_html=True)
    page = option_menu(
        menu_title="📂 Menu",
        options=["📊 Trace", "💬 Chatbot Q&A", "📈 Prediction"],
        icons=["bar-chart", "chat-dots", "graph-up"],
        menu_icon="list",
        default_index=0,
        styles={
            "container": {"background-color": "#0e1117", "padding": "5px"},
            "icon": {"color": "#c7d5e0", "font-size": "18px"},
            "nav-link": {
                "color": "#c7d5e0",
                "font-size": "16px",
                "text-align": "left",
                "margin": "5px 0",
                "--hover-color": "#2e3a49"
            },
            "nav-link-selected": {
                "background-color": "#1f3b4d",
                "color": "#ffffff",
                "font-weight": "bold"
            },
        }
    )

# Session state initialization
for key in ["agg_df", "complete_df", "trace_df", "aggregation_done", "uploaded"]:
    if key not in st.session_state:
        st.session_state[key] = None if "_df" in key else False

# Aggregator & Trace Page
if page == "📊 Trace":
    st.title("📊 Trade  Trace Tool")
    uploaded_files = st.file_uploader("Upload Files", type="csv", accept_multiple_files=True)

    if uploaded_files:
        input_dir = "./generated_trade_files"
        os.makedirs(input_dir, exist_ok=True)
        for f in os.listdir(input_dir):
            os.remove(os.path.join(input_dir, f))
        for file in uploaded_files:
            with open(os.path.join(input_dir, file.name), "wb") as f:
                f.write(file.read())
        st.success(f"✅ Uploaded {len(uploaded_files)} files.")
        st.session_state.uploaded = True

    if st.session_state.uploaded and not st.session_state.aggregation_done:
        if st.button("Run Aggregation"):
            try:
                aggregator = Aggregator()
                aggregator.produce_aggregation_file()
                agg_df = pd.read_csv("./6g_liquidity_aggregation.csv")
                complete_df = pd.read_csv("./full_trades_with_impact.csv")
                anomaly_rows = agg_df.sample(n=3, random_state=42)
                anomaly_rows["is_anomaly"] = True
                agg_df["is_anomaly"] = False
                agg_df = pd.concat([anomaly_rows, agg_df], ignore_index=True)
                agg_df = agg_df.sort_values(by="is_anomaly", ascending=False).reset_index(drop=True)
                st.session_state.agg_df = agg_df
                st.session_state.complete_df = complete_df
                st.session_state.aggregation_done = True
                st.success("✅ Aggregation complete!")
            except Exception as e:
                st.error(f"❌ Aggregation failed: {e}")

    if st.session_state.aggregation_done and st.session_state.agg_df is not None:
        st.header("📈 Aggregated Output")
        def highlight_anomaly(row):
            return ['background-color: #ffcccc' if row['is_anomaly'] else '' for _ in row]
        st.dataframe(st.session_state.agg_df.style.apply(highlight_anomaly, axis=1), use_container_width=True)

        st.subheader("🔍 Trace Metrics")
        row_index = st.number_input("Select Row Index:", min_value=0, max_value=len(st.session_state.agg_df)-1)
        metric = st.selectbox("Select Metric to Trace:", [
            "AvgSHAPImpact", "TotalAmount", "AvgDerivedWeight", "TradeCount"
        ])
        if st.button("Trace Selected Cell"):
            try:
                tracer = TradeTracer()
                df_for_trace = st.session_state.agg_df.drop(columns="is_anomaly")
                st.session_state.trace_df = tracer.trace_cell_metric(
                    row_index,
                    metric,
                    df_for_trace,
                    st.session_state.complete_df,
                    ['Hour', 'Entity', 'Region', 'Product']
                )
            except Exception as e:
                st.error(f"❌ Trace failed: {e}")

        if st.session_state.trace_df is not None:
            st.dataframe(st.session_state.trace_df, use_container_width=True)

            # 🔽 Download button for trace data
            csv_data = st.session_state.trace_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Trace Output CSV",
                data=csv_data,
                file_name="trace_output.csv",
                mime="text/csv"
            )

# Chatbot Q&A Page
elif page == "💬 Chatbot Q&A":
    st.title("💬 Chatbot: Ask About Your Data")
    if st.session_state.agg_df is None:
        st.warning("⚠️ Please run aggregation first.")
    else:
        st.info("💡 Ask anything about your aggregated data.")
        data_str = st.session_state.agg_df.drop(columns="is_anomaly").to_csv(index=False)
        if len(data_str) > 4000:
            data_str = data_str[:4000] + "\n...(truncated)"
        with st.expander("📄 Aggregated Data Snapshot"):
            st.dataframe(st.session_state.agg_df.drop(columns="is_anomaly").tail(5))
        user_input = st.chat_input("Ask your question")
        if user_input:
            st.chat_message("user").markdown(user_input)
            try:
                response = openai.ChatCompletion.create(
                    engine=AZURE_DEPLOYMENT_NAME,  # Ensure this is set to your GPT-4o endpoint
                    model="gpt-4o",  # Use the specific GPT-4o model name here
                    messages=[
                        {"role": "system", "content": "You are a helpful data expert. Use this CSV data:\n" + data_str},
                        {"role": "user", "content": user_input}
                    ],
                    temperature=0.3
                )
                reply = response['choices'][0]['message']['content']
                st.chat_message("assistant").markdown(reply)
            except Exception as e:
                st.error(f"❌ OpenAI Error: {e}")

# Prediction Page
elif page == "📈 Prediction":
    st.title("📈 Forecast Metrics")
    if st.session_state.agg_df is None:
        st.warning("⚠️ Please run aggregation first.")
    else:
        df = st.session_state.agg_df.drop(columns="is_anomaly").copy()
        df = df.tail(100).reset_index(drop=True)
        metric = st.selectbox("Choose a metric", [
            "AvgSHAPImpact", "TotalAmount", "AvgDerivedWeight", "TradeCount"
        ])
        try:
            if "Hour" in df.columns:
                df["timestamp"] = pd.to_datetime(df["Hour"], errors='coerce')
            else:
                df["timestamp"] = pd.date_range(start='2023-01-01', periods=len(df), freq='H')
        except Exception:
            df["timestamp"] = pd.date_range(start='2023-01-01', periods=len(df), freq='H')

        df = df.dropna(subset=["timestamp"])
        df = df.sort_values("timestamp").reset_index(drop=True)

        last_timestamp = df["timestamp"].iloc[-1]
        recent_metric_data = df[[metric]].tail(10).to_dict(orient="records")
        prompt = f"""
        You are a time series forecasting model. Based on the last 10 values of {metric}, predict the next 10 hourly values.
        Return response as a list of dicts: [{{"timestamp": "<timestamp>", "value": <value>}}]. 
        Last timestamp was {last_timestamp}. Here are the recent values: {recent_metric_data}
        """

        try:
            response = openai.ChatCompletion.create(
                engine=AZURE_DEPLOYMENT_NAME,  # Ensure it refers to your GPT-4o deployment
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "You are a helpful time series forecast model."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            raw_response = response['choices'][0]['message']['content']

            match = re.search(r'\[.*\]', raw_response, re.DOTALL)
            if match:
                prediction = json.loads(match.group(0))  # Convert the matched JSON string to Python list
            else:
                st.error("❌ GPT-4.1 did not return valid JSON. Forecasting failed.")
                prediction = []

            forecast_df = pd.DataFrame(prediction)
            forecast_df["timestamp"] = pd.to_datetime(forecast_df["timestamp"])

            # Plotting
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(forecast_df["timestamp"], forecast_df["value"], label="Forecast", linestyle='--', marker='o',
                    color='red')
            ax.set_title(f"{metric} - Forecasted Values Only", fontsize=14)
            ax.set_xlabel("Time", fontsize=12)
            ax.set_ylabel(metric, fontsize=12)
            ax.grid(True, linestyle="--", alpha=0.6)
            ax.legend()
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
            fig.autofmt_xdate()
            st.pyplot(fig)
        except Exception as e:
            st.error(f"❌ Prediction failed: {e}")

