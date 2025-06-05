package main

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"html/template"
	"io"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"time"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/ecr"
	ecrtypes "github.com/aws/aws-sdk-go-v2/service/ecr/types"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/aws/aws-sdk-go-v2/service/sts"
	cloudevents "github.com/cloudevents/sdk-go/v2"
	"github.com/google/uuid"
	batchv1 "k8s.io/api/batch/v1"
	corev1 "k8s.io/api/core/v1"
	k8serrors "k8s.io/apimachinery/pkg/api/errors"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/apis/meta/v1/unstructured"
	"k8s.io/apimachinery/pkg/runtime/schema"
	"k8s.io/client-go/dynamic"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/clientcmd"
	"sigs.k8s.io/yaml"
)

// BuildEvent is the event that is sent to the builder
type BuildEvent struct {
	ThirdPartyId string `json:"thirdPartyId"`
	ParserId     string `json:"parserId"`
	ID           string `json:"id,omitempty"`
}

// JobTemplateData holds data for job.yaml.tpl
type JobTemplateData struct {
	Name         string
	Dockerfile   string
	Context      string
	ImageTag     string
	ThirdPartyId string
	ParserId     string
	Region       string
	AccountId    string
}

// ServiceTemplateData holds data for service.yaml.tpl
type ServiceTemplateData struct {
	ThirdPartyId string
	ParserId     string
	Image        string
}

// WrapperTemplateData holds data for wrapper.js
type WrapperTemplateData struct {
	ParserId string
}

// ResourceEventData represents the data in a Kubernetes resource event
type ResourceEventData struct {
	Kind       string                 `json:"kind"`
	Name       string                 `json:"name"`
	Status     map[string]interface{} `json:"status,omitempty"`
	BuildEvent BuildEvent             `json:"buildEvent"`
}

// IsJobComplete checks if a job is complete based on its status conditions
func (r *ResourceEventData) IsJobComplete() bool {
	if r.Kind != "Job" || r.Status == nil {
		return false
	}

	// Check for conditions array in the status
	conditions, ok := r.Status["conditions"].([]interface{})
	if !ok {
		return false
	}

	// Look for the Complete condition with True status
	for _, cond := range conditions {
		condition, ok := cond.(map[string]interface{})
		if !ok {
			continue
		}

		condType, typeOk := condition["type"].(string)
		status, statusOk := condition["status"].(string)

		if typeOk && statusOk && condType == "Complete" && status == "True" {
			return true
		}
	}

	return false
}

const (
	// CloudEvent types
	EventTypeBuildStart     = "network.notifi.lambda.build.start"
	EventTypeResourceUpdate = "dev.knative.apiserver.resource.update"

	// Kubernetes namespaces
	NamespaceKnativeLambda = "knative-lambda"

	// File paths - Dockerfile name remains a const
	DefaultDockerfileName = "Dockerfile"

	// Environment variables
	EnvEcrBaseRegistry     = "ECR_BASE_REGISTRY"
	EnvS3SourceBucket      = "S3_SOURCE_BUCKET"
	EnvJobTemplatePath     = "JOB_TEMPLATE_PATH"
	EnvServiceTemplatePath = "SERVICE_TEMPLATE_PATH"
	EnvTriggerTemplatePath = "TRIGGER_TEMPLATE_PATH"
)

var (
	JobTemplatePath     string
	ServiceTemplatePath string
	TriggerTemplatePath string
)

var buildEvent BuildEvent

func init() {
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
}

func main() {
	log.Println("Starting builder...")
	log.Printf("Go version: %s", runtime.Version())

	// Log current working directory
	pwd, err := os.Getwd()
	if err != nil {
		log.Printf("Failed to get working directory: %v", err)
	} else {
		log.Printf("Current working directory: %s", pwd)
	}

	log.Printf("Effective JobTemplatePath: %s", JobTemplatePath)
	log.Printf("Effective ServiceTemplatePath: %s", ServiceTemplatePath)
	log.Printf("Effective TriggerTemplatePath: %s", TriggerTemplatePath)

	log.Printf("Working directory: %s", getWorkingDirectory())
	log.Printf("Environment variables: S3_SOURCE_BUCKET=%s, ECR_BASE_REGISTRY=%s",
		os.Getenv(EnvS3SourceBucket),
		os.Getenv(EnvEcrBaseRegistry))

	// List templates directory
	if entries, err := os.ReadDir("templates"); err == nil {
		log.Print("Available templates:")
		for _, entry := range entries {
			log.Printf("  - %s", entry.Name())
		}
	} else {
		log.Printf("ERROR: Failed to list templates directory: %v", err)
	}

	ctx := context.Background()
	p, err := cloudevents.NewHTTP()
	if err != nil {
		log.Fatalf("Failed to create protocol: %v", err)
	}

	c, err := cloudevents.NewClient(p)
	if err != nil {
		log.Fatalf("Failed to create client: %v", err)
	}

	log.Println("Starting cloudevents receiver...")
	if err := c.StartReceiver(ctx, handleCloudEvent); err != nil {
		log.Fatalf("Failed to start receiver: %v", err)
	}
}

// Helper function to get current working directory
func getWorkingDirectory() string {
	dir, err := os.Getwd()
	if err != nil {
		return fmt.Sprintf("Error getting working directory: %v", err)
	}
	return dir
}

