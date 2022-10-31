#!/bin/bash
 
 # Add bucket name
BUCKET_NAME=

set -x 
 
echo '-----------RUNNING BOOTSTRAP------------------------'
 
echo '-----------COPYING REQUIREMENTS FILE LOCALLY--------'
 
aws s3 cp s3://${BUCKET_NAME}/job_requirements.txt .
 
echo '-----------INSTALLING REQUIREMENTS------------------'
 
sudo python3 -m pip install -r job_requirements.txt
 
echo '-----------DONE BOOTSTRAP---------------------------'
