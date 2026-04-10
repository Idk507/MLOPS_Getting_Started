**Core Kubernetes Objects: Pods, ReplicaSets & Deployments, Services**  
**(Detailed Guide with YAML Examples + Hands-on Commands – Kubernetes v1.35.x, April 2026)**
1. **Pods** — The basic unit
2. **ReplicaSet** — Ensures a fixed number of Pods (self-healing)
3. **Deployment** — The recommended way to manage Pods + ReplicaSets (scaling + updates)
4. **Services** — Stable access + load balancing

**Important Rule (2026 Best Practice)**:  
Never create **naked Pods** (standalone `kind: Pod`) in real projects. Always use a **Deployment** (or StatefulSet/DaemonSet) so Kubernetes can manage scaling and self-healing for you.

### 1. Pods – The Smallest Deployable Unit

A **Pod** is the atomic unit in Kubernetes. It represents one or more tightly coupled containers that:
- Share the same IP address and port space (they can talk to each other via `localhost`).
- Share storage volumes.
- Share the same lifecycle (scheduled together, started/stopped together).

Most Pods contain **only one container**. Multi-container Pods are used for sidecar patterns (e.g., logging agent, proxy, or metrics exporter).

**Pod Characteristics**:
- Ephemeral → If a Pod dies, its IP changes.
- Has its own Pod IP (visible only inside the cluster by default).
- Defined declaratively in YAML.

#### Simple Pod YAML Example (nginx)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx          # Important for selection later
spec:
  containers:
  - name: nginx
    image: nginx:1.27-alpine   # Use specific tag (best practice)
    ports:
    - containerPort: 80
    resources:
      requests:
        cpu: "100m"       # 0.1 CPU
        memory: "128Mi"
      limits:
        cpu: "500m"
        memory: "256Mi"
    livenessProbe:          # Helps self-healing
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 5
```

**Hands-on Commands** (Run these after you have a cluster):

```bash
# 1. Create the Pod (save above as pod.yaml)
kubectl apply -f pod.yaml

# 2. Check status
kubectl get pods
kubectl get pods -o wide          # Shows IP and node

# 3. Detailed info
kubectl describe pod nginx-pod

# 4. View logs
kubectl logs nginx-pod

# 5. Exec into the Pod (like docker exec)
kubectl exec -it nginx-pod -- sh

# 6. Delete the Pod (Kubernetes will NOT recreate it automatically)
kubectl delete pod nginx-pod
```

**Important**: A standalone Pod does **not** self-heal if deleted or if the node fails. That’s why we use higher-level controllers.

### 2. ReplicaSet – Ensuring a Fixed Number of Pods

A **ReplicaSet** ensures a **specified number of identical Pods** are always running.

- If a Pod crashes or is deleted → ReplicaSet creates a new one (self-healing).
- If you scale up/down → It creates or deletes Pods.

ReplicaSet is rarely used directly today. It is the underlying mechanism managed by **Deployment**.

#### ReplicaSet YAML Example

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: nginx-rs
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:                  # Pod template
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.27-alpine
        ports:
        - containerPort: 80
```

**Hands-on**:
```bash
kubectl apply -f rs.yaml
kubectl get replicasets
kubectl get pods -l app=nginx     # See the 3 Pods managed by ReplicaSet

# Scale it
kubectl scale replicaset nginx-rs --replicas=5

# Delete one Pod manually → ReplicaSet will recreate it (self-healing demo)
kubectl delete pod <one-pod-name>
```

### 3. Deployment – The Recommended Object (Scaling + Self-Healing + Updates)

A **Deployment** is the **highest-level, production-ready** object for managing stateless apps.

- It manages **ReplicaSets**.
- Provides **declarative updates** (rolling updates, rollbacks).
- Handles scaling easily.
- When you change the image version or config → Deployment creates a new ReplicaSet and gradually replaces old Pods (zero-downtime updates).

#### Production-Ready Deployment YAML (2026 Best Practices)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 25%     # Max Pods that can be down during update
      maxSurge: 25%           # Max extra Pods that can be created
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.27-alpine
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "500m"
            memory: "256Mi"
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
```

**Hands-on Commands**:

```bash
# Create
kubectl apply -f deployment.yaml

# Check status
kubectl get deployments
kubectl get pods -l app=nginx -o wide

# Scale
kubectl scale deployment nginx-deployment --replicas=6

# Update image (triggers rolling update)
kubectl set image deployment/nginx-deployment nginx=nginx:1.27-alpine

# See rollout status
kubectl rollout status deployment/nginx-deployment

# See history & rollback if needed
kubectl rollout history deployment/nginx-deployment
kubectl rollout undo deployment/nginx-deployment

# Delete (graceful)
kubectl delete deployment nginx-deployment
```

**Self-Healing in Action**:  
Delete one Pod → Deployment/ReplicaSet will immediately create a replacement to maintain the desired replicas.

### 4. Services – Stable Access & Load Balancing

Pods have ephemeral IPs. A **Service** gives a stable virtual IP + DNS name and load-balances traffic across matching Pods.

#### Service YAML (ClusterIP – Internal)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx                  # Matches Pods with this label
  ports:
  - protocol: TCP
    port: 80                    # Service port
    targetPort: 80              # Container port
  type: ClusterIP               # Default (internal only)
```

**Hands-on**:
```bash
kubectl apply -f service.yaml

kubectl get services
kubectl get endpoints nginx-service   # Shows which Pods are backing the Service

# Test from inside cluster (run a temporary Pod)
kubectl run tmp-shell --rm -it --image=busybox -- sh
# Inside the shell: wget -qO- http://nginx-service
```

**Other Service Types**:
- **NodePort**: Exposes on every node’s IP at a high port (30000–32767) — good for testing.
- **LoadBalancer**: Provisions a real cloud load balancer (used in production on EKS/GKE/AKS).
- **ExternalName**: Maps to an external DNS name.

### Summary Table

| Object       | Purpose                              | Manages          | Self-Healing | Rolling Updates | Recommended? |
|--------------|--------------------------------------|------------------|--------------|-----------------|--------------|
| Pod          | Single instance                      | Nothing          | No           | No              | No (use with controller) |
| ReplicaSet   | Fixed number of identical Pods       | Pods             | Yes          | No              | Rarely direct |
| Deployment   | Manage app lifecycle                 | ReplicaSets      | Yes          | Yes             | **Yes** (most cases) |
| Service      | Stable access + load balancing       | Pods (via labels)| N/A          | N/A             | Yes          |

**Best Practices (2026)**:
- Always define `requests` and `limits`.
- Add meaningful `labels` and `selector`.
- Use health probes (`livenessProbe`, `readinessProbe`).
- Store all YAML in Git.
- Use `kubectl apply` (declarative) instead of imperative commands.



Tell me what you prefer, Dhanush. You're making excellent progress — these core objects are the foundation of almost everything in Kubernetes! 🚀

(When you have a cluster running, save the YAML files and run the commands above. Let me know if you hit any errors.)
