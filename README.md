# butterfly

Demonstrates execution of monarch with RDMA on Ubuntu based (Nvidia PyTorch)
hosts.

## Building and Deploying

### Automated Builds

Docker images are automatically built and pushed to GitHub Container Registry (ghcr.io)
when changes are pushed to the main branch. Images are available at:
- `ghcr.io/<owner>/butterfly:latest` - Latest main branch build
- `ghcr.io/<owner>/butterfly:<sha>` - Specific commit build

### Deploying to Kubernetes

1. Set the image URI environment variable (replace `<owner>` with your GitHub username/org):
```bash
# For latest image
export IMAGE_URI="ghcr.io/<owner>/butterfly:latest"

# Or for a specific commit
export IMAGE_URI="ghcr.io/<owner>/butterfly:<commit-sha>"
```

2. Deploy the Kubernetes Job using envsubst:
```bash
envsubst < pytest-rdma.yaml | kubectl create -f -
```

This will create a Kubernetes Job that runs `pytest python/tests/test_rdma.py -v`
with the required GPU and RDMA resources. You can monitor the job status and logs
using kubectl commands.
