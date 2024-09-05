import streamlit as st
import utils  # Import utility functions from utils.py
import plotly.express as px
import pandas as pd

def comparison_tool_page():
    st.title("🆚 Watch Comparison Tool")

    # Fetch data using utils
    df = utils.fetch_data()

    # Exclude 'id' or any other unwanted columns from the numerical columns
    numeric_cols = df.select_dtypes(include='number').columns.drop(['id'])

    # User Inputs
    st.sidebar.header("🔍 Select Watches to Compare")
    brand_1 = st.sidebar.selectbox("Select Brand 1", df['brand'].unique())
    model_1 = st.sidebar.selectbox("Select Model 1", df[df['brand'] == brand_1]['model'].unique())
    brand_2 = st.sidebar.selectbox("Select Brand 2", df['brand'].unique())
    model_2 = st.sidebar.selectbox("Select Model 2", df[df['brand'] == brand_2]['model'].unique())

    # Filter data
    watch_1 = df[(df['brand'] == brand_1) & (df['model'] == model_1)]
    watch_2 = df[(df['brand'] == brand_2) & (df['model'] == model_2)]

    # Select only numerical columns for comparison
    watch_1_mean = watch_1[numeric_cols].mean().rename(f'{brand_1} {model_1}')
    watch_2_mean = watch_2[numeric_cols].mean().rename(f'{brand_2} {model_2}')

    # Combine the means into a DataFrame for plotting
    comparison_df = pd.DataFrame({f'{brand_1} {model_1}': watch_1_mean, f'{brand_2} {model_2}': watch_2_mean}).reset_index()

    # Comparison Visualization
    st.header(f"Comparison of {model_1} and {model_2}")
    fig = px.bar(comparison_df, x='index', y=[f'{brand_1} {model_1}', f'{brand_2} {model_2}'], barmode='group', title="Comparison of Key Metrics")
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    comparison_tool_page()
