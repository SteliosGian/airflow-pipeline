#!/bin/bash

stack_name=AirflowData

echo Stack name set to ${stack_name}

aws cloudformation deploy --template-file aws/data.yaml --stack-name ${stack_name} --parameter-overrides file://aws/parameters/parameters.json --capabilities CAPABILITY_IAM
