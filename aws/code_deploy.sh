#!/bin/bash

stack_name=AirflowCode

echo Stack name set to ${stack_name}

aws cloudformation deploy --template-file aws/code.yaml --stack-name ${stack_name} --parameter-overrides file://aws/parameters/parameters.json --capabilities CAPABILITY_IAM
