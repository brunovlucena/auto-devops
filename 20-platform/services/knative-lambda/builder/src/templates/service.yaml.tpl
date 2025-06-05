# Create parser services.serving.knative.dev
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: lambda-{{.ThirdPartyId}}-{{.ParserId}}
  namespace: knative-lambda
spec:
  template:
    spec:
      containers:
        - image: {{.Image}}
      tolerations:
        - key: knative-spot
          operator: Equal
          value: "true"
          effect: NoSchedule
      nodeSelector:
        knative-spot: "true"