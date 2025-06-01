package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/pulumi/pulumi/sdk/v3/go/pulumi"
)

func bootstrapKindCluster(ctx *pulumi.Context, stackName string) error {
	ctx.Log.Info(fmt.Sprintf("bootstrapKindCluster: %s", stackName), nil)
	// Get the current directory
	currentDir, err := os.Getwd()
	if err != nil {
		return fmt.Errorf("failed to get current directory: %v", err)
	}

	// Path to the kind config file
	kindConfigPath := filepath.Join(currentDir, "kind-config.yaml")

	// Check if the config file exists
	if _, err := os.Stat(kindConfigPath); os.IsNotExist(err) {
		return fmt.Errorf("kind config file not found at %s", kindConfigPath)
	}

	// Check if kind is installed
	kindPath, err := exec.LookPath("kind")
	if err != nil {
		return fmt.Errorf("kind is not installed: %v", err)
	}
	ctx.Log.Info(fmt.Sprintf("Using kind at: %s", kindPath), nil)

	// Check if the cluster already exists
	clusterName := "auto-devops"

	// Get the existing clusters
	checkCmd := exec.Command("kind", "get", "clusters")
	output, err := checkCmd.CombinedOutput()
	if err != nil {
		return fmt.Errorf("failed to check existing clusters: %v, output: %s", err, string(output))
	}

	// Check if our cluster already exists
	clusters := strings.Split(strings.TrimSpace(string(output)), "\n")
	exists := false
	for _, name := range clusters {
		if strings.TrimSpace(name) == clusterName {
			exists = true
			break
		}
	}

	if exists {
		ctx.Log.Info(fmt.Sprintf("Cluster '%s' already exists, skipping creation", clusterName), nil)
		return nil
	}

	// Create the cluster
	ctx.Log.Info("Creating Kind cluster...", nil)
	createCmd := exec.Command("kind", "create", "cluster", "--config", kindConfigPath)
	createCmd.Stdout = os.Stdout
	createCmd.Stderr = os.Stderr

	if err := createCmd.Run(); err != nil {
		return fmt.Errorf("failed to create Kind cluster: %v", err)
	}

	ctx.Log.Info("Kind cluster created successfully", nil)
	return nil
}
