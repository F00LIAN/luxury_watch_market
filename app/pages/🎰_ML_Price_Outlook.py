import streamlit as st
import utils
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import plotly.express as px

def machine_learning_outlook_page():
    st.title("🤖 Machine Learning Price Outlook")

    # Fetch data using utils
    df = utils.fetch_data()

    # Model selection
    st.header("Choose a Machine Learning Model")
    model_choice = st.selectbox("Select Model", ["Random Forest", "Gradient Boosting", "Support Vector Regressor"])

    if st.button("Run Model"):
        # Show basic EDA
        st.header("Exploratory Data Analysis (EDA)")
        
        # Correlation heatmap
        st.subheader("Correlation Heatmap")
        corr_matrix = df[['price', 'shipping_price']].corr()
        fig, ax = plt.subplots()
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=ax)
        st.pyplot(fig)

        # Pairplot for numerical features
        st.subheader("Pairplot for Numerical Features")
        fig = sns.pairplot(df[['price', 'shipping_price']])
        st.pyplot(fig)

        # Define features
        categorical_features = ['certification_status', 'condition', 'merchant_name', 'badge']
        numerical_features = ['shipping_price']

        # Define target variable
        y = df['price']

        # Preprocessing for categorical data
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])

        # Preprocessing for numerical data
        numerical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='mean')),
            ('scaler', StandardScaler()) if model_choice == "Support Vector Regressor" else ('passthrough', 'passthrough')  # Scaling only for SVR
        ])

        # Combine preprocessing steps
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numerical_transformer, numerical_features),
                ('cat', categorical_transformer, categorical_features)
            ])

        # Select model based on user choice
        if model_choice == "Random Forest":
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        elif model_choice == "Gradient Boosting":
            model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        elif model_choice == "Support Vector Regressor":
            model = SVR(kernel='rbf', C=1.0, epsilon=0.2)

        # Define the model pipeline
        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('regressor', model)
        ])

        # Split data into training and testing sets
        X = df[categorical_features + numerical_features]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Fit the model
        pipeline.fit(X_train, y_train)

        # Predictions and evaluation
        predictions = pipeline.predict(X_test)
        mse = mean_squared_error(y_test, predictions)

        st.write(f"Model Mean Squared Error: {mse}")

        # Feature Importance (only for models that provide it)
        if model_choice in ["Random Forest", "Gradient Boosting"] and hasattr(pipeline.named_steps['regressor'], 'feature_importances_'):
            feature_importance = pd.DataFrame({
                'feature': numerical_features + list(pipeline.named_steps['preprocessor'].transformers_[1][1]['onehot'].get_feature_names_out(categorical_features)),
                'importance': pipeline.named_steps['regressor'].feature_importances_
            }).sort_values(by='importance', ascending=False)

            st.header("Feature Importance in Driving Price")
            fig = px.bar(feature_importance, x='importance', y='feature', title='Feature Importance')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("Feature importance is not available for the selected model.")

if __name__ == "__main__":
    machine_learning_outlook_page()
