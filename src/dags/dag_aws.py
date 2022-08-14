import sys
sys.path.append("/opt/airflow/")
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.contrib.operators.emr_create_job_flow_operator import EmrCreateJobFlowOperator
from pyspark.sql import SparkSession
from airflow.contrib.operators.emr_add_steps_operator import EmrAddStepsOperator
from airflow.contrib.sensors.emr_step_sensor import EmrStepSensor
from airflow.contrib.operators.emr_terminate_job_flow_operator import (
    EmrTerminateJobFlowOperator,
)
from datetime import datetime
from jobs import (process_demographics, process_immigration, process_label, process_temperature)

BUCKET_NAME = 'st-proj-airflow-bucket-data-eng'
PROCESS_IMMIGRATION = 'src/jobs/process_immigration.py'
PROCESS_DEMOGRAPHICS = 'src/jobs/process_demographics.py'
PROCESS_LABEL = 'src/jobs/process_label.py'
PROCESS_TEMPERATURE = 'src/jobs/process_temperature.py'

JOB_FLOW_OVERRIDES = {
    "Name": "Data Processing",
    "ReleaseLabel": "emr-5.29.0",
    "Applications": [{"Name": "Hadoop"}, {"Name": "Spark"}],  # We want our EMR cluster to have HDFS and Spark
    "Configurations": [
        {
            "Classification": "spark-env",
            "Configurations": [
                {
                    "Classification": "export",
                    "Properties": {"PYSPARK_PYTHON": "/usr/bin/python3"},  # by default EMR uses py2, change it to py3
                }
            ],
        }
    ],
    "Instances": {
        "InstanceGroups": [
            {
                "Name": "Master node",
                "Market": "ON_DEMAND",
                "InstanceRole": "MASTER",
                "InstanceType": "m4.xlarge",
                "InstanceCount": 1,
            },
            {
                "Name": "Core - 2",
                "Market": "ON_DEMAND",  # Spot instances are a "use as available" instances
                "InstanceRole": "CORE",
                "InstanceType": "m4.xlarge",
                "InstanceCount": 2,
            },
        ],
        "KeepJobFlowAliveWhenNoSteps": True,
        "TerminationProtected": False,  # this lets us programmatically terminate the cluster
    },
    "JobFlowRole": "EMR_EC2_DefaultRole",
    "ServiceRole": "EMR_DefaultRole",
}


SPARK_STEPS = [
    {
        "Name": "Process immigration data",
        "ActionOnFailure": "CANCEL_AND_WAIT",
        "HadoopJarStep": {
            "Args": [
                "spark-submit",
                "--deploy-mode",
                "client",
                "s3://{{ params.BUCKET_NAME }}/{{ params.process_immigration }}"
            ],
        },
    },
    {
        "Name": "Process Demographics data",
        "ActionOnFailure": "CANCEL_AND_WAIT",
        "HadoopJarStep": {
            "Args": [
                "spark-submit",
                "--deploy-mode",
                "client",
                "s3://{{ params.BUCKET_NAME }}/{{ params.process_demographics }}"
            ],
        },
    },
    {
        "Name": "Process label data",
        "ActionOnFailure": "CANCEL_AND_WAIT",
        "HadoopJarStep": {
            "Args": [
                "spark-submit",
                "--deploy-mode",
                "client",
                "s3://{{ params.BUCKET_NAME }}/{{ params.process_label }}"
            ],
        },
    },
    {
        "Name": "Process temperature data",
        "ActionOnFailure": "CANCEL_AND_WAIT",
        "HadoopJarStep": {
            "Args": [
                "spark-submit",
                "--deploy-mode",
                "client",
                "s3://{{ params.BUCKET_NAME }}/{{ params.process_temperature }}"
            ],
        },
    }
]

with DAG(
    'process_data',
    default_args={
        'depends_on_past': False,
        'email': ['steliosgiannik@gmail.com'],
        'email_on_failure': False,
        'email_on_retry': False,
    },
    description='Process data',
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=['data-engineering'],
) as dag:
    create_emr_cluster = EmrCreateJobFlowOperator(
        task_id="create_emr_cluster",
        job_flow_overrides=JOB_FLOW_OVERRIDES,
        aws_conn_id="aws_default",
        emr_conn_id="emr_default",
        dag=dag
    )

    step_adder = EmrAddStepsOperator(
        task_id="add_steps",
        job_flow_id="{{ task_instance.xcom_pull(task_ids='create_emr_cluster', key='return_value') }}",
        aws_conn_id="aws_default",
        steps=SPARK_STEPS,
        params={
            "BUCKET_NAME": BUCKET_NAME,
            "process_immigration": PROCESS_IMMIGRATION,
            "process_demographics": PROCESS_DEMOGRAPHICS,
            "process_label": PROCESS_LABEL,
            "process_temperature": PROCESS_TEMPERATURE
        },
        dag=dag
    )

    last_step = len(SPARK_STEPS) -1

    step_checker = EmrStepSensor(
        task_id="watch_step",
        job_flow_id="{{ task_instance.xcom_pull('create_emr_cluster', key='return_value') }}",
        step_id="{{ task_instance.xcom_pull(task_ids='add_steps', key='return_value')["
        + str(last_step)
        + "] }}",
        aws_conn_id="aws_default",
        dag=dag,
    )

    terminate_emr_cluster = EmrTerminateJobFlowOperator(
        task_id="terminate_emr_cluster",
        job_flow_id="{{ task_instance.xcom_pull(task_ids='create_emr_cluster', key='return_value') }}",
        aws_conn_id="aws_default",
        dag=dag
    )

    create_emr_cluster >> step_adder >> step_checker >> terminate_emr_cluster
