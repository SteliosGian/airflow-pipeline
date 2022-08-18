import logging
import os
import pandas as pd
import pyspark.sql.functions as F
from pyspark.sql.types import DateType
from pyspark.sql import SparkSession


def convert_to_date(date):
    """
    Convert SAS date to pandas timestamp
    :param date: Date
    :return: Pandas date
    """
    if date is not None:
        return pd.to_timedelta(date, unit='D') + pd.Timestamp('1960-1-1')


def process_immigration_data(input_path: str, output_path: str, spark_session: SparkSession = None) -> None:
    """
    Process the immigration data
    :param spark_session: Spark session
    :param input_path: Input data path
    :param output_path: Output data path
    :return: None
    """

    if spark_session:
        spark = spark_session

    convert_to_date_udf = F.udf(convert_to_date, DateType())

    logging.info("Loading immigration data")

    df = spark.read.parquet(input_path)

    logging.info('Starting processing immigration fact table')
    df.withColumnRenamed('cicid', 'cic_id') \
        .withColumnRenamed('i94yr', 'year') \
        .withColumnRenamed('i94mon', 'month') \
        .withColumnRenamed('i94port', 'city_code') \
        .withColumnRenamed('i94addr', 'state_code') \
        .withColumnRenamed('arrdate', 'arrival_date') \
        .withColumnRenamed('depdate', 'departure_date') \
        .withColumnRenamed('i94mode', 'mode') \
        .withColumnRenamed('i94visa', 'visa') \
        .select('cic_id', 'year', 'month', 'city_code', 'state_code', 'arrival_date', 'departure_date', 'mode', 'visa') \
        .distinct() \
        .withColumn('immigration_id', F.monotonically_increasing_id()) \
        .withColumn('country', F.lit('United States')) \
        .withColumn('arrival_date', convert_to_date_udf(F.col('arrival_date'))) \
        .withColumn('departure_date', convert_to_date_udf(F.col('departure_date'))) \
        .write \
        .mode('overwrite') \
        .partitionBy('state_code') \
        .parquet(path=os.path.join(output_path, 'fact_immigration'))

    logging.info('Starting processing immigration personal dimensional table')
    df.withColumnRenamed('cicid', 'cic_id') \
        .withColumnRenamed('i94cit', 'citizen_country') \
        .withColumnRenamed('i94res', 'residence_country') \
        .withColumnRenamed('biryear', 'birth_year') \
        .withColumnRenamed('insnum', 'ins_num') \
        .withColumn('personal_id', F.monotonically_increasing_id()) \
        .select('cic_id', 'citizen_country', 'residence_country', 'birth_year', 'gender', 'ins_num') \
        .distinct() \
        .write \
        .mode('overwrite') \
        .parquet(path=os.path.join(output_path, 'dim_immigration_personal'))

    logging.info('Starting processing immigration airline dimensional table')
    df.withColumnRenamed('cicid', 'cic_id') \
        .withColumnRenamed('admnum', 'admnum') \
        .withColumnRenamed('fltno', 'flight_number') \
        .withColumnRenamed('visatype', 'visa_type') \
        .select('cic_id', 'airline', 'admnum', 'flight_number', 'visa_type') \
        .distinct()  \
        .withColumn('airline_id', F.monotonically_increasing_id()) \
        .write \
        .mode('overwrite') \
        .parquet(path=os.path.join(output_path, 'dim_immigration_airline'))


if __name__ == "__main__":
    BUCKET_NAME = 'st-proj-airflow-bucket-data-eng'
    input_path = f"s3://{BUCKET_NAME}/src/data/sas_data"
    output_path = f"s3://{BUCKET_NAME}/src/output_data/"

    spark = SparkSession.builder.appName("process_immigration").getOrCreate()
    process_immigration_data(input_path=input_path, output_path=output_path, spark_session=spark)
