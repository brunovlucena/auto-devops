apiVersion: eventing.knative.dev/v1
kind: Trigger
metadata:
  name: lambda-{{ .ThirdPartyId }}-{{ .ParserId }}-trigger
  namespace: knative-eventing # Same namespace as the broker
spec:
  broker: service-broker
  filter:
    attributes:
      type: network.notifi.lambda.parser.start
      source: network.notifi.parsers.{{ .ThirdPartyId }}.{{ .ParserId }}
  subscriber:
    ref:
      apiVersion: serving.knative.dev/v1
      kind: Service
      name: lambda-{{ .ThirdPartyId }}-{{ .ParserId }}
      namespace: knative-lambda # Same namespace as the service
  delivery:
    retry: 5
    backoffPolicy: "exponential"
    backoffDelay: "PT1S"