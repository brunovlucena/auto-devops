# CloudEvents Data Flow and Knative Services

## Overview

CloudEvents is a specification for describing event data in a common way, providing interoperability across services, platforms and systems. Knative Services are serverless workloads that can be triggered by these CloudEvents, creating a powerful event-driven architecture.

## Example Flow

1. A build start event(CloudEvent) (`network.notifi.lambda.build.start`) is published to RabbitMQ.
2. The Knative Service called `builder` processes this event and creates a Kubernetes job to create a Docker image using Kaniko. It contains a Dockerfile, wrapper.js and the parser.js.
3. When the job completes, an Event Exporter (Kubernetes Deployment) creates a `network.notifi.lambda.build.completed` event once the Job is completed.
4. The Knative Service called `service` component creates a Knative Service using the built image on 2.
5. The Final Knative Service called [ThirdPartyId]-[ParserId] is configured to receive `network.notifi.lambda.exec` events for execution