**Complete End-to-End Guide: ReplicaSets → Deployments (Rollouts, Rollbacks, Updates)**  
**(Kubernetes v1.35.x – April 2026)**

This is the **natural next step** after mastering Pods. While Pods are the basic unit, **Deployments** are what you will use **95% of the time** in real projects.

---

### 1. ReplicaSet – The Foundation

A **ReplicaSet** ensures that a **specific number of identical Pods** are always running.

#### Key Responsibilities of ReplicaSet:
- Maintains the desired number of replicas (`replicas: 3`)
- Self-healing: If a Pod dies, it creates a new one
- Selector-based management: Uses labels to identify which Pods it owns

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
  template:                    # Pod template
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
kubectl get pods -l app=nginx -o wide
```

**Limitation**: ReplicaSet does **not** support rolling updates or version management. This is why we rarely use it directly.

---

### 2. Deployment – The Production Standard

A **Deployment** is a **higher-level controller** that manages ReplicaSets for you.

**What Deployment Adds**:
- Declarative updates (rolling updates)
- Rollbacks
- Revision history
- Easy scaling
- Pause/Resume updates

#### How Deployment Works (Internal Flow)

```
Deployment (Desired State)
       ↓
Creates / Manages ReplicaSet (v1, v2, v3...)
       ↓
ReplicaSet manages Pods
```

When you update the image or config, Deployment creates a **new ReplicaSet** and gradually migrates Pods from old to new.

---

### 3. Full Production Deployment YAML (2026 Best Practices)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 4
  strategy:
    type: RollingUpdate          # Default and recommended
    rollingUpdate:
      maxUnavailable: 25%        # Max pods that can be down
      maxSurge: 25%              # Max extra pods during update
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.27-alpine
        resources:
          requests:
            cpu: "150m"
            memory: "256Mi"
          limits:
            cpu: "400m"
            memory: "512Mi"
        ports:
        - containerPort: 80
        livenessProbe:
          httpGet:
            path: /
            port: 80
        readinessProbe:
          httpGet:
            path: /
            port: 80
```

---

### 4. Hands-on: Deploy, Update, Rollout & Rollback

**Step 1: Initial Deployment**

```bash
kubectl apply -f deployment.yaml
kubectl get deployments
kubectl get rs                    # Shows ReplicaSet created by Deployment
kubectl get pods -l app=nginx
```

**Step 2: Scaling**

```bash
kubectl scale deployment nginx-deployment --replicas=6

# Or edit the YAML and re-apply
kubectl apply -f deployment.yaml
```

**Step 3: Rolling Update (Change Image)**

```bash
# Method 1: Using set image (quick)
kubectl set image deployment/nginx-deployment nginx=nginx:1.27-perl

# Method 2: Edit the deployment (recommended for bigger changes)
kubectl edit deployment nginx-deployment
# Change image version and save

# Watch the rollout
kubectl rollout status deployment/nginx-deployment
```

During rollout you will see:
- New ReplicaSet created
- Old Pods gradually terminated
- New Pods started

**Step 4: Check Rollout History**

```bash
kubectl rollout history deployment/nginx-deployment
```

**Step 5: Rollback (Very Important)**

```bash
# Rollback to previous version
kubectl rollout undo deployment/nginx-deployment

# Rollback to specific revision
kubectl rollout undo deployment/nginx-deployment --to-revision=2
```

---

### 5. Update Strategies

| Strategy         | Behavior                                      | Use Case                          |
|------------------|-----------------------------------------------|-----------------------------------|
| **RollingUpdate** (Default) | Gradually replaces old Pods with new ones     | Zero-downtime updates             |
| **Recreate**     | Kills all old Pods first, then creates new    | When downtime is acceptable       |

You can configure in the `strategy` section.

---

### 6. Important Deployment Commands

```bash
# Pause a rollout (useful for canary testing)
kubectl rollout pause deployment/nginx-deployment

# Resume
kubectl rollout resume deployment/nginx-deployment

# Restart all Pods (without changing image)
kubectl rollout restart deployment/nginx-deployment

# See detailed status
kubectl describe deployment nginx-deployment
```

---

### 7. Best Practices for Deployments (2026)

1. **Always use Deployments** — never naked Pods or plain ReplicaSets.
2. Use meaningful labels and selectors.
3. Define proper `resources.requests` and `limits`.
4. Add health probes (`liveness`, `readiness`, `startup`).
5. Keep `maxUnavailable` and `maxSurge` balanced (25% is safe for most apps).
6. Use `kubectl apply` + Git for version control.
7. Monitor rollouts with `kubectl rollout status`.
8. Set revisionHistoryLimit (default 10) to control how many old ReplicaSets are kept.

---

### Summary Table: Pod → ReplicaSet → Deployment

| Object         | Manages          | Self-Healing | Rolling Updates | Rollback | Recommended Use          |
|----------------|------------------|--------------|-----------------|----------|--------------------------|
| Pod            | Nothing          | No           | No              | No       | Learning / Testing only  |
| ReplicaSet     | Pods             | Yes          | No              | No       | Rarely used directly     |
| Deployment     | ReplicaSets      | Yes          | Yes             | Yes      | **All stateless apps**   |

---

**Practice Exercise (Do This Now)**

1. Deploy the NGINX Deployment above.
2. Scale it to 5 replicas.
3. Update the image to `nginx:1.27-perl`.
4. Watch the rollout live (`kubectl get pods -w`).
5. Rollback to the previous version.
6. Try changing ConfigMap/Secret and see how to trigger a rollout.


Run the commands above on your Minikube cluster and share any observations or issues.
