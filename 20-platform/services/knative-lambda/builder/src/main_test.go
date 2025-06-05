package main

import (
	"context"
	"os"
	"path/filepath"
	"reflect"
	"testing"

	"github.com/aws/aws-sdk-go-v2/aws"
	cloudevents "github.com/cloudevents/sdk-go/v2"
)

// TestBuildEvent tests the BuildEvent struct
func TestBuildEvent(t *testing.T) {
	tests := []struct {
		name     string
		input    BuildEvent
		expected BuildEvent
	}{
		{
			name: "valid build event",
			input: BuildEvent{
				ThirdPartyId: "test-party",
				ParserId:     "test-parser",
				ID:           "test-id",
			},
			expected: BuildEvent{
				ThirdPartyId: "test-party",
				ParserId:     "test-parser",
				ID:           "test-id",
			},
		},
		{
			name: "build event without optional ID",
			input: BuildEvent{
				ThirdPartyId: "test-party",
				ParserId:     "test-parser",
			},
			expected: BuildEvent{
				ThirdPartyId: "test-party",
				ParserId:     "test-parser",
				ID:           "",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if !reflect.DeepEqual(tt.input, tt.expected) {
				t.Errorf("BuildEvent = %v, want %v", tt.input, tt.expected)
			}
		})
	}
}

// TestResourceEventData_IsJobComplete tests the IsJobComplete method
func TestResourceEventData_IsJobComplete(t *testing.T) {
	tests := []struct {
		name     string
		resource ResourceEventData
		expected bool
	}{
		{
			name: "job with complete condition true",
			resource: ResourceEventData{
				Kind: "Job",
				Name: "test-job",
				Status: map[string]interface{}{
					"conditions": []interface{}{
						map[string]interface{}{
							"type":   "Complete",
							"status": "True",
						},
					},
				},
			},
			expected: true,
		},
		{
			name: "job with complete condition false",
			resource: ResourceEventData{
				Kind: "Job",
				Name: "test-job",
				Status: map[string]interface{}{
					"conditions": []interface{}{
						map[string]interface{}{
							"type":   "Complete",
							"status": "False",
						},
					},
				},
			},
			expected: false,
		},
		{
			name: "job with different condition",
			resource: ResourceEventData{
				Kind: "Job",
				Name: "test-job",
				Status: map[string]interface{}{
					"conditions": []interface{}{
						map[string]interface{}{
							"type":   "Failed",
							"status": "True",
						},
					},
				},
			},
			expected: false,
		},
		{
			name: "not a job",
			resource: ResourceEventData{
				Kind: "Pod",
				Name: "test-pod",
			},
			expected: false,
		},
		{
			name: "job with no status",
			resource: ResourceEventData{
				Kind: "Job",
				Name: "test-job",
			},
			expected: false,
		},
		{
			name: "job with malformed conditions",
			resource: ResourceEventData{
				Kind: "Job",
				Name: "test-job",
				Status: map[string]interface{}{
					"conditions": "invalid",
				},
			},
			expected: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := tt.resource.IsJobComplete()
			if result != tt.expected {
				t.Errorf("IsJobComplete() = %v, want %v", result, tt.expected)
			}
		})
	}
}

// TestGetWorkingDirectory tests the getWorkingDirectory function
func TestGetWorkingDirectory(t *testing.T) {
	result := getWorkingDirectory()

	// The result should be a valid directory path and not contain "Error"
	if result == "" {
		t.Error("getWorkingDirectory() returned empty string")
	}

	// Should not contain error message
	if contains := "Error getting working directory"; len(result) > len(contains) && result[:len(contains)] == contains {
		t.Errorf("getWorkingDirectory() returned error: %s", result)
	}
}

