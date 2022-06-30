import sys
sys.path.append("/opt/airflow/jobs")
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from pyspark.sql import SparkSession
from datetime import datetime
import process_immigration


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
    'TEST_DAG_LOCAL',
    # These args will get passed on to each operator
    # You can override them on a per-task basis during operator initialization
    default_args={
        'depends_on_past': False,
        'email': ['airflow@example.com'],
        'email_on_failure': False,
        'email_on_retry': False,
        # 'retries': 1,
        # 'queue': 'bash_queue',
        # 'pool': 'backfill',
        # 'priority_weight': 10,
        # 'end_date': datetime(2016, 1, 1),
        # 'wait_for_downstream': False,
        # 'sla': timedelta(hours=2),
        # 'execution_timeout': timedelta(seconds=300),
        # 'on_failure_callback': some_function,
        # 'on_success_callback': some_other_function,
        # 'on_retry_callback': another_function,
        # 'sla_miss_callback': yet_another_function,
        # 'trigger_rule': 'all_success'
    },
    description='Process immigration data',
    # schedule_interval=timedelta(days=1),
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=['data-engineering'],
) as dag:

    # t1, t2 and t3 are examples of tasks created by instantiating operators
    t1 = PythonOperator(
        task_id='process_immigration_data',
        provide_context=True,
        python_callable=process_immigration.process_immigration_data,
        op_kwargs={
            'spark': spark,
            'input_path': 'data/sas_data/part-00000-b9542815-7a8d-45fc-9c67-c9c5007ad0d4-c000.snappy.parquet',
            'output_path': 'output_data/'
        },
        dag=dag
    )


t1
