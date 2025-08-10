#!/bin/bash
set -e

echo "Creating Kubernetes Job..."
JOB_NAME=$(kubectl create -f pytest-rdma.yaml -o jsonpath='{.metadata.name}')
echo "Created job: $JOB_NAME"

echo "Waiting for job to complete..."
kubectl wait --for=condition=complete --timeout=600s job/"$JOB_NAME" 2>/dev/null ||
  kubectl wait --for=condition=failed --timeout=600s job/"$JOB_NAME" 2>/dev/null || true

echo "Fetching logs..."
kubectl logs job/"$JOB_NAME"

# Check job status
if kubectl get job/"$JOB_NAME" -o jsonpath='{.status.succeeded}' | grep -q "1"; then
  echo "Tests passed!"
else
  echo "Tests failed!"
  exit 1
fi
