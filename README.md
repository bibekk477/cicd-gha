# Flask CI/CD Pipeline with GitHub Actions, ArgoCD & Kubernetes

A complete CI/CD pipeline that automates the deployment of a Flask application on **Minikube** using **GitHub Actions**, **Docker Hub**, **ArgoCD**, and **Kubernetes**.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Setup & Configuration](#setup--configuration)
  - [1. GitHub Repository Settings](#1-github-repository-settings)
  - [2. GitHub Secrets](#2-github-secrets)
  - [3. Minikube & Kubernetes Setup](#3-minikube--kubernetes-setup)
  - [4. ArgoCD Installation](#4-argocd-installation)
  - [5. ArgoCD Application Setup](#5-argocd-application-setup)
  - [6. Docker Image Pull Secret](#6-docker-image-pull-secret)
- [Pipeline Walkthrough](#pipeline-walkthrough)
- [Accessing the Application](#accessing-the-application)
- [Troubleshooting](#troubleshooting)

---

## Overview

This CI/CD pipeline automates the end-to-end deployment of a Flask application. On every push to the `main` branch, GitHub Actions builds a Docker image tagged with the short commit SHA, pushes it to Docker Hub, updates the Kubernetes deployment manifest using `yq`, and commits the change back to the repository. ArgoCD then detects the manifest update and syncs the deployment to the Minikube cluster automatically.

---

## Architecture

```
Developer Push (main)
        │
        ▼
  GitHub Actions
  ┌─────────────────────────────────┐
  │ 1. Checkout code                │
  │ 2. Extract short SHA            │
  │ 3. Docker Hub login             │
  │ 4. Build & tag Docker image     │
  │ 5. Push image to Docker Hub     │
  │ 6. Install yq                   │
  │ 7. Update k8s/deployment.yaml   │
  │ 8. Commit & push manifest       │
  └─────────────────────────────────┘
        │
        ▼
   GitHub Repo (updated manifest)
        │
        ▼
     ArgoCD (running in Minikube)
        │  Detects manifest change
        ▼
   Kubernetes (Minikube)
        │  Pulls new image & deploys
        ▼
   Flask App Running Live 🚀
```

---

## Tech Stack

| Tool | Purpose |
|---|---|
| **GitHub Actions** | CI — build, tag, push image, update manifest |
| **Docker Hub** | Container image registry |
| **yq** | YAML manipulation to update deployment manifest |
| **ArgoCD** | CD — GitOps-based sync to Kubernetes |
| **Kubernetes (Minikube)** | Container orchestration |
| **Flask** | Python web application framework |

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed locally
- [Minikube](https://minikube.sigs.k8s.io/docs/start/) installed and running locally
- [kubectl](https://kubernetes.io/docs/tasks/tools/) configured for your cluster
- A [Docker Hub](https://hub.docker.com/) account
- A GitHub repository with this project

---

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── pipeline.yaml          # GitHub Actions pipeline
├── k8s/
│   ├── deployment.yaml        # Kubernetes Deployment manifest
│   └── service.yaml           # Kubernetes Service manifest
├── templates/
│   └── index.html             # Flask HTML template
├── app.py                     # Flask application
├── Dockerfile                 # Docker image definition
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

---

## Setup & Configuration

### 1. GitHub Repository Settings

To allow the GitHub Actions workflow to commit the updated deployment manifest back to the repository, you must enable **read and write permissions** for workflows:

1. Go to your repository on GitHub
2. Navigate to **Settings → Actions → General**
3. Scroll to **Workflow permissions**
4. Select **Read and write permissions**
5. Click **Save**

> ⚠️ Without this, the `git push` step in the pipeline will fail with a permissions error.

---

### 2. GitHub Secrets

Add the following secrets to your repository under **Settings → Secrets and variables → Actions**:

| Secret Name | Description |
|---|---|
| `DOCKER_USERNAME` | Your Docker Hub username |
| `DOCKER_PASSWORD` | Your Docker Hub password or access token |

---

### 3. Minikube & Kubernetes Setup

Start Minikube and create the required namespaces:

```bash
# Start Minikube
minikube start

# Create namespace for the Flask app (used by ArgoCD for deployment)
kubectl create namespace flask-app
```

---

### 4. ArgoCD Installation

ArgoCD runs inside the Kubernetes cluster itself.

```bash
# Create the ArgoCD namespace
kubectl create namespace argocd

# Install ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for all pods to be ready
kubectl get pods -n argocd -w
```

**Expose the ArgoCD UI:**

```bash
# Option 1: Edit the service type to LoadBalancer
kubectl edit svc argocd-server -n argocd
# Change `type: ClusterIP` to `type: LoadBalancer`

# Option 2: Use Minikube service tunnel (recommended for local dev)
minikube service argocd-server -n argocd
```

**Retrieve the initial admin password:**

```bash
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d
```

Login at the ArgoCD UI with username `admin` and the password retrieved above.

---

### 5. ArgoCD Application Setup

In the ArgoCD UI (or via CLI), create an application pointing to your GitHub repository:

- **Application Name:** `gha-flaskapp`
- **Project:** `default`
- **Sync Policy:** Automatic
- **Repository URL:** your GitHub repo URL
- **Path:** `k8s/`
- **Cluster:** `https://kubernetes.default.svc`
- **Namespace:** `flask-app`

ArgoCD will now watch the `k8s/` directory and auto-sync whenever the deployment manifest changes.

---

### 6. Docker Image Pull Secret

Since the Docker image may be in a private Docker Hub repository, create an image pull secret in the `flask-app` namespace so Kubernetes can authenticate when pulling the image:

```bash
kubectl create secret docker-registry image-pull-secret \
  --docker-username=YOUR_USERNAME \
  --docker-password=YOUR_ACCESS_TOKEN \
  --docker-email=YOUR_EMAIL \
  -n flask-app
```

> This secret is referenced in `k8s/deployment.yaml` under `imagePullSecrets`.

---

## Pipeline Walkthrough

When you push code to the `main` branch, the following steps execute automatically:

| Step | Action |
|---|---|
| **1. Checkout** | Clones the repository |
| **2. Short SHA** | Extracts the first 5 characters of the commit SHA for image tagging |
| **3. Docker Login** | Authenticates with Docker Hub using stored secrets |
| **4. Build Image** | Builds `bibekk477/gha-argocd-k8s-pipeline:<SHORT_SHA>` |
| **5. Push Image** | Pushes the tagged image to Docker Hub |
| **6. Install yq** | Installs `yq` for YAML manipulation |
| **7. Update Manifest** | Updates `k8s/deployment.yaml` with the new image tag |
| **8. Commit & Push** | Commits the updated manifest back to `main` |
| **ArgoCD Sync** | Detects the manifest change and deploys the new image to Minikube |

---

## Accessing the Application

Once deployed, access the Flask app via Minikube:

```bash
minikube service my-flaskapp-service -n flask-app
```

This opens the app in your browser. The dashboard displays the current CI/CD pipeline status for all stages.

---

## Troubleshooting

**ArgoCD not syncing / application not found:**

```bash
# List all ArgoCD applications
kubectl get applications -n argocd

# Describe the application for detailed status and errors
kubectl describe application gha-flaskapp -n argocd
```

**Pods failing to pull image (ImagePullBackOff):**

Ensure the `image-pull-secret` exists in the `flask-app` namespace:

```bash
kubectl get secrets -n flask-app
```

If missing, recreate it using the command in [step 6](#6-docker-image-pull-secret).

**GitHub Actions push failing (403 / permission denied):**

Ensure **Read and write permissions** are enabled for workflows under **Settings → Actions → General** in your repository.

**ArgoCD UI not accessible:**

```bash
# Check if ArgoCD pods are running
kubectl get pods -n argocd

# Re-expose via Minikube
minikube service argocd-server -n argocd
```

**Check pod logs for any application errors:**

```bash
kubectl logs -n flask-app deployment/my-flaskapp-deployment
```

---