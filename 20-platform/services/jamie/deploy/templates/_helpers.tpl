{{/*
Expand the name of the chart.
*/}}
{{- define "jamie.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "jamie.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "jamie.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "jamie.labels" -}}
helm.sh/chart: {{ include "jamie.chart" . }}
{{ include "jamie.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "jamie.selectorLabels" -}}
app.kubernetes.io/name: {{ include "jamie.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "jamie.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "jamie.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Generate fullname for ollama
*/}}
{{- define "jamie.ollama.fullname" -}}
{{- printf "%s-ollama" (include "jamie.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Generate fullname for mongodb
*/}}
{{- define "jamie.mongodb.fullname" -}}
{{- printf "%s-mongodb" (include "jamie.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Generate fullname for redis
*/}}
{{- define "jamie.redis.fullname" -}}
{{- printf "%s-redis" (include "jamie.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Generate fullname for tempo
*/}}
{{- define "jamie.tempo.fullname" -}}
{{- printf "%s-tempo" (include "jamie.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Generate MongoDB connection URL
*/}}
{{- define "jamie.mongodb.url" -}}
{{- if .Values.mongodb.enabled }}
{{- printf "mongodb://%s:%s@%s:%d/%s" .Values.mongodb.auth.rootUsername .Values.mongodb.auth.rootPassword (include "jamie.mongodb.fullname" .) (.Values.mongodb.service.port | int) .Values.mongodb.auth.database }}
{{- else }}
{{- .Values.externalMongodb.url }}
{{- end }}
{{- end }}

{{/*
Generate Redis URL
*/}}
{{- define "jamie.redis.url" -}}
{{- if .Values.redis.enabled }}
{{- printf "redis://%s:%d" (include "jamie.redis.fullname" .) (.Values.redis.service.port | int) }}
{{- else }}
{{- .Values.externalRedis.url }}
{{- end }}
{{- end }}

{{/*
Generate Ollama URL
*/}}
{{- define "jamie.ollama.url" -}}
{{- if .Values.ollama.enabled }}
{{- printf "http://%s:%d" (include "jamie.ollama.fullname" .) (.Values.ollama.service.port | int) }}
{{- else }}
{{- .Values.externalOllama.url }}
{{- end }}
{{- end }}

{{/*
Generate Tempo OTLP endpoint
*/}}
{{- define "jamie.tempo.endpoint" -}}
{{- if .Values.tempo.enabled }}
{{- printf "http://%s:%d" (include "jamie.tempo.fullname" .) (.Values.tempo.service.ports.otlp-grpc | int) }}
{{- else }}
{{- .Values.externalTempo.endpoint }}
{{- end }}
{{- end }} 