#!/usr/bin/env bash
#
# Build the builder and service container images and push them to ECR.
#
# Usage:
#   ./push-to-ecr.sh  <aws-region>  <aws-account-id>  [tag] 
#
# Example:
#   ./push-to-ecr.sh  us-west-2  605322476540  v0.1.0
#
# If TAG is omitted, the current git commit SHA is used.
# Prerequisites:
#   • AWS CLI configured with credentials that can create / push to ECR
#   • Docker daemon running
#   • You are at the repo root when invoking the script
# ------------------------------------------------------------------------------

set -euo pipefail

REGION=${1:-us-west-2}
ACCOUNT_ID=${2:-$(aws sts get-caller-identity --query Account --output text)}
# TAG=${3:-$(git rev-parse --short HEAD)}
TAG="latest"

# Common ECR login function
ecr_login() {
  echo "Logging in to ECR …"
  aws ecr get-login-password --region "${REGION}" \
    | docker login --username AWS --password-stdin "${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"
}

# Function to ensure ECR repository exists
ensure_ecr_repo() {
  local repo_name=$1
  if ! aws ecr describe-repositories --repository-names "${repo_name}" --region "${REGION}" >/dev/null 2>&1; then
    echo "ECR repository ${repo_name} not found – creating it …"
    aws ecr create-repository \
      --repository-name "${repo_name}" \
      --image-scanning-configuration scanOnPush=true \
      --region "${REGION}" >/dev/null
  fi
}

# Function to build and push an image
build_and_push() {
  local image_name=$1
  local dockerfile_path=$2
  local build_context=$3
  
  local ecr_repository="knative-lambdas/${image_name}"
  local image_uri="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ecr_repository}:${TAG}"
  
  echo "Building ${image_name} ..."
  echo "Repository   : ${ecr_repository}"
  echo "Full image   : ${image_uri}"
  echo "-------------------------------------------"
  
  # Ensure the ECR repository exists
  ensure_ecr_repo "${ecr_repository}"
  
  # Build the Docker image
  echo "Building the ${image_name} image …"
  docker build \
    --platform linux/arm64 \
    -f "${dockerfile_path}" \
    -t "${image_uri}" \
    "${build_context}"
  
  # Push to ECR
  echo "Pushing ${image_name} to ECR …"
  docker push "${image_uri}"
  
  echo "✅ ${image_name} image pushed:"
  echo "   ${image_uri}"
  echo ""
}

echo "Region       : ${REGION}"
echo "Account      : ${ACCOUNT_ID}"
echo "Tag          : ${TAG}"
echo "-------------------------------------------"

# Login to ECR (once for all operations)
ecr_login

# Build and push builder image
BUILDER_NAME="knative-lambda-builder"
BUILDER_DOCKERFILE="../src/Dockerfile"
BUILDER_CONTEXT="../src"
build_and_push "${BUILDER_NAME}" "${BUILDER_DOCKERFILE}" "${BUILDER_CONTEXT}"

echo "✅ All images have been successfully built and pushed to ECR"