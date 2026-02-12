# Deployment Guide

**Target:** Yandex Cloud  
**Orchestration:** Kubernetes  
**CI/CD:** GitHub Actions

## Prerequisites

```bash
# Install tools
brew install yc kubectl helm terraform

# Login to Yandex Cloud
yc init

# Configure kubectl
yc managed-kubernetes cluster get-credentials algo-cluster --external
```

## Quick Deploy (Development)

```bash
# 1. Set environment
export YC_TOKEN=$(yc iam create-token)
export YC_CLOUD_ID=$(yc config get cloud-id)
export YC_FOLDER_ID=$(yc config get folder-id)

# 2. Run Terraform
cd infra/terraform
terraform init
terraform apply

# 3. Deploy services
cd ../kubernetes
kubectl apply -f namespaces/
kubectl apply -f secrets/
kubectl apply -f deployments/
kubectl apply -f services/
kubectl apply -f ingress/

# 4. Verify
kubectl get pods -n production
kubectl get svc -n production
```

## Production Deploy

```bash
# Use GitHub Actions
git push origin main

# Monitor deployment
kubectl rollout status deployment/company-service -n production
```

## Rollback

```bash
kubectl rollout undo deployment/company-service -n production
```

**Full Guide:** See detailed steps in `infra/DEPLOY_GUIDE.md`
