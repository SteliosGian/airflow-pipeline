import os
import logging
from pyspark.sql import SparkSession


def process_label_descriptions(input_path: str, output_path: str, spark_session: SparkSession = None) -> None:
    """
    Process the label descriptions
    :param input_path: Input data path
    :param output_path: Output data path
    :return: None
    """

    if spark_session:
        spark = spark_session

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
