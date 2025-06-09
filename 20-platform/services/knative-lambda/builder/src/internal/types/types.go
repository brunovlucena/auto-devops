package types

// =============================================================================
// 📋 CORE DATA TYPES
// =============================================================================
// This package contains all struct definitions used across the application
// 🎯 PURPOSE: Centralize data structures for better type safety and reuse

// BuildEvent represents a request to build a new lambda function
// 🎯 PURPOSE: This is the main trigger that starts our build process
type BuildEvent struct {
	ThirdPartyId string `json:"thirdPartyId"` // Who owns this lambda (like a customer ID)
	ParserId     string `json:"parserId"`     // What type of parser to build
	ID           string `json:"id,omitempty"` // Optional unique identifier
}

// JobTemplateData holds ALL the information needed to create a Kaniko build job
// 🎯 PURPOSE: This gets passed to our job template to fill in all the blanks
type JobTemplateData struct {
	Name         string // Unique name for this specific build job
	Dockerfile   string // Which Dockerfile to use (usually just "Dockerfile")
	Context      string // Where to find the source code (S3 path)
	ImageTag     string // Full Docker image URI where result will be stored
	BucketName   string // S3 bucket for temporary build files
	ThirdPartyId string // Customer/organization identifier
	ParserId     string // Parser type identifier
	Region       string // AWS region we're operating in
	AccountId    string // AWS account ID for ECR permissions
}

// ServiceTemplateData holds info needed to create a Knative service
// 🎯 PURPOSE: After build succeeds, this creates the running service
type ServiceTemplateData struct {
	ThirdPartyId string // Customer identifier
	ParserId     string // Parser type
	Image        string // Full Docker image URI to deploy
}

// WrapperTemplateData holds info for generating wrapper.js
// 🎯 PURPOSE: Creates the Node.js wrapper that loads the actual parser
type WrapperTemplateData struct {
	ParserId string // Used to locate and load the correct parser file
}

// ResourceEventData represents Kubernetes resource status updates
// 🎯 PURPOSE: This is how we know when build jobs complete successfully
type ResourceEventData struct {
	Kind       string                 `json:"kind"`             // Type of K8s resource (Job, Pod, etc)
	Name       string                 `json:"name"`             // Name of the specific resource
	Status     map[string]interface{} `json:"status,omitempty"` // Current status info
	BuildEvent BuildEvent             `json:"buildEvent"`       // Original build request that triggered this
}

// =============================================================================
// 🔍 HELPER METHODS
// =============================================================================

// IsJobComplete checks if a Kubernetes Job has finished successfully
// 🎯 WHY: We need to know when builds finish so we can deploy the result
// 📝 HOW: Looks for a "Complete" condition with "True" status in the job
func (r *ResourceEventData) IsJobComplete() bool {
	// Quick validation - only works for Job resources
	if r.Kind != "Job" || r.Status == nil {
		return false
	}

	// Extract the conditions array from status
	// 📝 NOTE: Kubernetes stores job status as nested maps/arrays
	conditions, ok := r.Status["conditions"].([]interface{})
	if !ok {
		return false
	}

	// Look through all conditions for the "Complete" one
	// 🔍 WHAT WE'RE LOOKING FOR: type="Complete" AND status="True"
	for _, cond := range conditions {
		condition, ok := cond.(map[string]interface{})
		if !ok {
			continue
		}

		condType, typeOk := condition["type"].(string)
		status, statusOk := condition["status"].(string)

		// 🎯 SUCCESS: Found a Complete=True condition
		if typeOk && statusOk && condType == "Complete" && status == "True" {
			return true
		}
	}

	return false
}

// =============================================================================
// 📁 BUILD CONTEXT TEMPLATE CONFIGURATION
// =============================================================================

// BuildContextTemplate defines a template file to be processed for the build context
type BuildContextTemplate struct {
	SourceTplPath string                       // Relative path from project root
	TargetName    string                       // Target filename in the tempDir
	DataFunc      func(BuildEvent) interface{} // Function to get template data
}
