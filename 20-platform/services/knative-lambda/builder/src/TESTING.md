# Testing Documentation

This document describes the comprehensive test suite for the Knative Lambda Builder, following Test-Driven Development (TDD) principles.

## Test Structure

The test suite is organized into multiple files, each covering different aspects of the application:

### Test Files

Note: *REVIEW TESTS*

1. **`main_test.go`** - Core functionality tests
   - BuildEvent struct validation
   - ResourceEventData and IsJobComplete method
   - CloudEvent handling
   - Template data structures
   - Constants validation
   - Environment configuration

2. **`template_test.go`** - Template processing tests
   - Template parsing and validation
   - Build context template processing
   - Template error handling
   - Template data function validation

3. **`kubernetes_test.go`** - Kubernetes operations tests
   - Kubernetes configuration
   - Resource application and creation
   - Namespace validation
   - Resource labeling
   - Job and Service template validation

4. **`integration_test.go`** - End-to-end integration tests
   - Complete build flow testing
   - Template processing workflow
   - Error handling scenarios
   - Concurrent event handling
   - Environment configuration testing

## Running Tests

### Quick Start

```bash
# Run all unit tests
make test

# Run with coverage
make test-coverage

# Run integration tests
make test-integration

# Run all tests including integration
make test-all
```

### Test Categories

#### Unit Tests
Unit tests focus on individual functions and methods:

```bash
# Run only unit tests (default)
go test -v ./... -short

# Run specific test categories
make test-main      # Core functionality tests
make test-template  # Template-related tests  
make test-kubernetes # Kubernetes-related tests
```

#### Integration Tests
Integration tests require the `INTEGRATION_TESTS=true` environment variable:

```bash
# Enable integration tests
export INTEGRATION_TESTS=true
go test -v ./...

# Or use the Makefile
make test-integration
```

#### Benchmark Tests
Performance benchmarks are included for critical paths:

```bash
# Run benchmarks
make test-bench

# Run integration benchmarks
make test-bench-integration
```

## Test-Driven Development (TDD) Workflow

### 1. Red-Green-Refactor Cycle

Our test suite supports the classic TDD workflow:

1. **Red**: Write a failing test first
2. **Green**: Write minimal code to make the test pass
3. **Refactor**: Improve the code while keeping tests green

### 2. Watch Mode for TDD

Use watch mode to automatically run tests when files change:

```bash
# Watch for changes and run unit tests
make tdd

# Watch for changes and run integration tests
make tdd-integration
```

### 3. Test-First Development

Before adding new functionality:

1. Write tests that describe the expected behavior
2. Run tests to see them fail (Red)
3. Implement the minimal code to pass tests (Green)
4. Refactor and improve while maintaining test coverage

## Test Coverage

### Generating Coverage Reports

```bash
# Generate HTML coverage report
make test-coverage

# View coverage in browser
open coverage.html
```

### Coverage Goals

- **Unit Test Coverage**: Aim for >90% code coverage
- **Integration Test Coverage**: Focus on critical user journeys
- **Edge Case Coverage**: Test error conditions and boundary cases

## Test Categories Explained

### Core Functionality Tests (`main_test.go`)

Tests the fundamental application logic:

- **BuildEvent**: Validates event structure and JSON marshaling
- **ResourceEventData**: Tests job completion detection logic
- **CloudEvent Handling**: Verifies proper event processing
- **Configuration**: Tests environment variable handling and defaults

### Template Processing Tests (`template_test.go`)

Ensures template engine works correctly:

- **Template Parsing**: Validates YAML template processing
- **Template Validation**: Ensures generated Kubernetes resources are valid
- **Error Handling**: Tests malformed templates and missing files
- **Context Processing**: Verifies build context template application

### Kubernetes Operations Tests (`kubernetes_test.go`)

Tests Kubernetes integration:

- **Configuration**: Validates kubeconfig handling
- **Resource Creation**: Tests Job and Service generation
- **Validation**: Ensures resources meet Kubernetes standards
- **Labeling**: Verifies proper resource labeling

### Integration Tests (`integration_test.go`)

End-to-end scenarios:

