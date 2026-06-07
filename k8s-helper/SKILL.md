---
name: k8s-helper
description: Utility for managing Kubernetes pods and logs for the OrderService project. Use this when the user asks for logs, pod status, or to investigate crashes in the student-lotarlmen-order-service namespace.
---

# Kubernetes Helper

This skill automates interaction with the project's Kubernetes cluster using the fixed kubeconfig at `C:\Users\VALERIY\.kube\order-service`.

## Usage

### Get Logs
To get the last 100 lines of logs for the order service pod:
```bash
python scripts/k8s_ops.py logs order
```

### List Pods
To see the status of all pods in the namespace:
```bash
python scripts/k8s_ops.py pods
```

## Configuration
- **KUBECONFIG**: `C:\Users\VALERIY\.kube\order-service`
- **Namespace**: `student-lotarlmen-order-service`
- **Context**: `student-lotarlmen-order-service-context`

The skill automatically handles context and namespace selection.
