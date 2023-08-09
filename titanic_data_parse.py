import base64
import io
import json
import sqlite3

import pandas as pd
from typing import Optional

from flask import jsonify
from matplotlib import pyplot as plt


class TitanicDataParser:
    def __init__(self, csv_path: Optional[str] = None, sqlite_connection: Optional[sqlite3.Connection] = None,
                 table_name: Optional[str] = None):
        if csv_path:
            self.df = pd.read_csv(csv_path, header=0)
        elif sqlite_connection:
            self.read_sql_data_to_df(sqlite_connection, table_name)

    def read_sql_data_to_df(self, sqlite_connection, table_name):
        # Read data from the database into a DataFrame
        query = f"SELECT * FROM {table_name}"
        self.df = pd.read_sql_query(query, sqlite_connection)
        self.conn.close()


    def get_fare_prices_histogram(self):
        # Sample data (percentage values)
        total_fare_sum = self.df['Fare'].sum()
        self.df["Fare Percent"] = (self.df['Fare'] / total_fare_sum) * 100

        # Divide into 10 groups and calculate the count for each group
        self.df['Percen Group'] = pd.cut(self.df["Fare Percent"], bins=10,
                                         labels=[f'{i * 10}-{(i + 1) * 10}%' for i in range(10)])
        group_counts = self.df['Percen Group'].value_counts().sort_index()

        # Plot the bar chart
        plt.figure(figsize=(10, 6))
        ax = group_counts.plot(kind='bar', color='skyblue')

        # Add labels and title
        plt.xlabel('Percentage Range')
        plt.ylabel('Count of Passengers')
        plt.title('Count of Titanic Passengers in Fare Percentage Ranges')
        plt.xticks(rotation=45)

        # Add text labels for max percentage range above each bar
        for p in ax.patches:
            ax.annotate(f'{p.get_height()}', (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='center', fontsize=10, color='black', xytext=(0, 5),
                        textcoords='offset points')

        # Save the plot to a BytesIO object
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)

        # Convert the image to a base64 encoded string
        img_data = base64.b64encode(img_buffer.read()).decode('utf-8')
        return img_data

    def get_single_passenger_data(self, passenger_id, specific_attributes=[]):
        # Filter the DataFrame to get the right passenger ID row
        filtered_df = self.df[self.df["PassengerId"] == passenger_id]
        if specific_attributes:
            filtered_df=filtered_df[specific_attributes]
        # Check if any row matches the filter
        if not filtered_df.empty:
            # Get the first matching row (assuming there is only one)
            row = filtered_df.iloc[0]
            row_dict = row.to_dict()
            json_data = json.dumps(row_dict)
            return json_data

    def get_all_passengers_data(self):
        json_list = []
        for index, row in self.df.iterrows():
            json_list.append(json.loads(row.to_json()))
        return json_list


# titanic_data = TitanicDataParser('Name')
# titanic_data.get_fare_prices_histogram()
# print('here')