- **Complete Build Flow**: Tests entire CloudEvent → Job → Service flow
- **Template Processing**: End-to-end template processing workflow
- **Error Scenarios**: Integration-level error handling
- **Concurrency**: Tests handling multiple concurrent events

## Mock Objects and Test Data

### Mock Functions

The test suite includes helper functions for creating test data:

```go
// Create mock AWS config
config := MockAWSConfig()

// Create mock build event
buildEvent := MockBuildEvent()
```

### Test Templates

Integration tests use a complete set of realistic templates stored in temporary directories.

## Environment Setup for Testing

### Required Environment Variables

For integration tests, you may need:

```bash
# Enable integration tests
export INTEGRATION_TESTS=true

# Optional: Custom template paths
export JOB_TEMPLATE_PATH=/path/to/custom/job.yaml.tpl
export SERVICE_TEMPLATE_PATH=/path/to/custom/service.yaml.tpl

# Optional: AWS configuration (for AWS integration tests)
export ECR_BASE_REGISTRY=123456789012.dkr.ecr.us-east-1.amazonaws.com
export S3_SOURCE_BUCKET=my-test-bucket
```

### Dependencies

For Kubernetes tests to fully pass, you need:

- Valid kubeconfig file or in-cluster configuration
- Access to a Kubernetes cluster (for full integration tests)

## Continuous Integration

### Pre-commit Hooks

Run before committing code:

```bash
make pre-commit
```

This runs:
- Code formatting (`go fmt`)
- Linting (`golint`, `go vet`)
- Unit tests with coverage

### CI Pipeline

The full CI pipeline:

```bash
# Standard CI (unit tests only)
make ci

# CI with integration tests
make ci-integration
```

## Common Test Patterns

### Table-Driven Tests

Most tests use table-driven patterns for comprehensive coverage:

```go
tests := []struct {
    name     string
    input    BuildEvent
    expected bool
}{
    {
        name: "valid build event",
        input: BuildEvent{
            ThirdPartyId: "test-party",
            ParserId:     "test-parser",
        },
        expected: true,
    },
    // More test cases...
}

for _, tt := range tests {
    t.Run(tt.name, func(t *testing.T) {
        // Test logic here
    })
}
```

### Setup and Teardown

Tests use proper setup and cleanup:

```go
func TestSomething(t *testing.T) {
    // Setup
    tempDir, err := os.MkdirTemp("", "test-prefix")
    if err != nil {
        t.Fatalf("Setup failed: %v", err)
    }
    defer os.RemoveAll(tempDir) // Cleanup

    // Test logic...
}
```

## Debugging Tests

### Verbose Output

For detailed test output:

```bash
make test-verbose
```

### Race Detection

To catch concurrency issues:

```bash
make test-race
```

### Specific Test Execution

Run specific tests:

```bash
# Run specific test function
go test -v -run TestBuildEvent

# Run tests matching pattern
PATTERN="Template.*" make test-pattern
```

## Best Practices

### Writing New Tests

1. **Follow the AAA Pattern**: Arrange, Act, Assert
2. **Use Descriptive Names**: Test names should describe the scenario
3. **Test Edge Cases**: Include boundary conditions and error cases
4. **Keep Tests Independent**: Each test should be able to run in isolation
5. **Use Subtests**: Group related test cases using `t.Run()`

### Test Maintenance

1. **Keep Tests Simple**: Tests should be easier to understand than the code they test
2. **Avoid Test Dependencies**: Tests should not depend on each other
3. **Update Tests with Code Changes**: Tests are first-class citizens
4. **Review Test Coverage**: Regularly check and improve coverage

## Troubleshooting

### Common Issues

1. **Integration Tests Skipped**: Set `INTEGRATION_TESTS=true`
2. **Kubernetes Tests Fail**: Ensure valid kubeconfig or cluster access
3. **Template Tests Fail**: Check file permissions and template syntax
4. **Race Conditions**: Use proper synchronization in concurrent code

### Getting Help

If tests fail unexpectedly:

1. Run with verbose output: `make test-verbose`
2. Check test logs for specific error messages
3. Verify environment setup and dependencies
4. Run individual test files to isolate issues 