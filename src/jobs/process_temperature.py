import os
import argparse
import logging
import pyspark.sql.functions as F
from pyspark.sql import SparkSession


def process_temp_data(input_path: str, output_path: str, spark: SparkSession) -> None:
    """
    Process the temperature data
    :param spark_session: Spark session
    :param input_path: Input data path
    :param output_path: Output data path
    :return: None
    """

    logging.info('Loading temperature data')
    df = spark.read.format('csv').options(header=True).load(input_path)

    logging.info('Starting processing temperature dimensional table')
    df.where(df['Country'] == 'United States') \
      .withColumnRenamed('AverageTemperature', 'avg_temperature') \
      .withColumnRenamed('AverageTemperatureUncertainty', 'avg_temperature_uncertainty') \
      .withColumnRenamed('City', 'city') \
      .withColumnRenamed('Country', 'country') \
      .select(['dt', 'avg_temperature', 'avg_temperature_uncertainty', 'city', 'country']) \
      .distinct() \
      .withColumn('dt', F.to_date(F.col('dt'))) \
      .withColumn('year', F.year(F.col('dt'))) \
      .withColumn('month', F.month(F.col('dt'))) \
      .write \
      .mode('overwrite') \
      .parquet(path=os.path.join(output_path, 'dim_immmigration_temperature'))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process Temperature')

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

    spark = SparkSession.builder.appName("process_temperature").getOrCreate()
    process_temp_data(input_path=args.input_path, output_path=args.output_path, spark=spark)