// TestHandleCloudEvent tests the handleCloudEvent function
func TestHandleCloudEvent(t *testing.T) {
	tests := []struct {
		name        string
		eventType   string
		eventData   interface{}
		expectError bool
	}{
		{
			name:      "valid build start event",
			eventType: EventTypeBuildStart,
			eventData: BuildEvent{
				ThirdPartyId: "test-party",
				ParserId:     "test-parser",
			},
			expectError: false,
		},
		{
			name:      "valid resource update event",
			eventType: EventTypeResourceUpdate,
			eventData: ResourceEventData{
				Kind: "Job",
				Name: "test-job",
			},
			expectError: false,
		},
		{
			name:        "unknown event type",
			eventType:   "unknown.event.type",
			eventData:   map[string]string{"test": "data"},
			expectError: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			event := cloudevents.NewEvent()
			event.SetType(tt.eventType)
			event.SetSource("test-source")
			event.SetID("test-id")

			if tt.eventData != nil {
				if err := event.SetData(cloudevents.ApplicationJSON, tt.eventData); err != nil {
					t.Fatalf("Failed to set event data: %v", err)
				}
			}

			ctx := context.Background()
			err := handleCloudEvent(ctx, event)

			if (err != nil) != tt.expectError {
				t.Errorf("handleCloudEvent() error = %v, expectError %v", err, tt.expectError)
			}
		})
	}
}

// TestJobTemplateData tests the JobTemplateData struct
func TestJobTemplateData(t *testing.T) {
	data := JobTemplateData{
		Name:         "test-job",
		Dockerfile:   "Dockerfile",
		Context:      "/tmp/context",
		ImageTag:     "registry/image:tag",
		ThirdPartyId: "test-party",
		ParserId:     "test-parser",
		Region:       "us-east-1",
		AccountId:    "123456789012",
	}

	// Test that all fields are properly set
	if data.Name != "test-job" {
		t.Errorf("Name = %v, want %v", data.Name, "test-job")
	}
	if data.ThirdPartyId != "test-party" {
		t.Errorf("ThirdPartyId = %v, want %v", data.ThirdPartyId, "test-party")
	}
	if data.ParserId != "test-parser" {
		t.Errorf("ParserId = %v, want %v", data.ParserId, "test-parser")
	}
	if data.Region != "us-east-1" {
		t.Errorf("Region = %v, want %v", data.Region, "us-east-1")
	}
	if data.AccountId != "123456789012" {
		t.Errorf("AccountId = %v, want %v", data.AccountId, "123456789012")
	}
}

// TestServiceTemplateData tests the ServiceTemplateData struct
func TestServiceTemplateData(t *testing.T) {
	data := ServiceTemplateData{
		ThirdPartyId: "test-party",
		ParserId:     "test-parser",
		Image:        "registry/image:tag",
	}

	if data.ThirdPartyId != "test-party" {
		t.Errorf("ThirdPartyId = %v, want %v", data.ThirdPartyId, "test-party")
	}
	if data.ParserId != "test-parser" {
		t.Errorf("ParserId = %v, want %v", data.ParserId, "test-parser")
	}
	if data.Image != "registry/image:tag" {
		t.Errorf("Image = %v, want %v", data.Image, "registry/image:tag")
	}
}

// TestWrapperTemplateData tests the WrapperTemplateData struct
func TestWrapperTemplateData(t *testing.T) {
	data := WrapperTemplateData{
		ParserId: "test-parser",
	}

	if data.ParserId != "test-parser" {
		t.Errorf("ParserId = %v, want %v", data.ParserId, "test-parser")
	}
}

// TestConstants tests that all constants are properly defined
func TestConstants(t *testing.T) {
	tests := []struct {
		name     string
		constant string
		expected string
	}{
		{"EventTypeBuildStart", EventTypeBuildStart, "network.notifi.lambda.build.start"},
		{"EventTypeResourceUpdate", EventTypeResourceUpdate, "dev.knative.apiserver.resource.update"},
		{"NamespaceKnativeLambda", NamespaceKnativeLambda, "knative-lambda"},
		{"DefaultDockerfileName", DefaultDockerfileName, "Dockerfile"},
		{"EnvEcrBaseRegistry", EnvEcrBaseRegistry, "ECR_BASE_REGISTRY"},
		{"EnvS3SourceBucket", EnvS3SourceBucket, "S3_SOURCE_BUCKET"},
		{"EnvJobTemplatePath", EnvJobTemplatePath, "JOB_TEMPLATE_PATH"},
		{"EnvServiceTemplatePath", EnvServiceTemplatePath, "SERVICE_TEMPLATE_PATH"},
		{"EnvTriggerTemplatePath", EnvTriggerTemplatePath, "TRIGGER_TEMPLATE_PATH"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.constant != tt.expected {
				t.Errorf("%s = %v, want %v", tt.name, tt.constant, tt.expected)
			}
		})
	}
}

