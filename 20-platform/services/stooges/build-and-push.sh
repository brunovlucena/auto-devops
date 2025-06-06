#!/bin/bash

# Script to build and push all 3 stooges services to GitHub Container Registry
# Usage: ./build-and-push.sh [tag]
# If no tag is provided, 'latest' will be used

set -e  # Exit on any error

# Configuration
GITHUB_USERNAME="brunovlucena"
REGISTRY="ghcr.io"
TAG=${1:-latest}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to build and push a service
build_and_push_service() {
    local service_name=$1
    local service_dir=$2
    
    print_status "Building and pushing $service_name service..."
    
    # Navigate to service directory
    cd "$service_dir"
    
    # Build the Docker image
    print_status "Building Docker image for $service_name..."
    docker build -t "${REGISTRY}/${GITHUB_USERNAME}/${service_name}-service:${TAG}" .
    
    if [ $? -eq 0 ]; then
        print_success "Successfully built ${service_name}-service:${TAG}"
    else
        print_error "Failed to build ${service_name}-service"
        return 1
    fi
    
    # Push the Docker image
    print_status "Pushing Docker image for $service_name..."
    docker push "${REGISTRY}/${GITHUB_USERNAME}/${service_name}-service:${TAG}"
    
    if [ $? -eq 0 ]; then
        print_success "Successfully pushed ${service_name}-service:${TAG}"
    else
        print_error "Failed to push ${service_name}-service"
        return 1
    fi
    
    # Return to original directory
    cd - > /dev/null
}

# Main script
print_status "Starting build and push process for the 3 stooges services..."
print_status "Using tag: $TAG"
print_status "Registry: $REGISTRY/$GITHUB_USERNAME"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if user is logged into GitHub Container Registry
print_status "Checking GitHub Container Registry authentication..."
if ! echo "test" | docker login ghcr.io -u "$GITHUB_USERNAME" --password-stdin > /dev/null 2>&1; then
    print_warning "You need to authenticate with GitHub Container Registry."
    print_warning "Please run the following command with your GitHub Personal Access Token:"
    print_warning "echo \$CR_PAT | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin"
    print_warning "Where CR_PAT is your GitHub Personal Access Token with packages:write scope"
    print_error "Authentication required. Please login and try again."
    exit 1
fi

# Store the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Array of services and their directories
declare -a services=("larry" "moe" "curly")

# Build and push each service
for service in "${services[@]}"; do
    service_dir="${SCRIPT_DIR}/${service}"
    
    if [ -d "$service_dir" ] && [ -f "$service_dir/Dockerfile" ]; then
        build_and_push_service "$service" "$service_dir"
        echo ""  # Add spacing between services
    else
        print_error "Service directory $service_dir not found or missing Dockerfile"
        exit 1
    fi
done

print_success "All 3 stooges services have been built and pushed successfully!"
print_status "Images pushed:"
for service in "${services[@]}"; do
    echo "  - ${REGISTRY}/${GITHUB_USERNAME}/${service}-service:${TAG}"
done

print_status "You can now update your Helm values.yaml files to reference these images." 