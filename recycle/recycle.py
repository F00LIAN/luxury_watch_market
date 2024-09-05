### Visuaization Utils

"""
def plot_avg_price_trend(df):
    df['month'] = pd.to_datetime(df['date_gathered']).dt.to_period('M').dt.to_timestamp()
    avg_price_trend = df.groupby(['month', 'brand'])['price'].mean().reset_index()
    fig = px.line(avg_price_trend, x='month', y='price', color='brand')
    return fig
"""

"""

# User input for watch selection
    st.sidebar.header("🔍 Find Below Market Watches")
    selected_brand = st.sidebar.selectbox("Select Brand", df['brand'].unique())
    selected_model = st.sidebar.selectbox("Select Model", df[df['brand'] == selected_brand]['model'].unique())

    # Cluster Analysis (dummy implementation for below market detection)
    st.header(f"{selected_model} Watches Below Market Price")
    below_market_df = df[(df['brand'] == selected_brand) & (df['model'] == selected_model) & (df['price'] < df['price'].quantile(0.25))]
    st.dataframe(below_market_df[['model', 'price', 'certification_status', 'url', 'date_gathered']])

    # Visualization: Undervalued Watches
    st.header("Undervalued Watch Analysis")
    st.write("These are watches that are statistically farther from the price distribution:")

    # Filter data for the selected brand and model
    filtered_df = df[(df['brand'] == selected_brand) & (df['model'] == selected_model)]

    # Calculate the lower and upper bounds for outlier detection (1.5 * IQR rule)
    Q1 = filtered_df['price'].quantile(0.25)
    Q3 = filtered_df['price'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Identify undervalued watches (prices below the lower bound)
    undervalued_df = filtered_df[filtered_df['price'] < lower_bound]

    if not undervalued_df.empty:
        # Plotting the data with interactive tooltips for image and URL
        fig = px.scatter(undervalued_df, 
                         x='date_gathered', 
                         y='price', 
                         color='condition', 
                         hover_data={'image_url': False, 'url': False},
                         hover_name='model',
                         title=f"{selected_model} Undervalued Watches")

        # Add custom tooltips for image and URL
        fig.update_traces(
            hovertemplate="<b>%{hovertext}</b><br>Price: %{y}<br>Condition: %{marker.color}<br>"
                          "<a href='%{customdata[1]}'>Link</a><br>"
                          "<img src='%{customdata[0]}' width='150px'>",
            customdata=undervalued_df[['image_url', 'url']]
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No undervalued watches found based on the current criteria.")

    # Box Plot for Price Distribution
    st.header("Price Distribution Analysis")
    box_fig = px.box(filtered_df, 
                     x='model', 
                     y='price', 
                     color='certification_status', 
                     title=f"Price Distribution for {selected_model}")
    st.plotly_chart(box_fig, use_container_width=True)
"""