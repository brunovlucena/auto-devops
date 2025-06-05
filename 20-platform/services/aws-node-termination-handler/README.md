# Components

The aws-node-termination-handler (NTH) can operate in two different modes: Instance Metadata Service (IMDS) or the Queue Processor.

## Instance Metadata Service Monitor (IMDS)

## Queue Processor
The aws-node-termination-handler Queue Processor will monitor an SQS queue of events from Amazon EventBridge for:

- ASG lifecycle events, 
- EC2 status change events, 
- Spot Interruption Termination Notice events, 
- and Spot Rebalance Recommendation events.

### Permissions
Queue Processor requires AWS IAM permissions to monitor and manage the SQS queue and to query the EC2 API.