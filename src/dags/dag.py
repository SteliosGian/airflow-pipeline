import sys
sys.path.append("/opt/airflow/")
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from pyspark.sql import SparkSession
from datetime import datetime
from jobs import (process_demographics, process_immigration, process_label, process_temperature)


def create_spark_session() -> SparkSession:
    """
    Create a Spark session
    :return: Spark session
    """
    spark = SparkSession.builder \
                        .config("spark.jars.repositories", "https://repos.spark-packages.org/") \
                        .config("spark.jars.packages", "saurfang:spark-sas7bdat:2.0.0-s_2.11") \
                        .enableHiveSupport() \
                        .getOrCreate()
    return spark


spark = create_spark_session()
spark.sparkContext.addPyFile("jobs/process_demographics.py")
spark.sparkContext.addPyFile("jobs/process_immigration.py")
spark.sparkContext.addPyFile("jobs/process_label.py")
spark.sparkContext.addPyFile("jobs/process_temperature.py")

with DAG(
    'process_data_local',
    default_args={
        'depends_on_past': False,
        'email': ['steliosgiannik@gmail.com'],
        'email_on_failure': False,
        'email_on_retry': False
    },
    description='Process data',
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=['data-engineering'],
) as dag:

    process_imig = PythonOperator(
        task_id='process_immigration_data',
        provide_context=True,
        python_callable=process_immigration.process_immigration_data,
        op_kwargs={
            'spark': spark,
            'input_path': 'data/sas_data',
            'output_path': 'output_data/'
        },
        dag=dag
    )

    process_demog = PythonOperator(
        task_id='process_demographics_data',
        provide_context=True,
        python_callable=process_demographics.process_demog_data,
        op_kwargs={
            'spark': spark,
            'input_path': 'data/us-cities-demographics.csv',
            'output_path': 'output_data/'
        },
        dag=dag
    )

    process_label = PythonOperator(
        task_id='process_label_data',
        provide_context=True,
        python_callable=process_label.process_label_descriptions,
        op_kwargs={
            'spark': spark,
            'input_path': 'data/I94_SAS_Labels_Descriptions.SAS',
            'output_path': 'output_data/'
        },
        dag=dag
    )

    process_temperature = PythonOperator(
        task_id='process_temperature_data',
        provide_context=True,
        python_callable=process_temperature.process_temp_data,
        op_kwargs={
            'spark': spark,
            'input_path': 'data/GlobalLandTemperaturesByCity.csv',
            'output_path': 'output_data/'
        },
        dag=dag
    )


[process_imig, process_demog, process_label, process_temperature]
