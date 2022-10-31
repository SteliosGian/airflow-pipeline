from helpers import create_tables, copy_tables, conf
from airflow import DAG
from airflow.contrib.operators.emr_create_job_flow_operator import EmrCreateJobFlowOperator
from airflow.contrib.operators.emr_add_steps_operator import EmrAddStepsOperator
from airflow.contrib.sensors.emr_step_sensor import EmrStepSensor
from airflow.contrib.operators.emr_terminate_job_flow_operator import EmrTerminateJobFlowOperator
from airflow.providers.amazon.aws.operators.redshift import RedshiftSQLOperator
from datetime import datetime

BUCKET_NAME = conf.BUCKET_NAME
PROCESS_IMMIGRATION = 'src/jobs/process_immigration.py'
PROCESS_DEMOGRAPHICS = 'src/jobs/process_demographics.py'
PROCESS_LABEL = 'src/jobs/process_label.py'
PROCESS_TEMPERATURE = 'src/jobs/process_temperature.py'
AIFRLOW_ROLE = conf.IAM_REDSHIFT_ROLE

JOB_FLOW_OVERRIDES = {
    "Name": "Data Processing",
    "ReleaseLabel": "emr-5.36.0",
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
        "KeepJobFlowAliveWhenNoSteps": False,
        "TerminationProtected": False,  # this lets us programmatically terminate the cluster
    },
    "JobFlowRole": "EMR_EC2_DefaultRole",
    "ServiceRole": "EMR_DefaultRole",
    "LogUri": f"s3://{BUCKET_NAME}/emr_logs/",
    "BootstrapActions": [
        {
            "Name": "string",
            "ScriptBootstrapAction": {
                "Path": f"s3://{BUCKET_NAME}/bootstrap.sh"
            }
        }
    ]
}

SPARK_STEP_IMMIGRATION_DATA = [
    {
        "Name": "Process immigration data",
        "ActionOnFailure": "CONTINUE",
        "HadoopJarStep": {
            "Jar": "command-runner.jar",
            "Args": [
                "spark-submit",
                "--deploy-mode",
                "client",
                "s3://{{ params.BUCKET_NAME }}/{{ params.process_immigration }}",
                "--input_path",
                "{{ params.input_path }}",
                "--output_path",
                "{{ params.output_path }}"
            ],
        }
    }
]

SPARK_STEP_DEMOGRAPHICS_DATA = [
    {
        "Name": "Process demographics data",
        "ActionOnFailure": "CONTINUE",
        "HadoopJarStep": {
            "Jar": "command-runner.jar",
            "Args": [
                "spark-submit",
                "--deploy-mode",
                "client",
                "s3://{{ params.BUCKET_NAME }}/{{ params.process_demographics }}",
                "--input_path",
                "{{ params.input_path }}",
                "--output_path",
                "{{ params.output_path }}"
            ],
        }
    }
]

SPARK_STEP_LABEL_DATA = [
    {
        "Name": "Process label data",
        "ActionOnFailure": "CONTINUE",
        "HadoopJarStep": {
            "Jar": "command-runner.jar",
            "Args": [
                "spark-submit",
                "--deploy-mode",
                "client",
                "s3://{{ params.BUCKET_NAME }}/{{ params.process_label }}",
                "--input_path",
                "{{ params.input_path }}",
                "--output_path",
                "{{ params.output_path }}",
                "--bucket_name",
                "{{ params.bucket_name }}"
            ],
        }
    }
]

