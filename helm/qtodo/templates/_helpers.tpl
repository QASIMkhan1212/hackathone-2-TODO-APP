{{/*
============================================
Q.TODO App - Helm Template Helpers
============================================
*/}}

{{/*
Expand the name of the chart.
*/}}
{{- define "qtodo.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "qtodo.fullname" -}}
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
{{- define "qtodo.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "qtodo.labels" -}}
helm.sh/chart: {{ include "qtodo.chart" . }}
{{ include "qtodo.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "qtodo.selectorLabels" -}}
app.kubernetes.io/name: {{ include "qtodo.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Frontend labels
*/}}
{{- define "qtodo.frontend.labels" -}}
{{ include "qtodo.labels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Frontend selector labels
*/}}
{{- define "qtodo.frontend.selectorLabels" -}}
{{ include "qtodo.selectorLabels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Backend labels
*/}}
{{- define "qtodo.backend.labels" -}}
{{ include "qtodo.labels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
Backend selector labels
*/}}
{{- define "qtodo.backend.selectorLabels" -}}
{{ include "qtodo.selectorLabels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "qtodo.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "qtodo.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Frontend full name
*/}}
{{- define "qtodo.frontend.fullname" -}}
{{- printf "%s-%s" (include "qtodo.fullname" .) .Values.frontend.name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Backend full name
*/}}
{{- define "qtodo.backend.fullname" -}}
{{- printf "%s-%s" (include "qtodo.fullname" .) .Values.backend.name | trunc 63 | trimSuffix "-" }}
{{- end }}
