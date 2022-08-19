#!/bin/bash

stack_name=AirflowTemplate

echo Stack name set to ${stack_name}

aws cloudformation deploy --template-file aws/template.yaml --stack-name ${stack_name} --parameter-overrides file://aws/parameters/parameters.json --capabilities CAPABILITY_IAM
