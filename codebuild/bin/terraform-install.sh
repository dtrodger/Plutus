#!/bin/bash

set -e

eval $(ssh-agent)
echo "SSH_AUTH_SOCK ${SSH_AUTH_SOCK}"
cd /tmp
echo "Installing Terraform"
curl -o terraform_1.0.6_linux_amd64.zip https://releases.hashicorp.com/terraform/1.0.6/terraform_1.0.6_linux_amd64.zip
unzip -o terraform_1.0.6_linux_amd64.zip && mv terraform /usr/bin
terraform --version
cd -