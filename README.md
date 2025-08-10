# butterfly

Demonstrates execution of monarch with RDMA on Ubuntu based (Nvidia PyTorch)
hosts.

## Building and Deploying

### Automated Builds

Docker images are automatically built and pushed to GitHub Container Registry (ghcr.io)
when changes are pushed to the main branch. Images are available at:
- `ghcr.io/abatilo/butterfly:latest` - Latest main branch build
- `ghcr.io/abatilo/butterfly:<sha>` - Specific commit build

### Deploying to Kubernetes

Deploy the Kubernetes Job directly:
```bash
kubectl create -f pytest-rdma.yaml
```

This will create a Kubernetes Job that runs `pytest python/tests/test_rdma.py -v`
with the required GPU and RDMA resources. You can monitor the job status and logs
using kubectl commands.
