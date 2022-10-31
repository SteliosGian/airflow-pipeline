"""
Process immigration data
"""

import logging
import os
import argparse
import pandas as pd
import pyspark.sql.functions as F
from pyspark.sql.types import DateType, LongType, FloatType
from pyspark.sql import SparkSession


def convert_to_date(date):
    """
    Convert SAS date to pandas timestamp
    :param date: Date
    :return: Pandas date
    """
    if date is not None:
        return pd.to_timedelta(date, unit='D') + pd.Timestamp('1960-1-1')


def process_immigration_data(input_path: str, output_path: str, spark: SparkSession) -> None:
    """
    Process the immigration data
    :param input_path: Input data path
    :param output_path: Output data path
    :param spark: Spark session
    :return: None
    """

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
        .withColumn('state_code_partition', F.col('state_code')) \
        .withColumn('cic_id', F.col('cic_id').cast(LongType())) \
        .withColumn('year', F.col('year').cast('int')) \
        .withColumn('month', F.col('month').cast('int')) \
        .withColumn('mode', F.col('mode').cast('int')) \
        .withColumn('visa', F.col('visa').cast('int')) \
        .withColumn('immigration_id', F.col('immigration_id').cast(LongType())) \
        .write \
        .mode('overwrite') \
        .partitionBy('state_code_partition') \
        .parquet(path=os.path.join(output_path, 'fact_immigration'))

    logging.info('Starting processing immigration personal dimensional table')
    df.withColumnRenamed('cicid', 'cic_id') \
        .withColumnRenamed('i94cit', 'citizen_country') \
        .withColumnRenamed('i94res', 'residence_country') \
        .withColumnRenamed('biryear', 'birth_year') \
        .withColumnRenamed('insnum', 'ins_num') \
        .select('cic_id', 'citizen_country', 'residence_country', 'birth_year', 'gender', 'ins_num') \
        .withColumn('cic_id', F.col('cic_id').cast(LongType())) \
        .withColumn('citizen_country', F.col('citizen_country').cast('int')) \
        .withColumn('residence_country', F.col('residence_country').cast('int')) \
        .withColumn('birth_year', F.col('birth_year').cast('int')) \
        .distinct() \
        .withColumn('personal_id', F.monotonically_increasing_id()) \
        .withColumn('personal_id', F.col('personal_id').cast(LongType())) \
        .write \
        .mode('overwrite') \
        .parquet(path=os.path.join(output_path, 'dim_immigration_personal'))

    logging.info('Starting processing immigration airline dimensional table')
    df.withColumnRenamed('cicid', 'cic_id') \
        .withColumnRenamed('admnum', 'admnum') \
        .withColumnRenamed('fltno', 'flight_number') \
        .withColumnRenamed('visatype', 'visa_type') \
        .select('cic_id', 'airline', 'admnum', 'flight_number', 'visa_type') \
        .withColumn('cic_id', F.col('cic_id').cast(LongType())) \
        .withColumn('admnum', F.col('admnum').cast(FloatType())) \
        .distinct()  \
        .withColumn('airline_id', F.monotonically_increasing_id()) \
        .withColumn('airline_id', F.col('airline_id').cast(LongType())) \
        .write \
        .mode('overwrite') \
        .parquet(path=os.path.join(output_path, 'dim_immigration_airline'))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process Immigration')

    parser.add_argument(
        "--input_path",
        required=True,
        help="",
    )

    parser.add_argument(
        "--output_path",
        required=True,
        help="",
    )

    args = parser.parse_args()

    spark = SparkSession.builder.appName("process_immigration").getOrCreate()
    process_immigration_data(input_path=args.input_path, output_path=args.output_path, spark=spark)
