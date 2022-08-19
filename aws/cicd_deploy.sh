#!/bin/bash

stack_name=AirflowCICD

echo Stack name set to ${stack_name}

aws cloudformation deploy --template-file aws/cicd.yaml --stack-name ${stack_name} --parameter-overrides file://aws/parameters/parameters.json --capabilities CAPABILITY_IAM
