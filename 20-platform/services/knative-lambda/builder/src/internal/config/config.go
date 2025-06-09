package config

import (
	"os"
)

// =============================================================================
// 🌍 APPLICATION CONFIGURATION
// =============================================================================
// This package centralizes all configuration management
// 🎯 PURPOSE: Single place to manage environment variables and settings

// Config holds all application configuration
type Config struct {
	// S3 Configuration
	S3SourceBucket string
	S3TmpBucket    string

	// ECR Configuration
	ECRBaseRegistry string

	// Template Paths
	JobTemplatePath     string
	ServiceTemplatePath string
	TriggerTemplatePath string

	// Kubernetes Configuration
	KubernetesNamespace string

	// Docker Configuration
	DefaultDockerfileName string
}

// Environment variable names
const (
	EnvEcrBaseRegistry     = "ECR_BASE_REGISTRY"
	EnvS3SourceBucket      = "S3_SOURCE_BUCKET"
	EnvS3TmpBucket         = "S3_TMP_BUCKET"
	EnvJobTemplatePath     = "JOB_TEMPLATE_PATH"
	EnvServiceTemplatePath = "SERVICE_TEMPLATE_PATH"
	EnvTriggerTemplatePath = "TRIGGER_TEMPLATE_PATH"
)

// Default values
const (
	DefaultJobTemplatePath     = "templates/job.yaml.tpl"
	DefaultServiceTemplatePath = "templates/service.yaml.tpl"
	DefaultTriggerTemplatePath = "templates/trigger.yaml.tpl"
	DefaultKubernetesNamespace = "knative-lambda"
	DefaultDockerfileName      = "Dockerfile"
)

// Load creates a new Config from environment variables with sensible defaults
// 🎯 PURPOSE: Initialize configuration once at startup
func Load() *Config {
	return &Config{
		// S3 Configuration
		S3SourceBucket: os.Getenv(EnvS3SourceBucket),
		S3TmpBucket:    os.Getenv(EnvS3TmpBucket),

		// ECR Configuration
		ECRBaseRegistry: os.Getenv(EnvEcrBaseRegistry),

		// Template Paths with defaults
		JobTemplatePath:     getEnvOrDefault(EnvJobTemplatePath, DefaultJobTemplatePath),
		ServiceTemplatePath: getEnvOrDefault(EnvServiceTemplatePath, DefaultServiceTemplatePath),
		TriggerTemplatePath: getEnvOrDefault(EnvTriggerTemplatePath, DefaultTriggerTemplatePath),

		// Constants
		KubernetesNamespace:   DefaultKubernetesNamespace,
		DefaultDockerfileName: DefaultDockerfileName,
	}
}

// getEnvOrDefault returns environment variable value or default if not set
func getEnvOrDefault(envVar, defaultValue string) string {
	if value := os.Getenv(envVar); value != "" {
		return value
	}
	return defaultValue
}
