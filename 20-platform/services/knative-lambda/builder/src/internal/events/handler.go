package events

import (
	"context"
	"fmt"
	"log"

	cloudevents "github.com/cloudevents/sdk-go/v2"

	"knative-lambda-builder/internal/build"
	"knative-lambda-builder/internal/services"
	"knative-lambda-builder/internal/types"
)

// =============================================================================
// 🎯 CLOUDEVENTS HANDLER
// =============================================================================
// This package handles incoming CloudEvents and routes them to appropriate handlers
// 🎯 PURPOSE: Centralize event processing logic

// CloudEvent types
const (
	EventTypeBuildStart     = "network.notifi.lambda.build.start"
	EventTypeResourceUpdate = "dev.knative.apiserver.resource.update"
)

// Handler manages CloudEvent processing
type Handler struct {
	buildOrchestrator *build.Orchestrator
	parserService     *services.ParserService
	currentBuild      *types.BuildEvent // Track current build for resource events
}

// NewHandler creates a new CloudEvent handler
func NewHandler(buildOrchestrator *build.Orchestrator, parserService *services.ParserService) *Handler {
	return &Handler{
		buildOrchestrator: buildOrchestrator,
		parserService:     parserService,
	}
}

// HandleCloudEvent processes incoming CloudEvents and routes them appropriately
// 🎯 PURPOSE: Route different event types to appropriate handlers
// 📨 EVENTS WE HANDLE:
//  1. build.start -> Start a new container build
//  2. resource.update -> Handle Kubernetes job status changes
func (h *Handler) HandleCloudEvent(ctx context.Context, event cloudevents.Event) error {
	log.Printf("Received CloudEvent: %s, ID: %s", event.Type(), event.ID())
	log.Printf("CloudEvent source: %s", event.Source())
	log.Printf("CloudEvent subject: %s", event.Subject())

	// 🔍 DEBUG: Log raw event data to help troubleshoot issues
	rawData := event.Data()
	if len(rawData) > 0 {
		log.Printf("CloudEvent raw data: %s", string(rawData))
	}

	// =============================================================================
	// 📍 EVENT ROUTING: Decide what to do based on event type
	// =============================================================================

	switch event.Type() {

	// =========================================================================
	// 🚀 CASE 1: BUILD START EVENT
	// =========================================================================
	case EventTypeBuildStart:
		return h.handleBuildStart(ctx, event)

	// =========================================================================
	// 📊 CASE 2: RESOURCE UPDATE EVENT
	// =========================================================================
	case EventTypeResourceUpdate:
		return h.handleResourceUpdate(ctx, event)

	// =========================================================================
	// ❓ CASE 3: UNKNOWN EVENT TYPE
	// =========================================================================
	default:
		log.Printf("Received unknown event type: %s", event.Type())
		return nil // Don't fail on unknown events
	}
}

// handleBuildStart processes build start events
func (h *Handler) handleBuildStart(ctx context.Context, event cloudevents.Event) error {
	log.Printf("Processing build start event")

	var buildEvent types.BuildEvent
	if err := event.DataAs(&buildEvent); err != nil {
		log.Printf("ERROR: Failed to parse build event: %v", err)
		return fmt.Errorf("failed to parse build event: %w", err)
	}

	log.Printf("Successfully parsed build event: %+v", buildEvent)

	// Store current build for resource update events
	h.currentBuild = &buildEvent

	// 🏃‍♂️ Start build process in background (don't block event handler)
	// WHY BACKGROUND: Event handlers should respond quickly
	go func(be types.BuildEvent) {
		if err := h.buildOrchestrator.CreateKanikoJob(ctx, be); err != nil {
			log.Printf("ERROR: Background job creation failed: %v", err)
		}
	}(buildEvent)

	return nil
}

// handleResourceUpdate processes Kubernetes resource update events
func (h *Handler) handleResourceUpdate(ctx context.Context, event cloudevents.Event) error {
	log.Printf("Processing resource update event")

	var resourceEvent types.ResourceEventData

	// 🔍 DEBUG: Log raw event data for troubleshooting
	log.Printf("Raw event data: %s", string(event.Data()))

	// 📥 Try to parse the event data
	if err := event.DataAs(&resourceEvent); err != nil {
		log.Printf("ERROR: Failed to parse resource event: %v", err)
		// 🤷‍♂️ Don't return error - just log and continue (non-critical)
		return nil
	}

	log.Printf("Received resource event: Kind=%s, Name=%s",
		resourceEvent.Kind, resourceEvent.Name)

	// 🔍 DEBUG: Log detailed status information
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

	// 🎯 THE IMPORTANT PART: Check if a build job completed successfully
	if resourceEvent.Kind == "Job" && resourceEvent.IsJobComplete() {
		log.Printf("Job completed, creating parser service")

		// Use current build info if available, otherwise try from event
		buildEvent := h.currentBuild
		if buildEvent == nil {
			buildEvent = &resourceEvent.BuildEvent
		}

		log.Printf("Creating parser service for ThirdPartyId=%s, ParserId=%s",
			buildEvent.ThirdPartyId, buildEvent.ParserId)

		// 🏃‍♂️ Create service in background (don't block event handler)
		go func(be *types.BuildEvent) {
			if err := h.parserService.CreateParserService(ctx, *be); err != nil {
				log.Printf("ERROR: Background parser service creation failed: %v", err)
			}
		}(buildEvent)
	}

	return nil
}
