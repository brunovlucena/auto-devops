package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"

	"github.com/pulumi/pulumi/sdk/v3/go/pulumi"
)

// applyKubectlCommand executes a kubectl command with the given arguments
func applyKubectlCommand(ctx *pulumi.Context, args ...string) error {
	if ctx == nil {
		return fmt.Errorf("pulumi context cannot be nil")
	}

	cmd := exec.Command("kubectl", args...)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	if err := cmd.Run(); err != nil {
		return fmt.Errorf("failed to execute kubectl command: %v", err)
	}

	return nil
}

func bootstrapArgoCD(ctx *pulumi.Context, stackName string) error {
	ctx.Log.Info(fmt.Sprintf("bootstrapArgoCD: %s", stackName), nil)
	// Create argocd namespace if it doesn't exist
	ctx.Log.Info("Creating ArgoCD namespace...", nil)
	createNsCmd := exec.Command("sh", "-c", "kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -")
	createNsCmd.Stdout = os.Stdout
	createNsCmd.Stderr = os.Stderr
	if err := createNsCmd.Run(); err != nil {
		return fmt.Errorf("failed to create argocd namespace: %v", err)
	}

	// Install ArgoCD
	ctx.Log.Info("Installing ArgoCD...", nil)
	if err := applyKubectlCommand(ctx, "apply", "-n", "argocd", "-f", "https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml"); err != nil {
		return fmt.Errorf("failed to install ArgoCD: %v", err)
	}

	// Wait for ArgoCD server to be ready
	ctx.Log.Info("Waiting for ArgoCD server to be ready...", nil)
	if err := applyKubectlCommand(ctx, "wait", "--for=condition=available", "--timeout=300s", "deployment/argocd-server", "-n", "argocd"); err != nil {
		return fmt.Errorf("failed to wait for ArgoCD server: %v", err)
	}

	// Get the initial admin password
	ctx.Log.Info("Getting initial admin password...", nil)
	passwordCmd := exec.Command("sh", "-c", "kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath={.data.password} | base64 -d")
	passwordOutput, err := passwordCmd.CombinedOutput()
	if err != nil {
		return fmt.Errorf("failed to get initial admin password: %v", err)
	}

	// Log the password securely (only in logs, not in output)
	ctx.Log.Info(fmt.Sprintf("Initial admin password: %s", string(passwordOutput)), nil)

	// Also output the password to stdout for user convenience
	fmt.Printf("Initial ArgoCD admin password: %s\n", string(passwordOutput))

	return nil
}

func createArgoCDProjects(ctx *pulumi.Context, stage string) error {
	// Get the current directory
	currentDir, err := os.Getwd()
	if err != nil {
		return fmt.Errorf("failed to get current directory: %v", err)
	}

	// Path to the ArgoCD project YAML files - go up one level from current directory
	repoRoot := filepath.Dir(currentDir)
	projectsDir := filepath.Join(repoRoot, "20-platform", "argocd", "config", stage, "projects")

	// List of project YAML files to apply
	projectFiles := []string{}

	// Walk the projects directory and add all YAML files
	err = filepath.Walk(projectsDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !info.IsDir() && (filepath.Ext(path) == ".yaml" || filepath.Ext(path) == ".yml") {
			projectFiles = append(projectFiles, path)
		}
		return nil
	})

	if err != nil {
		ctx.Log.Warn(fmt.Sprintf("Failed to walk projects directory: %v", err), nil)
	}

	// Apply each project YAML file
	for _, file := range projectFiles {
		ctx.Log.Info(fmt.Sprintf("Applying ArgoCD project from %s", file), nil)

		cmd := exec.Command("kubectl", "apply", "-f", file)
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		if err := cmd.Run(); err != nil {
			return fmt.Errorf("failed to apply ArgoCD project from %s: %v", file, err)
		}
	}

	return nil
}

func createArgoCDApplications(ctx *pulumi.Context, stage string) error {
	// Get the current directory
	currentDir, err := os.Getwd()
	if err != nil {
		return fmt.Errorf("failed to get current directory: %v", err)
	}

	// Path to the ArgoCD application YAML files - go up one level from current directory
	repoRoot := filepath.Dir(currentDir)
	applicationsetsDir := filepath.Join(repoRoot, "20-platform", "argocd", "config", stage, "applicationsets")

	// List of application YAML files to apply
	applicationFiles := []string{}

	// Walk the applicationsets directory and add all YAML files
	err = filepath.Walk(applicationsetsDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if !info.IsDir() && (filepath.Ext(path) == ".yaml" || filepath.Ext(path) == ".yml") {
			applicationFiles = append(applicationFiles, path)
		}
		return nil
	})

	if err != nil {
		ctx.Log.Warn(fmt.Sprintf("Failed to walk applicationsets directory: %v", err), nil)
	}

	// Apply each application YAML file
	for _, file := range applicationFiles {
		ctx.Log.Info(fmt.Sprintf("Applying ArgoCD application from %s", file), nil)

		cmd := exec.Command("kubectl", "apply", "-f", file)
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		if err := cmd.Run(); err != nil {
			return fmt.Errorf("failed to apply ArgoCD application from %s: %v", file, err)
		}
	}

	return nil
}