func handleCloudEvent(ctx context.Context, event cloudevents.Event) error {
	log.Printf("Received CloudEvent: %s, ID: %s", event.Type(), event.ID())
	log.Printf("CloudEvent source: %s", event.Source())
	log.Printf("CloudEvent subject: %s", event.Subject())
	log.Printf("CloudEvent data content type: %s", event.DataContentType())

	// Log raw data for debugging
	rawData := event.Data()
	if len(rawData) > 0 {
		log.Printf("CloudEvent raw data: %s", string(rawData))
	}

	switch event.Type() {
	case EventTypeBuildStart:
		log.Printf("Processing build start event")

		if err := event.DataAs(&buildEvent); err != nil {
			log.Printf("ERROR: Failed to parse build event: %v", err)
			return fmt.Errorf("failed to parse build event: %w", err)
		}

		log.Printf("Successfully parsed build event: %+v", buildEvent)

		// Run job creation in the background to avoid blocking the event handler
		go func(be BuildEvent) {
			if err := createKanikoJob(be); err != nil {
				log.Printf("ERROR: Background job creation failed: %v", err)
			}
		}(buildEvent)

		return nil

	case EventTypeResourceUpdate:
		log.Printf("Processing resource update event")
		var resourceEvent ResourceEventData

		// Log raw event data for debugging
		log.Printf("Raw event data: %s", string(event.Data()))

		if err := event.DataAs(&resourceEvent); err != nil {
			log.Printf("ERROR: Failed to parse resource event: %v", err)
			// Don't return an error - just log it and continue
			return nil
		}

		log.Printf("Received resource event: Kind=%s, Name=%s",
			resourceEvent.Kind, resourceEvent.Name)

		// Log status in more detail for debugging
		if resourceEvent.Status != nil {
			if conditions, ok := resourceEvent.Status["conditions"].([]interface{}); ok {
				log.Printf("Job conditions:")
				for _, c := range conditions {
					if cond, ok := c.(map[string]interface{}); ok {
						log.Printf("  Type: %v, Status: %v, Reason: %v",
							cond["type"], cond["status"], cond["reason"])
					}
				}
			}
		}

		// When the job is completed: createParserService
		if resourceEvent.Kind == "Job" && resourceEvent.IsJobComplete() {
			log.Printf("Job completed, creating parser service")

			log.Printf("Creating parser service for ThirdPartyId=%s, ParserId=%s",
				buildEvent.ThirdPartyId, buildEvent.ParserId)

			go func(be BuildEvent) {
				if err := createParserService(be); err != nil {
					log.Printf("ERROR: Background parser service creation failed: %v", err)
				}
			}(buildEvent)
			return nil
		}
	default:
		log.Printf("Received unknown event type: %s", event.Type())
	}

	return nil
}

