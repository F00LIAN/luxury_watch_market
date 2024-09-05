import streamlit as st
import plotly.express as px
import utils  # Import utility functions from utils.py

def home_page():
    st.title("⌚️ Watch Market Overview")
    # st.image("market_overview_image.jpg")  # Replace with your image file path

    # Fetch data using utils
    df = utils.fetch_data()

    # Exclude rows where price is 0
    df = df[df['price'] > 0]

    # User input for watch selection
    st.sidebar.header("🔍 Find Watches")
    selected_brand = st.sidebar.selectbox("Select Brand", df['brand'].unique())
    selected_model = st.sidebar.selectbox("Select Model", df[df['brand'] == selected_brand]['model'].unique())

    # Visualization: Market Overview
    st.header("Market Price Trends")
    fig = utils.plot_avg_price_trend(df)
    st.plotly_chart(fig, use_container_width=True)

    # Filter data for the selected brand and model
    df = df[(df['brand'] == selected_brand) & (df['model'] == selected_model)]

    # Tabs for additional analysis
    tab1, tab2, tab3 = st.tabs(["📈 Below Market", "📉 Undervalued", "📊 Price Distribution"])

    with tab1:
        st.subheader(f"{selected_model} Watches Below Market Price")
        below_market_df = df[(df['brand'] == selected_brand) & 
                             (df['model'] == selected_model) & 
                             (df['price'] < df['price'].quantile(0.25))]
        st.dataframe(below_market_df[['model', 'price', 'certification_status', 'url', 'date_gathered']])
    
    with tab2:
        st.subheader("Undervalued Watch Analysis")

        # Dropdown for selecting analysis method
        analysis_method = st.selectbox(
            "Choose an analysis method:",
            ["Z-Score Analysis", "Percentile Filtering", "Regression Residuals"]
        )

        if analysis_method == "Z-Score Analysis":
            st.write("### Z-Score Outliers")
            z_outliers = utils.z_score_outliers(df)
            st.dataframe(z_outliers)

        elif analysis_method == "Percentile Filtering":
            st.write("### Percentile Filtering (20th Percentile)")
            percentile_outliers = utils.percentile_filtering(df, percentile=20)
            st.dataframe(percentile_outliers)

        elif analysis_method == "Regression Residuals":
            st.write("### Regression Residuals Analysis")
            regression_outliers = utils.regression_residuals(df)
            st.dataframe(regression_outliers)

    with tab3:
        st.subheader("Price Distribution Analysis")
        plot_type = st.radio("Select Plot Type", ["Box Plot", "Normal Distribution"])

        if plot_type == "Box Plot":
            st.plotly_chart(utils.plot_box_plot(df), use_container_width=True)
        
        elif plot_type == "Normal Distribution":
            norm_fig = utils.plot_normal_distribution(df)
            st.plotly_chart(norm_fig, use_container_width=True)

if __name__ == "__main__":
    home_page()
