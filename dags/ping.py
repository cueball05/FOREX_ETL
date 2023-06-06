from datetime import datetime, date
from datetime import timedelta
from airflow import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook
import pandas as pd
import json
from pandas import json_normalize

current_date=datetime.today().strftime('%Y-%m-%d')

# defines the default arguments the dags will follow
default_args = {
    "owner": "Airflow",
    "start_date": datetime(2023,5,23),
    "retries": 1,
    "retry_delay": timedelta(minutes=5)

}


def _process_data(ti):
    data = ti.xcom_pull(task_ids='extract_user') # extract json object from XCom
    data = data['rates'] # gets the values in 'rates' key
    df = pd.DataFrame(columns = ['rate','symbol','date_crawled']) #creates empty dataframe with columns
    temp_dict = dict() #creates empty dictionary to things

    # json_normalize: normalizes semi-structured json into a flat table.
    for symbol, rate in data.items():
        temp_dict = json_normalize({
            'rate': float(rate),
            'symbol': symbol,
            'date_crawled': current_date
        }
        )
        df = pd.concat([df, temp_dict])

    df.to_csv('/tmp/processed_data.csv', index =None, header=False)


def _store_data():
    pg_hook = PostgresHook(postgres_conn_id = 'postgres')

    pg_hook.copy_expert(
        sql = "COPY rates FROM stdin WITH DELIMITER as ','",
        filename='/tmp/processed_data.csv'
    )



with DAG('forex_pipeline', default_args=default_args, schedule_interval = "0 8 * * *", catchup=False) as dag:


    is_api_available = HttpSensor(
        task_id = "is_api_available",
        method='GET',
        http_conn_id='is_api_available',
        endpoint= 'latest?apikey=TkbexcPknZDkRQSAJntfHCm2BNYVXnJ2',
        response_check=lambda response: "EUR" in response.text,
        poke_interval= 5

    )

    create_table = PostgresOperator(
        task_id="create_table",
        postgres_conn_id='postgres',
        sql = '''
            CREATE TABLE IF NOT EXISTS rates(
                rate FLOAT NOT NULL,
                symbol TEXT NOT NULL,
                date_crawled DATE NOT NULL
                
            
            );
            '''
       )

    #make a request and extract data
    extract_data = SimpleHttpOperator(
        task_id = 'extract_user',
        method='GET',
        http_conn_id = 'is_api_available',
        endpoint = 'latest?apikey=TkbexcPknZDkRQSAJntfHCm2BNYVXnJ2',
        response_filter=lambda response: json.loads(response.text),
        log_response= True

    )
    # use Airflow PythonOperator to call the function _process_data
    transform_data = PythonOperator(
        task_id='transform_data',
        python_callable=_process_data

    )

    # use Airflow PythonOperator to call the function _store_data
    load_data = PythonOperator(
        task_id='load_data',
        python_callable=_store_data

    )

    #Dependencies
    is_api_available >> create_table >> extract_data >> transform_data >> load_data