func createKanikoJob(buildEvent BuildEvent) error {
	log.Printf("Creating kaniko job for ThirdPartyId=%s, ParserId=%s",
		buildEvent.ThirdPartyId, buildEvent.ParserId)
	log.Printf("Build event details: %+v", buildEvent)

	// Create a unique job name
	jobName := fmt.Sprintf("build-%s-%s-%s",
		buildEvent.ThirdPartyId,
		buildEvent.ParserId,
		uuid.New().String()[0:8])

	// Download the code from S3
	sourcePath, err := downloadSourceFromS3(buildEvent)
	if err != nil {
		return fmt.Errorf("failed to download source from S3: %w", err)
	}

	// Upload the build context to S3 for Kaniko
	if err := uploadContextToS3(sourcePath, buildEvent); err != nil {
		log.Printf("WARNING: Failed to upload context to S3: %v", err)
	}

	// ECR and Image Configuration
	awsOpCtx, awsOpCancel := context.WithTimeout(context.Background(), 60*time.Second) // Context for AWS operations
	defer awsOpCancel()

	awsCfg, err := config.LoadDefaultConfig(awsOpCtx)
	if err != nil {
		return fmt.Errorf("failed to load AWS config for ECR operations: %w", err)
	}

	// Get AWS account ID using STS
	stsClient := sts.NewFromConfig(awsCfg)
	callerIdentity, err := stsClient.GetCallerIdentity(awsOpCtx, &sts.GetCallerIdentityInput{})
	if err != nil {
		return fmt.Errorf("failed to get AWS caller identity: %w", err)
	}

	// Use dynamic account ID for ECR base registry
	accountID := aws.ToString(callerIdentity.Account)
	ecrBaseRegistry := os.Getenv(EnvEcrBaseRegistry)
	if ecrBaseRegistry == "" {
		ecrBaseRegistry = fmt.Sprintf("%s.dkr.ecr.%s.amazonaws.com", accountID, awsCfg.Region)
		log.Printf("%s not set, using dynamic ECR base registry: %s", EnvEcrBaseRegistry, ecrBaseRegistry)
	}

	ecrRepositoryName := fmt.Sprintf("knative-lambdas/%s", buildEvent.ThirdPartyId)
	imageTag := buildEvent.ParserId // Using ParserId as the image tag
	fullImageURI := fmt.Sprintf("%s/%s:%s", ecrBaseRegistry, ecrRepositoryName, imageTag)
	log.Printf("Full image URI for Kaniko: %s", fullImageURI)

	// Ensure ECR repository exists
	if err := ensureEcrRepoExists(awsOpCtx, awsCfg, ecrRepositoryName); err != nil {
		return fmt.Errorf("failed to ensure ECR repository %s exists: %w", ecrRepositoryName, err)
	}

	// Parse job template
	jobTemplateData := JobTemplateData{
		Name:         jobName,
		Dockerfile:   DefaultDockerfileName,
		Context:      sourcePath,   // This context is for Kaniko, referring to the S3 path of the tarball
		ImageTag:     fullImageURI, // Kaniko will push to this full image URI
		ThirdPartyId: buildEvent.ThirdPartyId,
		ParserId:     buildEvent.ParserId,
		Region:       awsCfg.Region,
		AccountId:    accountID,
	}
	log.Printf("Job template data: %+v", jobTemplateData)

	// Apply template to create the job
	k8sClient, err := getKubernetesClient()
	if err != nil {
		return fmt.Errorf("failed to get kubernetes client: %w", err)
	}

	// Check if namespace exists
	ctxCheck, cancelCheck := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancelCheck()

	_, err = k8sClient.CoreV1().Namespaces().Get(ctxCheck, NamespaceKnativeLambda, metav1.GetOptions{})
	if err != nil {
		log.Printf("WARNING: Could not verify namespace %s: %v", NamespaceKnativeLambda, err)
	} else {
		log.Printf("Confirmed namespace %s exists", NamespaceKnativeLambda)
	}

	// Try to list jobs in namespace to verify permissions
	_, err = k8sClient.BatchV1().Jobs(NamespaceKnativeLambda).List(ctxCheck, metav1.ListOptions{Limit: 1})
	if err != nil {
		log.Printf("WARNING: Could not list jobs in namespace %s: %v", NamespaceKnativeLambda, err)
	} else {
		log.Printf("Confirmed permission to list jobs in namespace %s", NamespaceKnativeLambda)
	}

	// Get absolute path to template
	log.Printf("Using Job template path: %s", JobTemplatePath)

	// Parse the job template
	var job batchv1.Job
	if err := parseTemplate(JobTemplatePath, jobTemplateData, &job); err != nil {
		return fmt.Errorf("failed to parse job template: %w", err)
	}

	// Verify critical fields
	log.Printf("Verifying job fields after template parsing")
	log.Printf("Job name: %s", job.ObjectMeta.Name)
	log.Printf("Job namespace: %s", job.ObjectMeta.Namespace)

	if len(job.Spec.Template.Spec.Containers) > 0 {
		log.Printf("Container name: %s", job.Spec.Template.Spec.Containers[0].Name)
		log.Printf("Container image: %s", job.Spec.Template.Spec.Containers[0].Image)
		log.Printf("Container args: %v", job.Spec.Template.Spec.Containers[0].Args)
	} else {
		log.Printf("WARNING: No containers in job template!")
	}

	log.Printf("ServiceAccountName: %s", job.Spec.Template.Spec.ServiceAccountName)
	log.Printf("RestartPolicy: %s", job.Spec.Template.Spec.RestartPolicy)

	// Ensure required fields are set
	if job.ObjectMeta.Name == "" {
		log.Printf("Setting job name: %s", jobName)
		job.ObjectMeta.Name = jobName
	}

	if job.ObjectMeta.Namespace == "" {
		log.Printf("Setting job namespace: %s", NamespaceKnativeLambda)
		job.ObjectMeta.Namespace = NamespaceKnativeLambda
	}

	if job.Spec.Template.Spec.ServiceAccountName == "" {
		log.Printf("Setting ServiceAccountName: knative-lambda-builder")
		job.Spec.Template.Spec.ServiceAccountName = "knative-lambda-builder"
	}

	// Explicitly set the restart policy to a valid value
	job.Spec.Template.Spec.RestartPolicy = corev1.RestartPolicyNever
	log.Printf("Explicitly set RestartPolicy to: %s", job.Spec.Template.Spec.RestartPolicy)

	// Create the job
	log.Printf("Creating job with name: %s, namespace: %s, serviceAccount: %s",
		job.ObjectMeta.Name,
		job.ObjectMeta.Namespace,
		job.Spec.Template.Spec.ServiceAccountName)

	// Create context with timeout for job creation
	ctxWithTimeout, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	_, err = k8sClient.BatchV1().Jobs(NamespaceKnativeLambda).Create(
		ctxWithTimeout,
		&job,
		metav1.CreateOptions{},
	)
	if err != nil {
		log.Printf("ERROR: Failed to create job: %v", err)
		// Try to describe the job if creation failed due to already exists
		if k8serrors.IsAlreadyExists(err) {
			log.Printf("Job %s already exists. Checking its status.", jobName)
			// Potentially fetch and log job status here if needed for debugging
		}
		return fmt.Errorf("failed to create job: %w", err)
	}

	log.Printf("Created kaniko job: %s", jobName)
	return nil
}

// ensureEcrRepoExists checks if an ECR repository exists, and creates it if it doesn't.
func ensureEcrRepoExists(ctx context.Context, cfg aws.Config, repositoryName string) error {
	ecrClient := ecr.NewFromConfig(cfg)

	log.Printf("Checking if ECR repository %s exists...", repositoryName)
	_, err := ecrClient.DescribeRepositories(ctx, &ecr.DescribeRepositoriesInput{
		RepositoryNames: []string{repositoryName},
	})

	if err != nil {
		var rnfe *ecrtypes.RepositoryNotFoundException
		// Correct way to check for the specific AWS error type
		if strings.Contains(err.Error(), "RepositoryNotFoundException") || errors.As(err, &rnfe) {
			log.Printf("ECR repository %s not found, creating it.", repositoryName)
			_, createErr := ecrClient.CreateRepository(ctx, &ecr.CreateRepositoryInput{
				RepositoryName: aws.String(repositoryName),
				ImageScanningConfiguration: &ecrtypes.ImageScanningConfiguration{
					ScanOnPush: true,
				},
				ImageTagMutability: ecrtypes.ImageTagMutabilityMutable, // Consider IMMUTABLE for production
			})
			if createErr != nil {
				return fmt.Errorf("failed to create ECR repository %s: %w", repositoryName, createErr)
			}
			log.Printf("Successfully created ECR repository %s", repositoryName)
			return nil
		}
		// For other errors during DescribeRepositories
		return fmt.Errorf("failed to describe ECR repository %s: %w", repositoryName, err)
	}

	log.Printf("ECR repository %s already exists.", repositoryName)
	return nil
}

