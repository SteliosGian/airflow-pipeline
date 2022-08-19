import os
import argparse
import logging
import boto3
from pyspark.sql import SparkSession


def process_label_descriptions(input_path: str, output_path: str, spark: SparkSession, bucket: str = None) -> None:
    """
    Process the label descriptions
    :param input_path: Input data path
    :param output_path: Output data path
    :param spark_session: The spark session
    :param bucket: S3 bucket
    :return: None
    """

    if input_path.startswith('s3'):
        logging.info('Loading labels descriptions file from S3')
        s3_client = boto3.client('s3')
        target_file_path = '/'.join(input_path.split('/')[3:])
        local_file_path = input_path.split('/')[-1]
        s3_client.download_file(bucket, target_file_path, local_file_path)
        with open(local_file_path) as file:
            file_contents = file.readlines()
    else:
        logging.info('Loading labels descriptions file')
        with open(input_path) as file:
            file_contents = file.readlines()

    logging.info('Creating country code')
    country_code = {}
    for line in file_contents[10:298]:
        split = line.split('=')
        code, country = split[0].strip(), split[1].strip().strip("'")
        country_code[code] = country
    spark.createDataFrame(country_code.items(), ['code', 'country']) \
         .write \
         .mode('overwrite') \
         .parquet(path=os.path.join(output_path, 'country_code'))

    logging.info('Creating city code')
    city_code = {}
    for line in file_contents[303:962]:
        split = line.split('=')
        code, city = split[0].strip("\t").strip().strip("'"), split[1].strip('\t').strip().strip("''")
        city_code[code] = city
    spark.createDataFrame(city_code.items(), ['code', 'city']) \
         .write \
         .mode('overwrite') \
         .parquet(path=os.path.join(output_path, 'city_code'))

    logging.info('Creating state code')
    state_code = {}
    for line in file_contents[982:1036]:
        split = line.split('=')
        code, state = split[0].strip('\t').strip("'"), split[1].strip().strip("'")
        state_code[code] = state
    spark.createDataFrame(state_code.items(), ['code', 'state']) \
         .write \
         .mode('overwrite') \
         .parquet(path=os.path.join(output_path, 'state_code'))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process Label')

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

    parser.add_argument(
        "--bucket_name",
        required=True,
        help="",
    )

    args = parser.parse_args()

    spark = SparkSession.builder \
                        .config("spark.jars.repositories", "https://repos.spark-packages.org/") \
                        .config("spark.jars.packages", "saurfang:spark-sas7bdat:2.0.0-s_2.11") \
                        .enableHiveSupport() \
                        .appName("process_label") \
                        .getOrCreate()
    process_label_descriptions(input_path=args.input_path, output_path=args.output_path, spark=spark, bucket=args.bucket_name)
