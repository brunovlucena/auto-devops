package main

import (
	"github.com/pulumi/pulumi/sdk/v3/go/pulumi"

	"fmt"
)

// pulumi up --stack local -v 3
func main() {
	pulumi.Run(func(ctx *pulumi.Context) error {
		// Get the stack name from the context
		stackName := ctx.Stack()
		ctx.Log.Info(fmt.Sprintf("Stack name: %s", stackName), nil)

		// Bootstrap Kind cluster
		if err := bootstrapKindCluster(ctx, stackName); err != nil {
			return err
		}

		// Bootstrap ArgoCD
		if err := bootstrapArgoCD(ctx, stackName); err != nil {
			return err
		}

		// Load all ArgoCD configurations (projects and applications)
		if err := createArgoCDProjects(ctx, stackName); err != nil {
			return err
		}

		// Create ArgoCD Platform applications
		if err := createArgoCDApplications(ctx, stackName); err != nil {
			return err
		}

		return nil
	})
}
