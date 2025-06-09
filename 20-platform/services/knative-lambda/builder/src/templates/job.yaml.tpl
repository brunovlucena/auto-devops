# Receives a CloudEvent network.notifi.lambda.build.start
apiVersion: batch/v1
kind: Job
metadata:
  name: "{{.Name}}"
  namespace: "knative-lambda"
spec:
  ttlSecondsAfterFinished: 300
  template:
    spec:
      serviceAccountName: "knative-lambda-builder"
      containers:
      - name: "kaniko"
        image: "gcr.io/kaniko-project/executor:latest"
        args:
        - "--dockerfile={{.Dockerfile}}"
        - "--context=s3://{{.BucketName}}/builds/{{.ThirdPartyId}}/{{.ParserId}}.tar.gz"
        - "--destination={{.ImageTag}}"
        - "--cache=true"
        - "--cache-ttl=24h"
        - "--use-new-run"
        - "--verbosity=debug"
        - "--log-format=text"
        - "--cleanup"
        env:
        - name: "AWS_SDK_LOAD_CONFIG"
          value: "true"
        - name: "AWS_REGION"
          value: "{{.Region}}"
        - name: "AWS_ECR_REGISTRY"
          value: "{{.AccountId}}.dkr.ecr.{{.Region}}.amazonaws.com"
        - name: "AWS_ACCESS_KEY_ID"
          valueFrom:
            secretKeyRef:
              name: "ecr-secret"
              key: "AWS_ACCESS_KEY_ID"
              optional: true
        - name: "AWS_SECRET_ACCESS_KEY"
          valueFrom:
            secretKeyRef:
              name: "ecr-secret"
              key: "AWS_SECRET_ACCESS_KEY"
              optional: true
        volumeMounts:
        - name: "aws-credentials"
          mountPath: "/kaniko/.aws"
          readOnly: true
      volumes:
      - name: "aws-credentials"
        secret:
          secretName: "ecr-secret"
          optional: true
      - name: knative-lambda-config
        configMap:
          name: knative-lambda-config
      restartPolicy: "Never"
      # nodeSelector:
      #   knative-spot: "true"
      # tolerations:
      #   - key: knative-spot
      #     operator: Equal
      #     value: "true"
      #     effect: NoSchedule