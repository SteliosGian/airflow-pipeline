import argparse
import os
import logging
import pyspark.sql.functions as F
from pyspark.sql import SparkSession


def process_demog_data(input_path: str, output_path: str, spark: SparkSession) -> None:
    """
    Process demographics data
    :param input_path: Input data path
    :param output_path: Output data path
    :return: None
    """

    logging.info('Loading demographics data')
    df = spark.read.format('csv').options(header=True, delimiter=';').load(input_path)

    logging.info('Starting processing city population dimensional table')
    df.withColumnRenamed('City', 'city') \
      .withColumnRenamed('State', 'state') \
      .withColumnRenamed('Male Population', 'male_population') \
      .withColumnRenamed('Female Population', 'female_population') \
      .withColumnRenamed('Number of Veterans', 'num_veterans') \
      .withColumnRenamed('Foreign-born', 'foreign_born') \
      .withColumnRenamed('Race', 'race') \
      .select(['city', 'state', 'male_population', 'female_population', 'num_veterans', 'foreign_born', 'race']) \
      .distinct() \
      .withColumn('population_id', F.monotonically_increasing_id()) \
      .write \
      .mode('overwrite') \
      .parquet(path=os.path.join(output_path, 'dim_city_population'))

    logging.info('Starting processing city statistics dimensional table')
    df.withColumnRenamed('City', 'city') \
      .withColumnRenamed('State', 'state') \
      .withColumnRenamed('Median Age', 'median_age') \
      .withColumnRenamed('Average Household Size', 'avg_household_size') \
      .select(['city', 'state', 'median_age', 'avg_household_size']) \
      .distinct() \
      .withColumn('stat_id', F.monotonically_increasing_id()) \
      .write \
      .mode('overwrite') \
      .parquet(path=os.path.join(output_path, 'dim_city_stats'))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process Demographics')

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

    spark = SparkSession.builder.appName("process_demographics").getOrCreate()
    process_demog_data(input_path=args.input_path,
                       output_path=args.output_path,
                       spark=spark)