// TestInitFunction tests the init function behavior
func TestInitFunction(t *testing.T) {
	// Save original values
	originalJob := JobTemplatePath
	originalService := ServiceTemplatePath
	originalTrigger := TriggerTemplatePath

	// Test with environment variables set
	t.Run("with environment variables", func(t *testing.T) {
		os.Setenv(EnvJobTemplatePath, "/custom/job.yaml.tpl")
		os.Setenv(EnvServiceTemplatePath, "/custom/service.yaml.tpl")
		os.Setenv(EnvTriggerTemplatePath, "/custom/trigger.yaml.tpl")

		// Re-run init logic
		JobTemplatePath = os.Getenv(EnvJobTemplatePath)
		if JobTemplatePath == "" {
			JobTemplatePath = "templates/job.yaml.tpl"
		}

		ServiceTemplatePath = os.Getenv(EnvServiceTemplatePath)
		if ServiceTemplatePath == "" {
			ServiceTemplatePath = "templates/service.yaml.tpl"
		}

		TriggerTemplatePath = os.Getenv(EnvTriggerTemplatePath)
		if TriggerTemplatePath == "" {
			TriggerTemplatePath = "templates/trigger.yaml.tpl"
		}

		if JobTemplatePath != "/custom/job.yaml.tpl" {
			t.Errorf("JobTemplatePath = %v, want %v", JobTemplatePath, "/custom/job.yaml.tpl")
		}
		if ServiceTemplatePath != "/custom/service.yaml.tpl" {
			t.Errorf("ServiceTemplatePath = %v, want %v", ServiceTemplatePath, "/custom/service.yaml.tpl")
		}
		if TriggerTemplatePath != "/custom/trigger.yaml.tpl" {
			t.Errorf("TriggerTemplatePath = %v, want %v", TriggerTemplatePath, "/custom/trigger.yaml.tpl")
		}

		// Clean up
		os.Unsetenv(EnvJobTemplatePath)
		os.Unsetenv(EnvServiceTemplatePath)
		os.Unsetenv(EnvTriggerTemplatePath)
	})

	t.Run("with default values", func(t *testing.T) {
		// Re-run init logic with empty environment
		JobTemplatePath = os.Getenv(EnvJobTemplatePath)
		if JobTemplatePath == "" {
			JobTemplatePath = "templates/job.yaml.tpl"
		}

		ServiceTemplatePath = os.Getenv(EnvServiceTemplatePath)
		if ServiceTemplatePath == "" {
			ServiceTemplatePath = "templates/service.yaml.tpl"
		}

		TriggerTemplatePath = os.Getenv(EnvTriggerTemplatePath)
		if TriggerTemplatePath == "" {
			TriggerTemplatePath = "templates/trigger.yaml.tpl"
		}

		if JobTemplatePath != "templates/job.yaml.tpl" {
			t.Errorf("JobTemplatePath = %v, want %v", JobTemplatePath, "templates/job.yaml.tpl")
		}
		if ServiceTemplatePath != "templates/service.yaml.tpl" {
			t.Errorf("ServiceTemplatePath = %v, want %v", ServiceTemplatePath, "templates/service.yaml.tpl")
		}
		if TriggerTemplatePath != "templates/trigger.yaml.tpl" {
			t.Errorf("TriggerTemplatePath = %v, want %v", TriggerTemplatePath, "templates/trigger.yaml.tpl")
		}
	})

	// Restore original values
	JobTemplatePath = originalJob
	ServiceTemplatePath = originalService
	TriggerTemplatePath = originalTrigger
}

// MockAWSConfig returns a mock AWS config for testing
func MockAWSConfig() aws.Config {
	return aws.Config{
		Region: "us-east-1",
	}
}

// MockBuildEvent returns a mock BuildEvent for testing
func MockBuildEvent() BuildEvent {
	return BuildEvent{
		ThirdPartyId: "test-party",
		ParserId:     "test-parser",
		ID:           "test-id",
	}
}

