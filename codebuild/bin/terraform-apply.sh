#!/bin/bash
set -e 

cd terraform/live/${ENV}/sqs
terraform init
terraform apply -var-file=prod.tfvars -auto-approve
cd ../fargate/ftx_btc_ticker_channel
terraform init
terraform apply -var-file=prod.tfvars -auto-approve
