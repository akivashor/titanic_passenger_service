import base64
import io
import json
import sqlite3
from typing import Optional, List, Union

import pandas as pd
from matplotlib import pyplot as plt


class TitanicDataParser:
    def __init__(self, csv_path: Optional[str] = None, sqlite_connection: Optional[sqlite3.Connection] = None,
                 table_name: Optional[str] = None):
        """
        Initialize the TitanicDataParser instance.

        :param csv_path: Path to a CSV file containing Titanic dataset.
        :param sqlite_connection: SQLite database connection.
        :param table_name: Name of the table in the SQLite database.
        """
        if csv_path:
            self.df = pd.read_csv(csv_path, header=0)
        elif sqlite_connection:
            self.read_sql_data_to_df(sqlite_connection, table_name)

    def read_sql_data_to_df(self, sqlite_connection: sqlite3.Connection, table_name: str) -> None:
        """
        Read data from an SQLite table into a DataFrame.

        :param sqlite_connection: SQLite database connection.
        :param table_name: Name of the table to read.
        """
        query = f"SELECT * FROM {table_name}"
        self.df = pd.read_sql_query(query, sqlite_connection)
        sqlite_connection.close()

    def get_fare_prices_histogram(self) -> str:
        """
        Generate and return a base64-encoded image of the histogram of fare prices.

        :return: Base64-encoded image data.
        """
        total_fare_sum = self.df['Fare'].sum()
        self.df["Fare Percent"] = (self.df['Fare'] / total_fare_sum) * 100

        self.df['Percen Group'] = pd.cut(self.df["Fare Percent"], bins=10,
                                         labels=[f'{i * 10}-{(i + 1) * 10}%' for i in range(10)])
        group_counts = self.df['Percen Group'].value_counts().sort_index()

        plt.figure(figsize=(10, 6))
        ax = group_counts.plot(kind='bar', color='skyblue')

        plt.xlabel('Percentage Range')
        plt.ylabel('Count of Passengers')
        plt.title('Count of Titanic Passengers in Fare Percentage Ranges')
        plt.xticks(rotation=45)

        for p in ax.patches:
            ax.annotate(f'{p.get_height()}', (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='center', fontsize=10, color='black', xytext=(0, 5),
                        textcoords='offset points')

        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)

        img_data = base64.b64encode(img_buffer.read()).decode('utf-8')
        return img_data

    def get_single_passenger_data(self, passenger_id: int, specific_attributes: List[str] = None) -> Union[str, None]:
        """
        Get data for a specific passenger from Titanic dataset.

        :param passenger_id: Passenger ID.
        :param specific_attributes: List of specific attributes to retrieve.
        :return: JSON-encoded passenger data or None if no match is found.
        """
        filtered_df = self.df[self.df["PassengerId"] == passenger_id]
        if specific_attributes:
            filtered_df = filtered_df[specific_attributes]

        if not filtered_df.empty:
            row = filtered_df.iloc[0]
            row_dict = row.to_dict()
            json_data = json.dumps(row_dict)
            return json_data

    def get_all_passengers_data(self) -> List[dict]:
        """
        Get data for all passengers from Titanic dataset.

        :return: List of dictionaries containing passenger data.
        """
        json_list = []
        for index, row in self.df.iterrows():
            json_list.append(json.loads(row.to_json()))
        return json_list
