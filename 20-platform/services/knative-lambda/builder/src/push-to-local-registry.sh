#!/usr/bin/env bash
#
# Build the builder and service container images and push them to local registry.
#
# Usage:
#   ./push-to-local-registry.sh  [tag] 
#
# Example:
#   ./push-to-local-registry.sh  v0.1.0
#
# If TAG is omitted, "latest" is used.
# Prerequisites:
#   • Docker daemon running
#   • Local registry running at localhost:5001 (accessible as kind-registry:5000 from cluster)
#   • You are at the repo root when invoking the script
# ------------------------------------------------------------------------------

set -euo pipefail

TAG=${1:-latest}
LOCAL_REGISTRY="localhost:5001"

# Function to build and push an image
build_and_push() {
  local image_name=$1
  local dockerfile_path=$2
  local build_context=$3
  
  local repository="knative-lambdas/${image_name}"
  local image_uri="${LOCAL_REGISTRY}/${repository}:${TAG}"
  
  echo "Building ${image_name} ..."
  echo "Repository   : ${repository}"
  echo "Full image   : ${image_uri}"
  echo "-------------------------------------------"
  
  # Build the Docker image
  echo "Building the ${image_name} image …"
  docker build \
    --platform linux/arm64 \
    -f "${dockerfile_path}" \
    -t "${image_uri}" \
    "${build_context}"
  
  # Push to local registry
  echo "Pushing ${image_name} to local registry …"
  docker push "${image_uri}"
  
  echo "✅ ${image_name} image pushed:"
  echo "   ${image_uri}"
  echo ""
}

echo "Local Registry: ${LOCAL_REGISTRY}"
echo "Tag           : ${TAG}"
echo "-------------------------------------------"

# Build and push builder image
BUILDER_NAME="knative-lambda-builder"
BUILDER_DOCKERFILE="../src/Dockerfile"
BUILDER_CONTEXT="../src"
build_and_push "${BUILDER_NAME}" "${BUILDER_DOCKERFILE}" "${BUILDER_CONTEXT}"

echo "✅ All images have been successfully built and pushed to local registry"