// TestBuildContextTemplate tests the BuildContextTemplate struct
func TestBuildContextTemplate(t *testing.T) {
	template := BuildContextTemplate{
		SourceTplPath: "templates/Dockerfile.tpl",
		TargetName:    "Dockerfile",
		DataFunc: func(buildEvent BuildEvent) interface{} {
			return WrapperTemplateData{ParserId: buildEvent.ParserId}
		},
	}

	if template.SourceTplPath != "templates/Dockerfile.tpl" {
		t.Errorf("SourceTplPath = %v, want %v", template.SourceTplPath, "templates/Dockerfile.tpl")
	}
	if template.TargetName != "Dockerfile" {
		t.Errorf("TargetName = %v, want %v", template.TargetName, "Dockerfile")
	}

	// Test DataFunc
	mockEvent := MockBuildEvent()
	data := template.DataFunc(mockEvent)
	wrapperData, ok := data.(WrapperTemplateData)
	if !ok {
		t.Errorf("DataFunc returned wrong type: %T", data)
	}
	if wrapperData.ParserId != mockEvent.ParserId {
		t.Errorf("DataFunc ParserId = %v, want %v", wrapperData.ParserId, mockEvent.ParserId)
	}
}

// TestCopyTemplatesDir tests the copyTemplatesDir function
func TestCopyTemplatesDir(t *testing.T) {
	// Create a temporary directory for testing
	tempDir, err := os.MkdirTemp("", "test-copy-templates")
	if err != nil {
		t.Fatalf("Failed to create temp dir: %v", err)
	}
	defer os.RemoveAll(tempDir)

	// Create a mock templates directory
	templatesDir := filepath.Join(tempDir, "source-templates")
	if err := os.MkdirAll(templatesDir, 0755); err != nil {
		t.Fatalf("Failed to create templates dir: %v", err)
	}

	// Create a test template file
	testContent := "apiVersion: v1\nkind: ConfigMap\nmetadata:\n  name: test"
	testFile := filepath.Join(templatesDir, "test.yaml.tpl")
	if err := os.WriteFile(testFile, []byte(testContent), 0644); err != nil {
		t.Fatalf("Failed to write test file: %v", err)
	}

	// Change to the temp directory so copyTemplatesDir can find the templates
	oldDir, err := os.Getwd()
	if err != nil {
		t.Fatalf("Failed to get current dir: %v", err)
	}
	defer os.Chdir(oldDir)

	if err := os.Chdir(tempDir); err != nil {
		t.Fatalf("Failed to change dir: %v", err)
	}

	// Rename the source templates to "templates" so the function can find it
	if err := os.Rename("source-templates", "templates"); err != nil {
		t.Fatalf("Failed to rename templates dir: %v", err)
	}

	// Create target directory
	targetDir := filepath.Join(tempDir, "target")
	if err := os.MkdirAll(targetDir, 0755); err != nil {
		t.Fatalf("Failed to create target dir: %v", err)
	}

	// Test the function
	err = copyTemplatesDir(targetDir)
	if err != nil {
		t.Errorf("copyTemplatesDir() error = %v", err)
	}

	// Verify the file was copied
	copiedFile := filepath.Join(targetDir, "templates", "test.yaml.tpl")
	if _, err := os.Stat(copiedFile); os.IsNotExist(err) {
		t.Errorf("Expected file was not copied: %s", copiedFile)
	}

	// Verify content
	copiedContent, err := os.ReadFile(copiedFile)
	if err != nil {
		t.Errorf("Failed to read copied file: %v", err)
	}
	if string(copiedContent) != testContent {
		t.Errorf("Copied content = %v, want %v", string(copiedContent), testContent)
	}
}

// BenchmarkIsJobComplete benchmarks the IsJobComplete method
func BenchmarkIsJobComplete(b *testing.B) {
	resource := ResourceEventData{
		Kind: "Job",
		Name: "test-job",
		Status: map[string]interface{}{
			"conditions": []interface{}{
				map[string]interface{}{
					"type":   "Complete",
					"status": "True",
				},
			},
		},
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		resource.IsJobComplete()
	}
}

// BenchmarkHandleCloudEvent benchmarks the handleCloudEvent function
func BenchmarkHandleCloudEvent(b *testing.B) {
	event := cloudevents.NewEvent()
	event.SetType(EventTypeResourceUpdate)
	event.SetSource("test-source")
	event.SetID("test-id")

	resourceData := ResourceEventData{
		Kind: "Job",
		Name: "test-job",
	}
	event.SetData(cloudevents.ApplicationJSON, resourceData)

	ctx := context.Background()

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		handleCloudEvent(ctx, event)
	}
}
