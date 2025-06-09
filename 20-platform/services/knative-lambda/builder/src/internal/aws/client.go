package aws

import (
	"context"
	"fmt"
	"time"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/ecr"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/aws/aws-sdk-go-v2/service/sts"
)

// =============================================================================
// 🔧 AWS CLIENT MANAGEMENT
// =============================================================================
// This package handles AWS SDK configuration and client creation
// 🎯 PURPOSE: Centralize AWS authentication and client management

// Client holds AWS service clients and configuration
type Client struct {
	Config    aws.Config
	ECR       *ecr.Client
	S3        *s3.Client
	STS       *sts.Client
	AccountID string
}

// NewClient creates a new AWS client with all necessary services
// 🎯 PURPOSE: Set up authenticated AWS clients for ECR, S3, and STS operations
func NewClient(ctx context.Context) (*Client, error) {
	// =========================================================================
	// 📍 STEP 1: LOAD AWS CONFIGURATION
	// =========================================================================
	// This handles various authentication methods:
	// - Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
	// - IAM roles (for EC2/EKS pods)
	// - AWS profiles (~/.aws/credentials)
	// - EKS Pod Identity (service account tokens)

	cfg, err := config.LoadDefaultConfig(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to load AWS config: %w", err)
	}

	// =========================================================================
	// 📍 STEP 2: CREATE SERVICE CLIENTS
	// =========================================================================

	ecrClient := ecr.NewFromConfig(cfg)
	s3Client := s3.NewFromConfig(cfg)
	stsClient := sts.NewFromConfig(cfg)

	// =========================================================================
	// 📍 STEP 3: GET AWS ACCOUNT ID
	// =========================================================================
	// We need this for constructing ECR registry URLs

	callerIdentity, err := stsClient.GetCallerIdentity(ctx, &sts.GetCallerIdentityInput{})
	if err != nil {
		return nil, fmt.Errorf("failed to get AWS caller identity: %w", err)
	}

	accountID := aws.ToString(callerIdentity.Account)

	return &Client{
		Config:    cfg,
		ECR:       ecrClient,
		S3:        s3Client,
		STS:       stsClient,
		AccountID: accountID,
	}, nil
}

// GetECRRegistryURL constructs the ECR registry URL for this account and region
// 🎯 PURPOSE: Build the ECR registry URL needed for Docker image tags
func (c *Client) GetECRRegistryURL() string {
	return fmt.Sprintf("%s.dkr.ecr.%s.amazonaws.com", c.AccountID, c.Config.Region)
}

// NewClientWithTimeout creates an AWS client with a specified timeout
// 🎯 PURPOSE: For operations that need custom timeout handling
func NewClientWithTimeout(timeout time.Duration) (*Client, error) {
	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()

	return NewClient(ctx)
}
