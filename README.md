# butterfly

Demonstrates execution of monarch with RDMA on Ubuntu based (Nvidia PyTorch)
hosts in Kubernetes.

## Building and Deploying

### Builds

Docker images are manually built and pushed to GitHub Container Registry
(ghcr.io) since the free GHA runners aren't large enough to build the docker
images based on the nvcr images.

### Deploying to Kubernetes

Deploy the Kubernetes Job directly:
```bash
kubectl create -f pytest-rdma.yaml
```

This will create a Kubernetes Job that runs `pytest python/tests/test_rdma.py -v`
with the required GPU and RDMA resources. You can monitor the job status and logs
using kubectl commands.

For convenience, we've included `test.sh` to run these steps.