SPARK_STEP_TEMPERATURE_DATA = [
    {
        "Name": "Process temperature data",
        "ActionOnFailure": "CONTINUE",
        "HadoopJarStep": {
            "Jar": "command-runner.jar",
            "Args": [
                "spark-submit",
                "--deploy-mode",
                "client",
                "s3://{{ params.BUCKET_NAME }}/{{ params.process_temperature }}",
                "--input_path",
                "{{ params.input_path }}",
                "--output_path",
                "{{ params.output_path }}"
            ],
        }
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

    add_immigration_step = EmrAddStepsOperator(
        task_id="process_immigration",
        job_flow_id="{{ task_instance.xcom_pull(task_ids='create_emr_cluster', key='return_value') }}",
        aws_conn_id="aws_default",
        steps=SPARK_STEP_IMMIGRATION_DATA,
        params={
            "BUCKET_NAME": BUCKET_NAME,
            "process_immigration": PROCESS_IMMIGRATION,
            "input_path": f"s3://{BUCKET_NAME}/src/data/sas_data",
            "output_path": f"s3://{BUCKET_NAME}/src/output_data/"
        },
        dag=dag
    )

    add_demographics_step = EmrAddStepsOperator(
        task_id="process_demographics",
        job_flow_id="{{ task_instance.xcom_pull(task_ids='create_emr_cluster', key='return_value') }}",
        aws_conn_id="aws_default",
        steps=SPARK_STEP_DEMOGRAPHICS_DATA,
        params={
            "BUCKET_NAME": BUCKET_NAME,
            "process_demographics": PROCESS_DEMOGRAPHICS,
            "input_path": f"s3://{BUCKET_NAME}/src/data/us-cities-demographics.csv",
            "output_path": f"s3://{BUCKET_NAME}/src/output_data/"
        },
        dag=dag
    )

    add_label_step = EmrAddStepsOperator(
        task_id="process_label",
        job_flow_id="{{ task_instance.xcom_pull(task_ids='create_emr_cluster', key='return_value') }}",
        aws_conn_id="aws_default",
        steps=SPARK_STEP_LABEL_DATA,
        params={
            "BUCKET_NAME": BUCKET_NAME,
            "process_label": PROCESS_LABEL,
            "input_path": f"s3://{BUCKET_NAME}/src/data/I94_SAS_Labels_Descriptions.SAS",
            "output_path": f"s3://{BUCKET_NAME}/src/output_data/",
            "bucket_name": BUCKET_NAME
        },
        dag=dag
    )

    add_temperature_step = EmrAddStepsOperator(
        task_id="process_temperature",
        job_flow_id="{{ task_instance.xcom_pull(task_ids='create_emr_cluster', key='return_value') }}",
        aws_conn_id="aws_default",
        steps=SPARK_STEP_TEMPERATURE_DATA,
        params={
            "BUCKET_NAME": BUCKET_NAME,
            "process_temperature": PROCESS_TEMPERATURE,
            "input_path": f"s3://{BUCKET_NAME}/src/data/GlobalLandTemperaturesByCity.csv",
            "output_path": f"s3://{BUCKET_NAME}/src/output_data/"
        },
        dag=dag
    )

    check_immigration = EmrStepSensor(
        task_id="watch_immigration",
        job_flow_id="{{ task_instance.xcom_pull('create_emr_cluster', key='return_value') }}",
        step_id="{{ task_instance.xcom_pull(task_ids='process_immigration', key='return_value')[0] }}",
        aws_conn_id="aws_default",
        dag=dag,
    )
    check_demographics = EmrStepSensor(
        task_id="watch_demographics",
        job_flow_id="{{ task_instance.xcom_pull('create_emr_cluster', key='return_value') }}",
        step_id="{{ task_instance.xcom_pull(task_ids='process_demographics', key='return_value')[0] }}",
        aws_conn_id="aws_default",
        dag=dag,
    )
    check_label = EmrStepSensor(
        task_id="watch_label",
        job_flow_id="{{ task_instance.xcom_pull('create_emr_cluster', key='return_value') }}",
        step_id="{{ task_instance.xcom_pull(task_ids='process_label', key='return_value')[0] }}",
        aws_conn_id="aws_default",
        dag=dag,
    )
    check_temperature = EmrStepSensor(
        task_id="watch_temperature",
        job_flow_id="{{ task_instance.xcom_pull('create_emr_cluster', key='return_value') }}",
        step_id="{{ task_instance.xcom_pull(task_ids='process_temperature', key='return_value')[0] }}",
        aws_conn_id="aws_default",
        dag=dag,
    )

    terminate_emr_cluster = EmrTerminateJobFlowOperator(
        task_id="terminate_emr_cluster",
        job_flow_id="{{ task_instance.xcom_pull(task_ids='create_emr_cluster', key='return_value') }}",
        aws_conn_id="aws_default",
        dag=dag
    )

    create_tables_dim_city_population = RedshiftSQLOperator(
        task_id='create_tables_dim_city_population',
        redshift_conn_id='redshift_default',
        sql=create_tables.CREATE_DIM_CITY_POPULATION
    )

    create_tables_dim_city_stats = RedshiftSQLOperator(
        task_id='create_tables_dim_city_stats',
        redshift_conn_id='redshift_default',
        sql=create_tables.CREATE_DIM_CITY_STATS
    )

    create_tables_fact_immigration = RedshiftSQLOperator(
        task_id='create_tables_fact_immigration',
        redshift_conn_id='redshift_default',
        sql=create_tables.CREATE_FACT_IMMIGRATION
    )

    create_tables_dim_immigration_personal = RedshiftSQLOperator(
        task_id='create_tables_dim_immigration_personal',
        redshift_conn_id='redshift_default',
        sql=create_tables.CREATE_DIM_IMMIGRATION_PERSONAL
    )

    create_tables_dim_immigration_airline = RedshiftSQLOperator(
        task_id='create_tables_dim_immigration_airline',
        redshift_conn_id='redshift_default',
        sql=create_tables.CREATE_DIM_IMMIGRATION_AIRLINE
    )

    create_tables_country_code = RedshiftSQLOperator(
        task_id='create_tables_country_code',
        redshift_conn_id='redshift_default',
        sql=create_tables.CREATE_COUNTRY_CODE
    )

    create_tables_city_code = RedshiftSQLOperator(
        task_id='create_tables_city_code',
        redshift_conn_id='redshift_default',
        sql=create_tables.CREATE_CITY_CODE
    )

    create_tables_state_code = RedshiftSQLOperator(
        task_id='create_tables_state_code',
        redshift_conn_id='redshift_default',
        sql=create_tables.CREATE_STATE_CODE
    )

    create_tables_dim_immigration_temperature = RedshiftSQLOperator(
        task_id='create_tables_dim_immigration_temperature',
        redshift_conn_id='redshift_default',
        sql=create_tables.CREATE_DIM_IMMIGRATION_TEMPERATURE
    )

    insert_dim_city_population = RedshiftSQLOperator(
        task_id='insert_dim_city_population',
        redshift_conn_id='redshift_default',
        sql=copy_tables.LOAD_DIM_CITY_POPULATION,
        params={
                'location': f"s3://{BUCKET_NAME}/src/output_data/dim_city_population/",
                'iam_role': AIFRLOW_ROLE
        }
    )

    insert_dim_city_stats = RedshiftSQLOperator(
        task_id='insert_dim_city_stats',
        redshift_conn_id='redshift_default',
        sql=copy_tables.LOAD_DIM_CITY_STATS,
        params={
                'location': f"s3://{BUCKET_NAME}/src/output_data/dim_city_stats/",
                'iam_role': AIFRLOW_ROLE
        }
    )

    insert_fact_immigration = RedshiftSQLOperator(
        task_id='insert_fact_immigration',
        redshift_conn_id='redshift_default',
        sql=copy_tables.LOAD_FACT_IMMIGRATION,
        params={
                'location': f"s3://{BUCKET_NAME}/src/output_data/fact_immigration/",
                'iam_role': AIFRLOW_ROLE
        }
    )

    insert_dim_immigration_personal = RedshiftSQLOperator(
        task_id='insert_dim_immigration_personal',
        redshift_conn_id='redshift_default',
        sql=copy_tables.LOAD_DIM_IMMIGRATION_PERSONAL,
        params={
                'location': f"s3://{BUCKET_NAME}/src/output_data/dim_immigration_personal/",
                'iam_role': AIFRLOW_ROLE
        }
    )

    insert_dim_immigration_airline = RedshiftSQLOperator(
        task_id='insert_dim_immigration_airline',
        redshift_conn_id='redshift_default',
        sql=copy_tables.LOAD_DIM_IMMIGRATION_AIRLINE,
        params={
                'location': f"s3://{BUCKET_NAME}/src/output_data/dim_immigration_airline/",
                'iam_role': AIFRLOW_ROLE
        }
    )

    insert_country_code = RedshiftSQLOperator(
        task_id='insert_country_code',
        redshift_conn_id='redshift_default',
        sql=copy_tables.LOAD_COUNTRY_CODE,
        params={
                'location': f"s3://{BUCKET_NAME}/src/output_data/country_code/",
                'iam_role': AIFRLOW_ROLE
        }
    )

    insert_city_code = RedshiftSQLOperator(
        task_id='insert_city_code',
        redshift_conn_id='redshift_default',
        sql=copy_tables.LOAD_CITY_CODE,
        params={
                'location': f"s3://{BUCKET_NAME}/src/output_data/city_code/",
                'iam_role': AIFRLOW_ROLE
        }
    )

    insert_state_code = RedshiftSQLOperator(
        task_id='insert_state_code',
        redshift_conn_id='redshift_default',
        sql=copy_tables.LOAD_STATE_CODE,
        params={
                'location': f"s3://{BUCKET_NAME}/src/output_data/state_code/",
                'iam_role': AIFRLOW_ROLE
        }
    )

    insert_dim_immigration_temperature = RedshiftSQLOperator(
        task_id='insert_dim_immigration_temperature',
        redshift_conn_id='redshift_default',
        sql=copy_tables.LOAD_DIM_IMMIGRATION_TEMPERATURE,
        params={
                'location': f"s3://{BUCKET_NAME}/src/output_data/dim_immigration_temperature/",
                'iam_role': AIFRLOW_ROLE
        }
    )

    create_emr_cluster >> [add_immigration_step, add_demographics_step, add_label_step, add_temperature_step]
    add_immigration_step >> check_immigration
    add_demographics_step >> check_demographics
    add_label_step >> check_label
    add_temperature_step >> check_temperature
    [check_immigration, check_demographics, check_label, check_temperature] >> terminate_emr_cluster
    terminate_emr_cluster >> [create_tables_dim_city_population, create_tables_dim_city_stats,
                              create_tables_fact_immigration, create_tables_dim_immigration_personal,
                              create_tables_dim_immigration_airline, create_tables_country_code, create_tables_city_code,
                              create_tables_state_code, create_tables_dim_immigration_temperature]
    create_tables_dim_city_population >> insert_dim_city_population
    create_tables_dim_city_stats >> insert_dim_city_stats
    create_tables_fact_immigration >> insert_fact_immigration
    create_tables_dim_immigration_personal >> insert_dim_immigration_personal
    create_tables_dim_immigration_airline >> insert_dim_immigration_airline
    create_tables_country_code >> insert_country_code
    create_tables_city_code >> insert_city_code
    create_tables_state_code >> insert_state_code
    create_tables_dim_immigration_temperature >> insert_dim_immigration_temperature
