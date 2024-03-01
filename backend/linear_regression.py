import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression


class ProcessLinearRegression:
    
    def __init__(self, household: str):
        self.household = household
        
    
    
    def _get_data(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = f"SELECT * FROM sensor_data WHERE household = ?;"
            df = pd.read_sql_query(query, conn, params=(self.household, ))
            conn.commit()
    
            return df
        
        
    def get_x_and_y(self):
        raw_data = self._get_data()
        x = raw_data['temperature']
        y = raw_data['energy']
        
        from sklearn.model_selection import train_test_split
        
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.4)

        from sklearn.linear_model import LinearRegression

        model = LinearRegression()

        model.fit(x_train, y_train)

        print(model.coef_)

        print(model.intercept_)

        pd.DataFrame(model.coef_, x.columns, columns = ['Coeff'])

        predictions = model.predict(x_test)

        plt.scatter(y_test, predictions)
        plt.xlabel("Temperature")
        plt.ylabel("Energy")
        plt.title("Linear Regression - Temperature vs Energy")


class DisplayLinearRegression:

    def display_linear_regression(self, dataset, feature_columns, target_column, test_size, random_state):
        """
        Performs linear regression on a given dataset with specified features and target.

        Parameters:
        - dataset: pandas DataFrame, the dataset to perform regression on.
        - feature_columns: list of str, names of the columns to use as features.
        - target_column: str, name of the column to use as target.
        - test_size: float, proportion of the dataset to include in the test split.
        - random_state: int, seed used by the random number generator for reproducibility.

        Returns:
        - Plots the actual vs predicted values along with the regression line.
        """
        # Select features and target from the dataset
        X = dataset[feature_columns]
        y = dataset[target_column]
        
        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
        
        # Reshape features for the model if only one feature column is specified
        if len(feature_columns) == 1:
            X_train = np.array(X_train).reshape(-1, 1)
            X_test = np.array(X_test).reshape(-1, 1)
        
        # Initialize and train the linear regression model
        lr = LinearRegression()
        lr.fit(X_train, y_train)

        # Predict using the test set
        Y_pred = lr.predict(X_test)

        # Plot the results
        plt.scatter(X_test, y_test)
        plt.plot(X_test, Y_pred, color='red')
        plt.xlabel(feature_columns[0] if len(feature_columns) == 1 else 'Features')
        plt.ylabel(target_column)
        plt.title('Linear Regression Analysis')
        plt.show()