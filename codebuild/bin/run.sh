#!/bin/bash

#!/bin/bash

HOME_DIR=$PWD
BUILD=$1
ENV=$2
VERSION=$3

if [[ "$BUILD" == "ci" ]] 
then
    aws codebuild start-build \
        --project-name=plutus-ci \
        --region us-west-1
elif [[ "$BUILD" == "cd" ]] 
then
    aws codebuild start-build \
        --project-name=plutus-cd \
        --region us-west-1 \
        --environment-variables-override \
                name=VERSION,value=${PROJECT_VERSION},type=PLAINTEXT \
                name=ENV,value=${ENV},type=PLAINTEXT
fi