// uploadContextToS3 creates a tarball of the build context and uploads it to S3
func uploadContextToS3(contextDir string, buildEvent BuildEvent) error {
	log.Printf("Uploading build context to S3 for Kaniko")

	// Create context with timeout
	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()

	// Get S3 bucket name
	bucket := os.Getenv(EnvS3SourceBucket)
	if bucket == "" {
		bucket = buildEvent.ThirdPartyId
		log.Printf("S3_SOURCE_BUCKET not set, using ThirdPartyId as bucket: %s", bucket)
	}

	// Create a tarball of the context directory
	tarballPath := filepath.Join(os.TempDir(), fmt.Sprintf("%s-%s.tar.gz",
		buildEvent.ThirdPartyId,
		buildEvent.ParserId))

	log.Printf("Creating context tarball at %s", tarballPath)
	cmd := exec.Command("tar", "-czf", tarballPath, "-C", contextDir, ".")
	output, err := cmd.CombinedOutput()
	if err != nil {
		return fmt.Errorf("failed to create context tarball: %w, output: %s", err, string(output))
	}

	// Check if tarball was created
	fileInfo, err := os.Stat(tarballPath)
	if err != nil {
		return fmt.Errorf("failed to stat context tarball: %w", err)
	}
	log.Printf("Created context tarball: %s (%d bytes)", tarballPath, fileInfo.Size())

	// Load AWS config
	cfg, err := config.LoadDefaultConfig(ctx)
	if err != nil {
		return fmt.Errorf("failed to load AWS config: %w", err)
	}

	// Create S3 client
	s3Client := s3.NewFromConfig(cfg)

	// Open tarball file for upload
	file, err := os.Open(tarballPath)
	if err != nil {
		return fmt.Errorf("failed to open context tarball: %w", err)
	}
	defer file.Close()

	// Key for the S3 object - use the same format as in the job template
	key := fmt.Sprintf("%s.tar.gz", buildEvent.ParserId)

	// Upload tarball to S3
	log.Printf("Uploading context tarball to s3://%s/%s", bucket, key)
	_, err = s3Client.PutObject(ctx, &s3.PutObjectInput{
		Bucket: aws.String(bucket),
		Key:    aws.String(key),
		Body:   file,
	})
	if err != nil {
		return fmt.Errorf("failed to upload context tarball to S3: %w", err)
	}

	log.Printf("Successfully uploaded context tarball to S3")

	// Cleanup
	if err := os.Remove(tarballPath); err != nil {
		log.Printf("WARNING: Failed to remove temporary tarball: %v", err)
	}

	return nil
}

func createParserService(buildEvent BuildEvent) error {
	log.Printf("Creating parser service for %s-%s", buildEvent.ThirdPartyId, buildEvent.ParserId)

	awsOpCtx, awsOpCancel := context.WithTimeout(context.Background(), 60*time.Second) // Context for AWS operations
	defer awsOpCancel()

	awsCfg, err := config.LoadDefaultConfig(awsOpCtx)
	if err != nil {
		return fmt.Errorf("failed to load AWS config for ECR operations: %w", err)
	}

	// Get AWS account ID using STS
	stsClient := sts.NewFromConfig(awsCfg)
	callerIdentity, err := stsClient.GetCallerIdentity(awsOpCtx, &sts.GetCallerIdentityInput{})
	if err != nil {
		return fmt.Errorf("failed to get AWS caller identity: %w", err)
	}

	// Use dynamic account ID for ECR base registry
	accountID := aws.ToString(callerIdentity.Account)
	ecrBaseRegistry := os.Getenv(EnvEcrBaseRegistry)
	if ecrBaseRegistry == "" {
		ecrBaseRegistry = fmt.Sprintf("%s.dkr.ecr.%s.amazonaws.com", accountID, awsCfg.Region)
		log.Printf("%s not set, using dynamic ECR base registry: %s", EnvEcrBaseRegistry, ecrBaseRegistry)
	}

	ecrRepositoryName := fmt.Sprintf("knative-lambdas/%s", buildEvent.ThirdPartyId)
	imageIdentifierTag := buildEvent.ParserId
	fullImageURI := fmt.Sprintf("%s/%s:%s", ecrBaseRegistry, ecrRepositoryName, imageIdentifierTag)

	log.Printf("Using image URI for service: %s", fullImageURI)

	serviceTemplateData := ServiceTemplateData{
		ThirdPartyId: buildEvent.ThirdPartyId,
		ParserId:     buildEvent.ParserId,
		Image:        fullImageURI, // Use the consistent image URI
	}

	// Create Knative service from template
	var serviceYAML bytes.Buffer
	serviceTemplate, err := template.ParseFiles(ServiceTemplatePath)
	if err != nil {
		return fmt.Errorf("failed to parse service template: %w", err)
	}

	if err := serviceTemplate.Execute(&serviceYAML, serviceTemplateData); err != nil {
		return fmt.Errorf("failed to execute service template: %w", err)
	}

	// Apply Knative service YAML using kubectl
	if err := applyKubernetesResource(serviceYAML.String()); err != nil {
		return fmt.Errorf("failed to apply Knative service: %w", err)
	}

	// Create RabbitMQ source from template
	var triggerYAML bytes.Buffer
	triggerTemplate, err := template.ParseFiles(TriggerTemplatePath)
	if err != nil {
		return fmt.Errorf("failed to parse trigger template: %w", err)
	}

	if err := triggerTemplate.Execute(&triggerYAML, serviceTemplateData); err != nil {
		return fmt.Errorf("failed to execute trigger template: %w", err)
	}

	// Apply trigger YAML using kubectl
	if err := applyKubernetesResource(triggerYAML.String()); err != nil {
		return fmt.Errorf("failed to apply trigger: %w", err)
	}

	log.Printf("Created parser service for %s-%s", buildEvent.ThirdPartyId, buildEvent.ParserId)
	return nil
}

