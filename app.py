import json
import sqlite3
from fastapi import FastAPI, Query
import uvicorn
from titanic_data_parse import TitanicDataParser

app = FastAPI()


def get_titanic_object():
    """
    Load TitanicDataParser object based on data source configuration.
    """
    with open('data_config.json', 'r') as config_file:
        data_config = json.load(config_file)

    if data_config["data_source"] == "csv":
        titanic_data = TitanicDataParser(csv_path=data_config["csv_file_path"])
    elif data_config["data_source"] == "sqlite":
        conn = sqlite3.connect(data_config["sqlite_db_file"])
        titanic_data = TitanicDataParser(sqlite_connection=conn)
    return titanic_data


@app.get('/hist')
async def get_fare_histogram():
    """
    Get the histogram of fare prices from Titanic dataset.
    """
    titanic_data = get_titanic_object()
    hist = titanic_data.get_fare_prices_histogram()
    return {'image': hist}


@app.get('/passenger/{passenger_id}')
async def get_passenger_data(
        passenger_id: int,
        attributes: str = Query(None, description="Comma-separated list of attributes to retrieve")
):
    """
    Get data for a specific passenger from Titanic dataset.

    :param passenger_id: Passenger ID.
    :param attributes: Comma-separated list of attributes to retrieve.
    """
    titanic_data = get_titanic_object()
    attribute_list = attributes.split(',') if attributes else []
    passenger_data = titanic_data.get_single_passenger_data(passenger_id, attribute_list)
    return {'passenger_data': passenger_data}


@app.get('/passengers')
async def get_passengers_data():
    """
    Get data for all passengers from Titanic dataset.
    """
    titanic_data = get_titanic_object()
    passengers_data = titanic_data.get_all_passengers_data()
    return {'passengers_data': passengers_data}


def run():
    """
    Run the FastAPI application using UVicorn server.
    """
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == '__main__':
    run()
