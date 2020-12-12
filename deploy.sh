#!/usr/bin/env sh

ARTIFACTS_BUCKET="galudy-visual-search-artifacts"
S3_WORKFLOW_PREFIX="aws-codeguru-reviewer-automation"
WORKFLOW_STACK_NAME="aws-codeguru-reviewer-automation-wf"

mkdir -p deploy
sam build -b deploy/

sam package --template-file deploy/template.yaml \
  --output-template-file packaged.template.yaml \
  --s3-bucket ${ARTIFACTS_BUCKET} \
  --s3-prefix ${S3_WORKFLOW_PREFIX}

sam deploy --stack-name ${WORKFLOW_STACK_NAME} \
  --template-file packaged.template.yaml \
  --parameter-overrides AssociatedRepositoryName="sagemaker-autopilot-step-functions" TeamEmail="elesin.olalekan@gmail.com" \
  --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND \
  --no-fail-on-empty-changeset

rm -rf deploy/ packaged.template.yaml
