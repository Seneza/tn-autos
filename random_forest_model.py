"""A module for random_forest_model."""

# random_forest_model.py

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


class RandomForestModel:
    """
    A class used to train and evaluate a Random Forest regression model for predicting business counts based on population data.

    Attributes:
        X (pd.DataFrame): Feature DataFrame containing the 'Population_2020' column.
        y (pd.Series): Target Series containing the 'business_count' data.
    """

    def __init__(self, df_model: pd.DataFrame):
        """
        Initialize the RandomForestModel with the provided dataset.

        Parameters:
            df_model (pd.DataFrame): DataFrame containing the features and target variable.
                                     Expected to have 'Population_2020' and 'business_count' columns.
        """
        self.X = df_model[["Population_2020"]]
        self.y = df_model["business_count"]

    def train_model(self) -> tuple:
        """
        Train the Random Forest regression model and evaluate its performance.

        This method splits the data into training and testing sets, fits a Random Forest regressor,
        makes predictions on the test set, and calculates evaluation metrics.

        Returns:
            tuple: A tuple containing the trained RandomForestRegressor model, Mean Squared Error (mse),
                   R-squared score (r2), test features (X_test), true target values (y_test), and predicted values (y_pred).

        Raises:
            ValueError: If the model training fails.
        """
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                self.X, self.y, test_size=0.2, random_state=42
            )
            rf = RandomForestRegressor(n_estimators=100, random_state=42)
            rf.fit(X_train, y_train)

            y_pred = rf.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            return rf, mse, r2, X_test, y_test, y_pred
        except Exception as e:
            raise ValueError("An error occurred during model training.") from e