func downloadSourceFromS3(buildEvent BuildEvent) (string, error) {
	log.Printf("Downloading source from S3 for %s/%s.js", buildEvent.ThirdPartyId, buildEvent.ParserId)

	// Create context with timeout
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// Create temporary directory for source code
	tempDir, err := os.MkdirTemp("", fmt.Sprintf("lambda-%s-%s-*",
		buildEvent.ThirdPartyId,
		buildEvent.ParserId))
	if err != nil {
		return "", fmt.Errorf("failed to create temp dir: %w", err)
	}

	// Copy templates directory to the build context
	log.Printf("Copying templates directory to build context: %s", tempDir)
	if err := copyTemplatesDir(tempDir); err != nil {
		log.Printf("ERROR: Failed to copy templates directory: %v", err)
		return "", fmt.Errorf("failed to copy templates directory: %w", err)
	}

	// find the bucket = {thirdPartyId}
	// get the parser = {parserId}.js
	// upload a result file == {thirdPartyId}/{parserId}.tar.gz
	bucket := os.Getenv(EnvS3SourceBucket)
	if bucket == "" {
		bucket = buildEvent.ThirdPartyId
		log.Printf("S3_SOURCE_BUCKET not set, using ThirdPartyId as bucket: %s", bucket)
	}

	// Download the parser file
	parserKey := fmt.Sprintf("%s.js", buildEvent.ParserId)
	parserFilePath := filepath.Join(tempDir, parserKey)

	// Ensure directory exists
	if err := os.MkdirAll(filepath.Dir(parserFilePath), 0755); err != nil {
		return "", fmt.Errorf("failed to create parser directory: %w", err)
	}

	log.Printf("Downloading parser file from s3://%s/%s", bucket, parserKey)

	// Check if running in Kubernetes with a service account
	tokenFile := "/var/run/secrets/eks.amazonaws.com/serviceaccount/token"
	if _, err := os.Stat(tokenFile); err == nil {
		log.Printf("Found EKS service account token at %s, using pod identity", tokenFile)

		// Log additional information for debugging
		roleArnFile := "/var/run/secrets/eks.amazonaws.com/serviceaccount/role-arn"
		if roleArnBytes, err := os.ReadFile(roleArnFile); err == nil {
			log.Printf("Using IAM role: %s", string(roleArnBytes))
		}

		// Set environment variables explicitly for AWS SDK
		os.Setenv("AWS_WEB_IDENTITY_TOKEN_FILE", tokenFile)
		if roleArnBytes, err := os.ReadFile(roleArnFile); err == nil {
			os.Setenv("AWS_ROLE_ARN", string(roleArnBytes))
		}
		os.Setenv("AWS_SDK_LOAD_CONFIG", "true")
	}

	// Load AWS config - will automatically use environment variables set above
	log.Printf("Loading AWS SDK configuration")
	cfg, err := config.LoadDefaultConfig(ctx)
	if err != nil {
		log.Printf("ERROR: Failed to load AWS config: %v", err)
		return "", fmt.Errorf("failed to load AWS config: %w", err)
	}

	// Additional logging to help diagnose credential issues
	log.Printf("AWS SDK loaded, creating S3 client")
	s3Client := s3.NewFromConfig(cfg)

	// Try to get the object from S3
	log.Printf("Getting object from S3: %s/%s", bucket, parserKey)
	output, err := s3Client.GetObject(ctx, &s3.GetObjectInput{
		Bucket: aws.String(bucket),
		Key:    aws.String(parserKey),
	})
	if err != nil {
		log.Printf("ERROR: S3 GetObject failed: %v", err)
		return "", fmt.Errorf("failed to get object from S3: %w", err)
	}
	defer output.Body.Close()

	// Save the object to a file
	log.Printf("Writing S3 object to file: %s", parserFilePath)
	file, err := os.Create(parserFilePath)
	if err != nil {
		log.Printf("ERROR: Failed to create local file: %v", err)
		return "", fmt.Errorf("failed to create local file: %w", err)
	}
	defer file.Close()

	_, err = io.Copy(file, output.Body)
	if err != nil {
		log.Printf("ERROR: Failed to copy S3 object to file: %v", err)
		return "", fmt.Errorf("failed to copy S3 object to file: %w", err)
	}

	// Verify file was downloaded
	fileInfo, err := os.Stat(parserFilePath)
	if err != nil {
		log.Printf("ERROR: Failed to stat downloaded file: %v", err)
		return "", fmt.Errorf("failed to verify downloaded file: %w", err)
	}

	log.Printf("Downloaded parser file size: %d bytes", fileInfo.Size())

	if fileInfo.Size() == 0 {
		log.Printf("ERROR: Downloaded parser file is empty")
		return "", fmt.Errorf("downloaded parser file is empty")
	}

	// Process build context templates (Dockerfile, index.js, package.json)
	if err := processBuildContextTemplates(tempDir, buildEvent); err != nil {
		return "", fmt.Errorf("failed to process build context templates: %w", err)
	}

	log.Printf("Successfully prepared build directory at %s", tempDir)
	return tempDir, nil
}

