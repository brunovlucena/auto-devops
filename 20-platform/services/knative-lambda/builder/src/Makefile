# Makefile for Knative Lambda Builder

.PHONY: test test-unit test-integration test-coverage test-verbose clean build fmt lint help

# Default target
help: ## Show this help message
	@echo 'Usage:'
	@echo '  make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Test targets
test: test-unit ## Run all unit tests

test-unit: ## Run unit tests only
	@echo "Running unit tests..."
	go test -v ./... -short

test-integration: ## Run integration tests
	@echo "Running integration tests..."
	INTEGRATION_TESTS=true go test -v ./... -run TestIntegration

test-all: ## Run all tests including integration tests
	@echo "Running all tests..."
	INTEGRATION_TESTS=true go test -v ./...

test-coverage: ## Run tests with coverage report
	@echo "Running tests with coverage..."
	go test -v ./... -coverprofile=coverage.out -short
	go tool cover -html=coverage.out -o coverage.html
	@echo "Coverage report generated: coverage.html"

test-coverage-integration: ## Run all tests with coverage including integration tests
	@echo "Running all tests with coverage..."
	INTEGRATION_TESTS=true go test -v ./... -coverprofile=coverage.out
	go tool cover -html=coverage.out -o coverage.html
	@echo "Coverage report generated: coverage.html"

test-verbose: ## Run tests with verbose output
	@echo "Running tests verbosely..."
	go test -v ./... -short -count=1

test-race: ## Run tests with race detection
	@echo "Running tests with race detection..."
	go test -v ./... -short -race

test-bench: ## Run benchmark tests
	@echo "Running benchmark tests..."
	go test -v ./... -bench=. -benchmem -short

test-bench-integration: ## Run integration benchmark tests
	@echo "Running integration benchmark tests..."
	INTEGRATION_TESTS=true go test -v ./... -bench=BenchmarkIntegration -benchmem

# Test specific files
test-main: ## Run tests for main functionality
	go test -v -run TestBuildEvent,TestResourceEventData,TestHandleCloudEvent

test-template: ## Run template-related tests
	go test -v -run TestParseTemplate,TestProcessBuildContextTemplates,TestTemplateValidation

test-kubernetes: ## Run Kubernetes-related tests
	go test -v -run TestKubernetes,TestNamespaceValidation,TestResourceLabeling

# Build targets
build: ## Build the application
	@echo "Building application..."
	go build -o bin/knative-lambda-builder .

build-race: ## Build with race detection
	@echo "Building with race detection..."
	go build -race -o bin/knative-lambda-builder .

# Development targets
fmt: ## Format Go code
	@echo "Formatting code..."
	go fmt ./...

lint: ## Run golint
	@echo "Running golint..."
	golint ./...

vet: ## Run go vet
	@echo "Running go vet..."
	go vet ./...

check: fmt vet lint ## Run all code quality checks

# Docker targets
docker-build: ## Build Docker image
	@echo "Building Docker image..."
	docker build -t knative-lambda-builder .

docker-test: ## Run tests in Docker container
	@echo "Running tests in Docker..."
	docker run --rm knative-lambda-builder go test -v ./... -short

# Clean targets
clean: ## Clean build artifacts and test files
	@echo "Cleaning up..."
	rm -f bin/knative-lambda-builder
	rm -f coverage.out
	rm -f coverage.html
	rm -rf tmp/

clean-cache: ## Clean Go module cache
	@echo "Cleaning Go module cache..."
	go clean -modcache

# Setup targets
deps: ## Download dependencies
	@echo "Downloading dependencies..."
	go mod download

deps-update: ## Update dependencies
	@echo "Updating dependencies..."
	go mod tidy
	go mod download

# TDD workflow targets
tdd: ## Run tests in watch mode (requires entr)
	@echo "Starting TDD mode - watching for file changes..."
	find . -name "*.go" | entr -c make test-unit

tdd-integration: ## Run integration tests in watch mode
	@echo "Starting TDD mode with integration tests..."
	find . -name "*.go" | entr -c make test-integration

# Pre-commit hook target
pre-commit: check test ## Run pre-commit checks
	@echo "Pre-commit checks completed successfully!"

# CI targets
ci: deps check test-coverage ## Run CI pipeline
	@echo "CI pipeline completed!"

ci-integration: deps check test-coverage-integration ## Run CI with integration tests
	@echo "CI pipeline with integration tests completed!"

# Install development tools
install-tools: ## Install development tools
	@echo "Installing development tools..."
	go install golang.org/x/lint/golint@latest
	go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

# Generate test report
test-report: ## Generate detailed test report
	@echo "Generating test report..."
	go test -v ./... -short -json > test-report.json
	@echo "Test report generated: test-report.json"

# Run specific test patterns
test-pattern: ## Run tests matching pattern (use PATTERN=... make test-pattern)
	@echo "Running tests matching pattern: $(PATTERN)"
	go test -v ./... -run "$(PATTERN)" -short 