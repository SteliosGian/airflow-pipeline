# Airflow Pipeline

[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
      </ul>
    </li>
    <li><a href="#roadmap">Roadmap</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

This project creates data pipelines using Airflow both locally and on AWS.  

### Local

The Airflow pipeline runs in parallel all the spark jobs that are defined in the "src/jobs" directory.

### AWS

To create the AWS environment, run the ".sh" scripts inside the aws directory. These scripts will create 4 different stacks that are needed for Airflow.  

Script "cicd_deploy.sh" creates the CI/CD part of the project. For this, AWS Codepipeline is used that sources from AWS Codecommit and deployes on S3. There is also an event rule that triggers the pipeline every time there's a commit.  

Script "code_deploy.sh" creates the AWS Codecommit repository to store the code.  

Script "data_deploy.sh" creates the S3 bucket with versioning and with all public access blocked.  

Finally, script "template_deploy.sh" creates the core services such as Airflow, Redshift, and different networking services that are needed such as VPC.  

Once all the stacks are deployed successfully, a managed Airflow environment will be created on AWS. Open the Airflow UI and run the dag. By running the dag, an EMR cluster will be created to run the jobs.

### Built With

* [Docker](https://www.docker.com/)
* [Airflow](https://airflow.apache.org/)
* [Pipenv](https://pipenv-fork.readthedocs.io/en/latest/)
* [Spark](https://spark.apache.org/)
* [AWS CloudFormation](https://aws.amazon.com/cloudformation/)
* [AWS EMR](https://aws.amazon.com/emr/)
* [AWS Redshift](https://aws.amazon.com/redshift/)


### Datasets

#### I94 Immigration

The I94 Immigration dataset contains statistics regarding the international visitor arrivals split by world regions and countries, type of visa, mode of transportation, age groups, states visited, and the ports of entry.  
The dataset can be found <a href="https://www.trade.gov/national-travel-and-tourism-office" target="_blank">here</a>.  
The dataset files in the repo can be found inside the "src/data/sas_data/" directory.

#### World Temperature

The World Temperature dataset contains data regarding the monthly average temperature by country. This dataset is taken from <a href="https://www.kaggle.com/berkeleyearth/climate-change-earth-surface-temperature-data" target="_blank">Kaggle</a>.  
This data has to be downloaded and placed inside the "src/data/ directory.

#### U.S. City Demographic

The U.S. City Demographic dataset contains demographic information of US cities and census-designated places with a population greater or equal to 65,000.  
More about the dataset can be found here <a href="https://public.opendatasoft.com/explore/dataset/us-cities-demographics/export/" target="_blank">here</a>.  
The dataset in the repo can be found at "src/data/us-cities-demographics.csv".

#### Airport Code

A simple table of Airport codes and corresponding cities. More about the dataset can be found <a href="https://datahub.io/core/airport-codes#data" target="_blank">here</a>.  
The dataset in the repo can be found at: "src/data/I94_SAS_Labels_Descriptions.SAS".


## Getting Started

### Local

To start Airflow locally, run:

```Bash
bash run-local.sh
```

The Airflow UI can be accessed from localhost:8080.

To delete all created containers, run:

```Bash
docker-compose down --volumes --rmi all
```

### AWS

The AWS part of this project is split in 2 parts.  

1) AWS CloudFormation stacks  
The services are created using AWS's Cloudformation. There are 4 templates available that create the necessary tables. The first 3 are related to repositories and services that do not cost a lot and can remain active. The "template.yaml" contains the core services that should be deleted when experimentation is over.  
2) Airflow  
The Airflow Dag for AWS can be found at "src/aws_dags/". This directory contains the main dag as well as the helper function that contain configurations and the SQL scripts required for Redshift.  

Some mandatory steps are needed to run it on AWS.  
1) Fill the **"S3BucketName"** and **"RedshiftMasterUserPassword"** inside the "aws/parameters/parameters.json" file.  
The **"S3BucketName"** is the unique bucket name that will be created and the **"RedshiftMasterUserPassword"** is the Redshift database password.
2) Fill the **"IAM_REDSHIFT_ROLE"** and **"BUCKET_NAME"** inside the "src/aws_dags/helpers/conf.py" file.  
The **"IAM_REDSHIFT_ROLE"** is the IAM role ARN required to access Redshift. This can be found using the AWS console and accessing IAM Roles. The name should be in the format "arn:aws:iam\<AccountNumber>:role/AirflowTemplate-AirflowRole-\<id>".
The  **"BUCKET_NAME"** is the Bucket name used in **"S3BucketName"**.  
3) Fill the **"BUCKET_NAME"** inside the "bootstrap.sh" file.
4) When the template.yaml has been deployed. Go to the Airflow UI at Admin -> Connections. Create a new connection by pressing the "+" button on the upper left.  
Add the following values:  

* Connection Id: redshift_default
* Connection Type: Amazon Redshift
* Host: The "Endpoint" value taken from the Redshift page in AWS console without the port and schema. Has the following format: \<clusterIdentifier>.\<id>.\<region>.redshift.amazonaws.com.  
* Schema: The database name. Should be the same as the **RedshiftDBName** value in "aws/parameters/parameters.json".  
* Login: The Admin user name. The default used is "master".  
Can also be found inside the Redshift page in AWS console at Properties -> Database configurations -> Admin user name.  
* Password: The database password. Should be the same as the **"RedshiftMasterUserPassword"** value in "aws/parameters/parameters.json".  
* Port: Database port. The default is 5439. Can also be found inside the Redshift page in AWS console at Properties -> Database configurations -> Port.  

To remove the created services, just delete the stack from the CloudFormation page on the AWS console.

### Prerequisites

Docker must be installed to run the docker files.
AWS cli must be installed to run the AWS scripts.


## Roadmap

<ul>
  <li>Set local Airflow &#9745; </li>
  <li>Install PySpark in Airflow image &#9745; </li>
  <li>Create local Airflow jobs &#9745; </li>
  <li>Create Airflow environment on AWS &#9745; </li>
  <li>Create Airflow Pyspark jobs on AWS EMR &#9745; </li>
  <li>Save EMR results on AWS Redshift &#9745; </li>
</ul>

[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-white.svg?
[linkedin-url]: https://linkedin.com/in/stelios-giannikis