// BuildContextTemplate defines a template file to be processed for the build context.
type BuildContextTemplate struct {
	SourceTplPath string                                  // Relative path from project root, e.g., "templates/Dockerfile.tpl"
	TargetName    string                                  // Target filename in the tempDir, e.g., "Dockerfile"
	DataFunc      func(buildEvent BuildEvent) interface{} // Function to get the template data
}

// buildContextTemplates lists the templates to be processed into the root of the build context.
var buildContextTemplates = []BuildContextTemplate{
	{
		SourceTplPath: "templates/Dockerfile.tpl",
		TargetName:    DefaultDockerfileName, // "Dockerfile"
		DataFunc:      func(be BuildEvent) interface{} { return be },
	},
	{
		SourceTplPath: "templates/index.js.tpl", // Assumes your wrapper is now here
		TargetName:    "index.js",
		DataFunc:      func(be BuildEvent) interface{} { return WrapperTemplateData{ParserId: be.ParserId} },
	},
	{
		SourceTplPath: "templates/package.json.tpl",
		TargetName:    "package.json",
		DataFunc:      func(be BuildEvent) interface{} { return be },
	},
	{
		SourceTplPath: "templates/func.yaml.tpl",
		TargetName:    "func.yaml",
		DataFunc:      func(be BuildEvent) interface{} { return WrapperTemplateData{ParserId: be.ParserId} },
	},
}

// processBuildContextTemplates reads, templates, and writes core files for the build context.
func processBuildContextTemplates(tempDir string, buildEvent BuildEvent) error {
	for _, tplInfo := range buildContextTemplates {
		log.Printf("Processing build context template %s -> %s", tplInfo.SourceTplPath, filepath.Join(tempDir, tplInfo.TargetName))

		content, err := os.ReadFile(tplInfo.SourceTplPath)
		if err != nil {
			return fmt.Errorf("failed to read build context template %s: %w", tplInfo.SourceTplPath, err)
		}

		tmpl, err := template.New(filepath.Base(tplInfo.SourceTplPath)).Parse(string(content))
		if err != nil {
			return fmt.Errorf("failed to parse build context template %s: %w", tplInfo.SourceTplPath, err)
		}

		destPath := filepath.Join(tempDir, tplInfo.TargetName)
		destFile, err := os.Create(destPath)
		if err != nil {
			return fmt.Errorf("failed to create destination file %s for template %s: %w", destPath, tplInfo.SourceTplPath, err)
		}
		defer destFile.Close() // Close file within the loop

		templateData := tplInfo.DataFunc(buildEvent)
		if err := tmpl.Execute(destFile, templateData); err != nil {
			// Ensure file is closed before returning error if Execute fails
			// destFile.Close() // Already deferred
			return fmt.Errorf("failed to execute build context template %s to %s: %w", tplInfo.SourceTplPath, destPath, err)
		}
		// destFile.Close() // Ensure data is flushed, already deferred
		log.Printf("Successfully generated %s from %s", destPath, tplInfo.SourceTplPath)
	}
	return nil
}

func applyKubernetesResource(yamlContent string) error {
	log.Printf("Applying Kubernetes resource using API (re-create strategy)")

	k8sRestConfig, err := getKubernetesConfig()
	if err != nil {
		return fmt.Errorf("failed to get kubernetes config: %w", err)
	}

	// Parse the YAML into a map to determine the kind and API version
	var obj map[string]interface{}
	if err := yaml.Unmarshal([]byte(yamlContent), &obj); err != nil {
		return fmt.Errorf("failed to decode resource YAML: %w", err)
	}

	// Extract resource type info
	apiVersion, _ := obj["apiVersion"].(string)
	kind, _ := obj["kind"].(string)
	metadata, _ := obj["metadata"].(map[string]interface{})
	name, _ := metadata["name"].(string)
	namespaceVal, _ := metadata["namespace"].(string)

	if namespaceVal == "" {
		namespaceVal = NamespaceKnativeLambda // Default to knative-lambda if not specified
		log.Printf("Resource namespace not specified in YAML, defaulting to '%s' for %s/%s", namespaceVal, kind, name)
	}

	log.Printf("Resource metadata: Type=%s/%s, Name=%s, Namespace=%s",
		apiVersion, kind, name, namespaceVal)

	// Create context with timeout that covers potential delete and create operations
	ctx, cancel := context.WithTimeout(context.Background(), 90*time.Second) // Increased timeout
	defer cancel()

	// Log specific type before applying
	switch {
	case apiVersion == "serving.knative.dev/v1" && kind == "Service":
		log.Printf("Preparing to re-create Knative Service: %s in namespace %s", name, namespaceVal)
	case apiVersion == "sources.knative.dev/v1" && kind == "RabbitmqSource":
		log.Printf("Preparing to re-create Knative RabbitmqSource: %s in namespace %s", name, namespaceVal)
	default:
		log.Printf("Preparing to re-create resource dynamically: %s/%s, Name: %s in namespace %s", apiVersion, kind, name, namespaceVal)
	}

	return applyUnstructuredResource(ctx, k8sRestConfig, yamlContent, namespaceVal)
}

