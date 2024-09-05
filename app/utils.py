import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import plotly.graph_objs as go
import os
from sklearn.preprocessing import LabelEncoder
import numpy as np
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
import streamlit as st
from dotenv import load_dotenv
from scipy.stats import norm


load_dotenv()

# Config

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

"""
# Function to fetch data from Chrono24 API
def fetch_data_from_chrono24():
    url = "https://api.chrono24.com/v1/watchlistings"  # Example endpoint
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data['listings'])
    return df

"""

@st.cache_resource
def get_engine():
    """
    Create and return a SQLAlchemy engine for PostgreSQL.
    """
    engine_url = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    return create_engine(engine_url)

@st.cache_resource
def fetch_data():
    """
    Fetches watch data from the PostgreSQL database.
    """
    engine = get_engine()
    query = "SELECT * FROM chrono.watch_prices"
    return pd.read_sql(query, engine)

def plot_avg_price_trend(df):
    df['date'] = pd.to_datetime(df['date_gathered']).dt.date  # Convert to date to keep it daily
    avg_price_trend = df.groupby(['date', 'brand'])['price'].mean().reset_index()
    fig = px.line(avg_price_trend, x='date', y='price', color='brand')
    return fig

def z_score_outliers(df):
    df['z_score'] = (df['price'] - df['price'].mean()) / df['price'].std()
    return df[df['z_score'] < -2]

def percentile_filtering(df, percentile=20):
    threshold = np.percentile(df['price'], percentile)
    return df[df['price'] < threshold]

def regression_residuals(df):
    X = df[['condition', 'certification_status']].copy()
    X = pd.get_dummies(X, drop_first=True)
    y = df['price']
    model = LinearRegression().fit(X, y)
    df['predicted_price'] = model.predict(X)
    df['residuals'] = df['predicted_price'] - df['price']
    return df[df['residuals'] < 0]

def plot_box_plot(df):
    box_fig = px.box(df, 
                     x='model', 
                     y='price', 
                     color='certification_status', 
                     title=f"Price Distribution for {df['model'].iloc[0]}")
    return box_fig

def plot_normal_distribution(df):
    prices = df['price']
    mean = prices.mean()
    std = prices.std()
    
    x = np.linspace(min(prices), max(prices), 100)
    y = norm.pdf(x, mean, std)
    
    hist_data = go.Histogram(x=prices, histnorm='probability density', name='Price Distribution')
    norm_curve = go.Scatter(x=x, y=y, mode='lines', name='Normal Distribution', line=dict(color='red'))

    fig = go.Figure(data=[hist_data, norm_curve])
    fig.update_layout(title="Normal Distribution vs Price Distribution", xaxis_title="Price", yaxis_title="Density")
    
    return fig