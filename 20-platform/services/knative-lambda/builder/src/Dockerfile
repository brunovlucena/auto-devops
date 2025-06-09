# =============================================================================
# 🏗️ MULTI-STAGE DOCKERFILE FOR KNATIVE-LAMBDA-BUILDER
# =============================================================================
# This Dockerfile builds the lambda builder service in two stages:
# 1. 🔨 Builder stage: Compiles the Go application
# 2. 🚀 Runtime stage: Creates minimal production image

# =============================================================================
# 📍 STAGE 1: BUILD STAGE
# =============================================================================
# 🎯 PURPOSE: Compile the Go application with all dependencies
# 💡 WHY ALPINE: Smaller base image, good for builds
# 🆕 LATEST GO: Using Go 1.23 for compatibility with go.mod requirements

FROM golang:1.23-alpine AS builder

# 🔒 SECURITY: Add ca-certificates for HTTPS requests during build
RUN apk add --no-cache ca-certificates git

# 📂 Set working directory for build
WORKDIR /build

# =============================================================================
# 🚀 DEPENDENCY OPTIMIZATION (Better Docker Layer Caching)
# =============================================================================
# 🎯 STRATEGY: Copy go.mod first to cache dependency downloads
# 💡 WHY: Dependencies change less frequently than source code


# =============================================================================
# 📁 COPY SOURCE CODE (New Package Structure)
# =============================================================================
# 🎯 PURPOSE: Copy all source code for the new refactored package structure
# 📋 NEW STRUCTURE:
#   - cmd/          (application entry points)
#   - internal/     (private application code)
#   - templates/    (YAML templates)

# Copy all source code directories
COPY cmd/       cmd/
COPY internal/  internal/
COPY templates/ templates/

# =============================================================================
# 🔧 DEPENDENCY RESOLUTION AFTER SOURCE COPY
# =============================================================================
# 🎯 PURPOSE: Ensure all imports are resolved after copying source code
# 💡 WHY: Some dependencies might only be discovered after seeing all imports

# Run go mod tidy again to resolve any new dependencies from source code
RUN cd cmd/builder && go mod tidy

# =============================================================================
# 🔨 BUILD THE APPLICATION
# =============================================================================
# 🎯 PURPOSE: Compile optimized binary for production

# Build args for better build info
ARG VERSION=dev
ARG BUILD_TIME
ARG GIT_COMMIT

# Change to the directory containing go.mod
WORKDIR /build/cmd/builder

# 🏗️ Build with optimizations:
# - CGO_ENABLED=0    : Pure Go binary (no C dependencies)
# - -a               : Force rebuilding of packages
# - -installsuffix   : Add suffix to package installation directory
# - -ldflags         : Pass information to linker
# - -w -s            : Strip debug information (smaller binary)
RUN CGO_ENABLED=0 GOOS=linux go build \
    -a -installsuffix cgo \
    -ldflags "-w -s -X main.version=${VERSION} -X main.buildTime=${BUILD_TIME} -X main.gitCommit=${GIT_COMMIT}" \
    -o lambda-builder \
    .

# 🔍 VERIFICATION: Ensure binary was created successfully
RUN ls -la lambda-builder

# =============================================================================
# 📍 STAGE 2: RUNTIME STAGE  
# =============================================================================
# 🎯 PURPOSE: Create minimal production image with just what we need
# 💡 WHY ALPINE: Smallest possible image with security updates

FROM alpine:3.19

# 🏷️ METADATA: Add labels for better container management
ARG VERSION=dev
LABEL maintainer="notifi-team" \
      description="Knative Lambda Builder Service" \
      version="${VERSION}"

# 🔒 SECURITY: Add ca-certificates and create non-root user
RUN apk --no-cache add ca-certificates tzdata wget && \
    addgroup -g 1001 -S builder && \
    adduser -u 1001 -S builder -G builder

# 📂 Set up application directory
WORKDIR /app

# 🔐 SECURITY: Change ownership to non-root user
RUN chown -R builder:builder /app

# =============================================================================
# 📁 COPY ARTIFACTS FROM BUILD STAGE
# =============================================================================
# 🎯 PURPOSE: Copy only what we need for runtime (minimal attack surface)

# Copy the compiled binary
COPY --from=builder --chown=builder:builder /build/cmd/builder/lambda-builder .

# Copy templates (needed at runtime)
COPY --from=builder --chown=builder:builder /build/templates/ templates/

# 🔍 VERIFICATION: List copied files for debugging
RUN ls -la && ls -la templates/

# =============================================================================
# 🔒 SECURITY HARDENING
# =============================================================================

# Switch to non-root user for security
USER builder

# 🌐 NETWORKING: Expose the port the application listens on
# (CloudEvents typically uses 8080)
EXPOSE 8080

# 🏥 HEALTH CHECK: Add health check for container orchestration
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# =============================================================================
# 🚀 RUNTIME CONFIGURATION
# =============================================================================

# 📋 ENVIRONMENT: Set default environment variables
ENV GO_ENV=production \
    LOG_LEVEL=info \
    PORT=8080

# 🎯 ENTRYPOINT: Use exec form for better signal handling
ENTRYPOINT ["./lambda-builder"]

# =============================================================================
# 💡 USAGE EXAMPLES
# =============================================================================
#
# 🔨 BUILD:
#   docker build -t knative-lambda-builder .
#
# 🔨 BUILD WITH ARGS:
#   docker build \
#     --build-arg VERSION=v1.0.0 \
#     --build-arg BUILD_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ) \
#     --build-arg GIT_COMMIT=$(git rev-parse HEAD) \
#     -t knative-lambda-builder:v1.0.0 .
#
# 🚀 RUN:
#   docker run -p 8080:8080 \
#     -e S3_SOURCE_BUCKET=my-bucket \
#     -e ECR_BASE_REGISTRY=123456789.dkr.ecr.us-east-1.amazonaws.com \
#     knative-lambda-builder
#
# 🧪 RUN WITH DEBUG:
#   docker run -p 8080:8080 \
#     -e LOG_LEVEL=debug \
#     knative-lambda-builder
#
# ============================================================================= 