// Helper function to apply a resource using the dynamic client (delete then create strategy)
func applyUnstructuredResource(ctx context.Context, k8sRestConfig *rest.Config, yamlContent, namespace string) error {
	dynamicClient, err := dynamic.NewForConfig(k8sRestConfig)
	if err != nil {
		return fmt.Errorf("failed to create dynamic client from config: %w", err)
	}

	jsonData, err := yaml.YAMLToJSON([]byte(yamlContent))
	if err != nil {
		return fmt.Errorf("failed to convert YAML to JSON: %w", err)
	}

	var unstructuredObj unstructured.Unstructured
	if err := json.Unmarshal(jsonData, &unstructuredObj); err != nil {
		return fmt.Errorf("failed to unmarshal resource JSON: %w", err)
	}

	gvk := unstructuredObj.GroupVersionKind()
	resourceName := unstructuredObj.GetName()

	// Determine the resource string for the API (plural form)
	resourceStr := strings.ToLower(gvk.Kind) + "s"
	switch gvk.Kind { // Add common irregular pluralizations or kinds that are already plural
	case "Endpoints":
		resourceStr = "endpoints"
	case "SecurityContextConstraints":
		resourceStr = "securitycontextconstraints"
	case "NetworkPolicy":
		resourceStr = "networkpolicies"
		// Add more specific cases as identified
	}

	apiResource := schema.GroupVersionResource{
		Group:    gvk.Group,
		Version:  gvk.Version,
		Resource: resourceStr,
	}

	log.Printf("Attempting to re-create resource: Kind=%s, Name=%s, Namespace=%s, APIResource=%s.%s/%s",
		gvk.Kind, resourceName, namespace, apiResource.Resource, apiResource.Group, apiResource.Version)

	// 1. Delete the resource if it exists
	log.Printf("Attempting to delete resource %s (%s) in namespace %s if it exists...", resourceName, gvk.Kind, namespace)
	deletePropagation := metav1.DeletePropagationBackground
	err = dynamicClient.Resource(apiResource).Namespace(namespace).Delete(ctx, resourceName, metav1.DeleteOptions{
		PropagationPolicy: &deletePropagation,
	})

	if err != nil {
		if k8serrors.IsNotFound(err) {
			log.Printf("Resource %s (%s) not found in namespace %s. No deletion needed.", resourceName, gvk.Kind, namespace)
		} else {
			log.Printf("Error deleting resource %s (%s) in namespace %s: %v. YAML snippet for context: %.100s...", resourceName, gvk.Kind, namespace, err, yamlContent)
			return fmt.Errorf("failed to delete existing resource %s (%s) in namespace %s during re-create: %w", resourceName, gvk.Kind, namespace, err)
		}
	} else {
		log.Printf("Successfully deleted resource %s (%s) in namespace %s (or it was already terminating/deleted).", resourceName, gvk.Kind, namespace)
		// For robust re-creation, one might wait/poll for the resource to be fully gone,
		// especially if it has finalizers. For this implementation, we proceed to create.
		// A small, fixed delay can sometimes help, but isn't a guaranteed fix for race conditions.
		// time.Sleep(2 * time.Second) // Example: optional short delay
	}

	// 2. Create the resource
	// The unstructuredObj is pristine from the initial YAML unmarshal, so it's suitable for creation.
	log.Printf("Attempting to create resource %s (%s) in namespace %s...", resourceName, gvk.Kind, namespace)
	createdObj, createErr := dynamicClient.Resource(apiResource).Namespace(namespace).Create(ctx, &unstructuredObj, metav1.CreateOptions{})
	if createErr != nil {
		// Log detailed error and part of the YAML for better debugging
		log.Printf("Failed to create resource %s (%s) in namespace %s. Error: %v. YAML snippet: %.200s...", resourceName, gvk.Kind, namespace, createErr, yamlContent)
		if k8serrors.IsAlreadyExists(createErr) {
			return fmt.Errorf("failed to create resource %s (%s) as it already exists (deletion might not have completed or a new version appeared): %w", resourceName, gvk.Kind, createErr)
		}
		return fmt.Errorf("failed to create resource %s (%s) in namespace %s: %w", resourceName, gvk.Kind, namespace, createErr)
	}

	log.Printf("Successfully re-created resource %s (%s) in namespace %s. UID: %s", resourceName, gvk.Kind, namespace, createdObj.GetUID())
	return nil
}

