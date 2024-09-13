#!/bin/bash

GIT_SHA=$(git rev-parse --short HEAD)
IMG_NAME=k8sdash-${GIT_SHA}
docker build -t $IMG_NAME .
