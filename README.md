# FOREX_ETL

An ETL pipeline using Docker and Airflow that makes a call to an API endpoint and extracts foreign exchange rates and places them into a CSV file.  

The DAG file `ping.py` contains 5 DAGS that will perform the ETL process. 


## DAG 1: is_api_available

Uses the Airflow `HttpSensor` class to determine if the API is available.


## DAG 2: create_table

Uses the Airflow `PostgresOperator` class to create a table if it does not exist in a specific ddatabase


## DAG 3: extract_user

Makes a request to the API endpoint and extract the data


## DAG 4: transform_data

Calls the user defined function `_process_data` that pulls the extracted data from Airflow's X-Com, converts it into a dataframe and saves said dataframe into a CSV file


## DAG 5: load_data

Calls the user defined function `_store_data` that copies the content from the CSV file into the table rates using Airflow's `PostgresHook`


## Aifrlow Configuration

In Admin -> Connections -> New Connection, make a connection to `https://api.apilayer.com/fixer/` under Host. This will allow Airflow to make a call to the API and its endpoint
![image](https://github.com/cueball05/FOREX_ETL/assets/89449921/b96c3aec-c0db-4580-b380-cc635e68e5e5)

In Admin -> Connections -> New Connection, make a connection to postgres with the following setttings. This will allow Airflow to talk to postgresql to create tables and dump data
![image](https://github.com/cueball05/FOREX_ETL/assets/89449921/dc41a200-4102-44b9-93e0-3fb8ca1c362a)