func getKubernetesConfig() (*rest.Config, error) {
	log.Printf("Attempting to get Kubernetes REST config")
	var config *rest.Config
	var err error

	// Try in-cluster config first
	config, err = rest.InClusterConfig()
	if err != nil {
		log.Printf("In-cluster config failed: %v. Falling back to kubeconfig.", err)

		kubeconfigPath := os.Getenv("KUBECONFIG")
		if kubeconfigPath == "" {
			homeDir, homeErr := os.UserHomeDir()
			if homeErr != nil {
				log.Printf("Failed to get user home directory: %v", homeErr)
				// If home dir fails, BuildConfigFromFlags might still work if KUBECONFIG was empty but context is set.
			} else if homeDir != "" { // Ensure homeDir is not empty before joining
				kubeconfigPath = filepath.Join(homeDir, ".kube", "config")
			}
			log.Printf("KUBECONFIG environment variable not set, attempting default path: %s", kubeconfigPath)
		} else {
			log.Printf("Using KUBECONFIG from environment variable: %s", kubeconfigPath)
		}

		// Check if kubeconfigPath is non-empty before trying to Stat it or use it.
		if kubeconfigPath != "" {
			if _, statErr := os.Stat(kubeconfigPath); os.IsNotExist(statErr) {
				log.Printf("WARNING: Kubeconfig file does not exist at specified/default path: %s", kubeconfigPath)
				// Continue to BuildConfigFromFlags, it might handle default loading paths or in-memory contexts.
			}
		} else {
			log.Printf("WARNING: Kubeconfig path could not be determined. Will rely on client-go default behavior for BuildConfigFromFlags.")
		}

		config, err = clientcmd.BuildConfigFromFlags("", kubeconfigPath) // Pass empty masterUrl, and determined kubeconfigPath
		if err != nil {
			return nil, fmt.Errorf("failed to build config from kubeconfig path '%s': %w", kubeconfigPath, err)
		}
		log.Printf("Successfully built config from kubeconfig.")
	} else {
		log.Printf("Successfully obtained in-cluster config.")
	}

	// Log the API server we're connecting to
	log.Printf("Kubernetes API Server target: %s", config.Host)

	// Set a common timeout for client operations initiated with this config
	config.Timeout = 60 * time.Second // Increased default timeout for operations using this config

	return config, nil
}

func getKubernetesClient() (*kubernetes.Clientset, error) {
	log.Printf("Getting Kubernetes clientset")

	config, err := getKubernetesConfig()
	if err != nil {
		return nil, fmt.Errorf("failed to get kubernetes config for clientset: %w", err)
	}

	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		return nil, fmt.Errorf("failed to create kubernetes clientset: %w", err)
	}
	log.Printf("Successfully created Kubernetes clientset")

	// Test the connection by getting API resources
	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()

	// ServerVersion doesn't accept any parameters
	_, err = clientset.Discovery().ServerVersion()
	if err != nil {
		log.Printf("WARNING: Failed to get server version: %v", err)
	} else {
		log.Printf("Successfully connected to Kubernetes API server")
	}

	// Use ctx with a method that accepts context
	_, err = clientset.CoreV1().Namespaces().List(ctx, metav1.ListOptions{Limit: 1})
	if err != nil {
		log.Printf("WARNING: Failed to list namespaces: %v", err)
	}

	return clientset, nil
}

func parseTemplate(templatePath string, data interface{}, result interface{}) error {
	log.Printf("Parsing template: %s", templatePath)

	// Check if template file exists
	if _, err := os.Stat(templatePath); os.IsNotExist(err) {
		log.Printf("ERROR: Template file does not exist: %s", templatePath)
		return fmt.Errorf("template file does not exist: %w", err)
	}

	// Read template file content
	content, err := os.ReadFile(templatePath)
	if err != nil {
		return fmt.Errorf("failed to read template file: %w", err)
	}

	// Create a new template and parse
	tmpl, err := template.New(filepath.Base(templatePath)).Parse(string(content))
	if err != nil {
		return fmt.Errorf("failed to parse template %s: %w", templatePath, err)
	}

	// Create a buffer to store rendered template
	var buf bytes.Buffer
	if err := tmpl.Execute(&buf, data); err != nil {
		return fmt.Errorf("failed to execute template: %w", err)
	}

	// Log the rendered YAML for debugging
	renderedYAML := buf.String()
	log.Printf("Rendered template:\n%s", renderedYAML)

	// Decode YAML into result object using the rendered content
	if err := yaml.Unmarshal([]byte(renderedYAML), result); err != nil {
		return fmt.Errorf("failed to decode YAML: %w", err)
	}

	log.Printf("Successfully parsed template into: %+v", result)
	return nil
}

func copyTemplatesDir(tempDir string) error {
	srcDir := "templates"
	destDir := filepath.Join(tempDir, "templates")

	log.Printf("Copying templates from %s to %s", srcDir, destDir)

	// Create destination templates directory
	if err := os.MkdirAll(destDir, 0755); err != nil {
		return fmt.Errorf("failed to create templates directory in context: %w", err)
	}

	// Get list of files in the templates directory
	entries, err := os.ReadDir(srcDir)
	if err != nil {
		return fmt.Errorf("failed to read templates directory: %w", err)
	}

	// Copy each file
	for _, entry := range entries {
		if entry.IsDir() {
			log.Printf("Skipping subdirectory in templates: %s", entry.Name())
			continue
		}

		srcPath := filepath.Join(srcDir, entry.Name())
		destPath := filepath.Join(destDir, entry.Name())

		log.Printf("Copying template file: %s to %s", srcPath, destPath)

		// Read source file
		content, err := os.ReadFile(srcPath)
		if err != nil {
			log.Printf("WARNING: Failed to read template file %s: %v", srcPath, err)
			continue
		}

		// Write to destination file
		if err := os.WriteFile(destPath, content, 0644); err != nil {
			log.Printf("WARNING: Failed to write template file %s: %v", destPath, err)
			continue
		}
	}

	// List files in destination directory for verification
	entries, err = os.ReadDir(destDir)
	if err == nil {
		log.Printf("Templates directory contents after copy:")
		for _, entry := range entries {
			log.Printf("  - %s", entry.Name())
		}
	}

	log.Printf("Successfully copied templates directory to build context")
	return nil
}
