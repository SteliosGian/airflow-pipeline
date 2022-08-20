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
        <li><a href="#notes">Notes</a></li>
      </ul>
    </li>
    <li><a href="#roadmap">Roadmap</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

This project creates data pipelines using Airflow both locally and on AWS.  

### Local

The Airflow pipeline runs in parallel all the spark jobs that are defined in the src/jobs directory.

### AWS

To create the AWS environment, run the scripts inside the aws directory. These scripts will create 4 different stacks that are needed for Airflow.  
Script cicd_deploy.sh creates the CICD part of the project. For this, AWS Codepipeline is used that sources from AWS Codecommit and deployes on S3. There is also an event rule that triggers the pipeline every time there's a commit.  
Script code_deploy.sh creates the AWS Codecommit repository to store the code.
Script data_deploy.sh creates the S3 bucket with versioning and with all public access blocked.
Finally, script template_deploy.sh creates the core services such as Airflow and different networking services that are needed such as VPN.  

Once all the stacks are deployed successfully, a managed Airflow environment will be created on AWS. Open the Airflow UI and run the dag. By running the dag, an EMR cluster will be created to run the jobs.

### Built With

* [Docker](https://www.docker.com/)
* [Airflow](https://airflow.apache.org/)
* [Pipenv](https://pipenv-fork.readthedocs.io/en/latest/)
* [Spark](https://spark.apache.org/)
* [AWS CloudFormation](https://aws.amazon.com/cloudformation/)
* [AWS EMR](https://aws.amazon.com/emr/)


## Getting Started

To start Airflow locally, run:

```Bash
bash run-local.sh
```

The Airflow UI can be accessed from localhost:8080.

To delete all created containers, run:

```Bash
docker-compose down --volumes --rmi all
```

### Prerequisites

Docker must in installed to run the docker files.

### Notes


## Roadmap

<ul>
  <li>Set local Airflow &#9745; </li>
  <li>Install PySpark in Airflow image &#9745; </li>
  <li>Create local Airflow jobs &#9745; </li>
  <li>Create Airflow environment on AWS &#9745; </li>
  <li>Create Airflow Pyspark jobs on AWS EMR &#9745; </li>
  <li>Save EMR results on AWS Redshift </li>
</ul>

[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-white.svg?
[linkedin-url]: https://linkedin.com/in/stelios-giannikis
