# FOREX_ETL

An ETL pipeline using Docker and Airflow to extract foreign exchange rates and place them into a CSV file.  

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
