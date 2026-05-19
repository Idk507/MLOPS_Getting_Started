**Complete End-to-End Guide to Kubernetes DaemonSets**  
**(Kubernetes v1.35.x – April 2026)**

### 1. What is a DaemonSet?

A **DaemonSet** is a Kubernetes **workload controller** that ensures **exactly one Pod runs on every node** (or a selected subset of nodes) in the cluster.

- If a new node joins the cluster → DaemonSet automatically creates a Pod on it.
- If a node is removed → The Pod is garbage collected.
- It is designed for **node-level** background services that need to run on **all (or most)** nodes.

**Key Difference from other controllers**:
- **Deployment** → Runs a specified number of Pods (distributed across nodes).
- **StatefulSet** → Runs a fixed number of Pods with stable identity.
- **DaemonSet** → Runs **one Pod per node** (node-scoped).

---

### 2. When to Use DaemonSets? (Real-World Use Cases)

**Common Use Cases**:

| Category              | Examples                                      | Why DaemonSet? |
|-----------------------|-----------------------------------------------|----------------|
| **Logging**           | Fluentd, Filebeat, Vector                     | Collect logs from every node |
| **Monitoring**        | Prometheus Node Exporter, Datadog Agent       | Collect node metrics |
| **Networking**        | Calico, Cilium, Flannel, kube-proxy          | Provide cluster networking |
| **Security**          | Falco, Sysdig, Aqua Security                  | Runtime security & auditing |
| **Storage**           | CSI Node Driver (e.g., AWS EBS CSI)           | Mount storage on nodes |
| **Cluster Utilities** | kubelet (indirectly), node-problem-detector   | Node maintenance |

**Rule of Thumb**:  
Use DaemonSet when your Pod must run **on every node** to provide a **node-local service**.

---

### 3. DaemonSet vs Other Controllers (Full Comparison)

| Feature                    | Deployment          | StatefulSet           | DaemonSet                  |
|---------------------------|---------------------|-----------------------|----------------------------|
| Number of Pods             | Fixed / Autoscaled  | Fixed                 | One per Node               |
| Pod Identity               | Random              | Stable (ordinal)      | Node name based            |
| Scheduling                 | Any nodes           | Any nodes             | Every matching node        |
| Storage                    | Shared              | Per-Pod PVC           | Usually hostPath / emptyDir |
| Scaling                    | Manual / HPA        | Manual                | Automatic with nodes       |
| Update Strategy            | RollingUpdate       | RollingUpdate         | RollingUpdate / OnDelete   |
| Use Case                   | Stateless apps      | Databases             | Node agents & daemons      |

---

### 4. Complete DaemonSet YAML (Production Ready)

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd-daemon
  namespace: kube-system
  labels:
    app: fluentd
spec:
  selector:
    matchLabels:
      app: fluentd

  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1          # Max pods that can be unavailable during update

  template:
    metadata:
      labels:
        app: fluentd
    spec:
      tolerations:                 # Critical for running on control-plane nodes
      - key: node-role.kubernetes.io/control-plane
        operator: Exists
        effect: NoSchedule

      containers:
      - name: fluentd
        image: fluent/fluentd:v1.17-debian
        resources:
          requests:
            cpu: "100m"
            memory: "300Mi"
          limits:
            cpu: "500m"
            memory: "600Mi"

        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true

      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers

      # Optional: Run only on specific nodes
      # nodeSelector:
      #   disktype: ssd
```

---

### 5. Key Fields Explained

- **`selector`**: Must match the `template.metadata.labels`.
- **`template`**: The Pod template (same as in Deployment).
- **`updateStrategy`**:
  - `RollingUpdate` (default) — Updates Pods gradually.
  - `OnDelete` — Only updates when you manually delete the old Pod.
- **`tolerations`**: Allows the DaemonSet to run on **tainted nodes** (e.g., control-plane nodes).
- **`nodeSelector` / `affinity`**: Restrict which nodes get the DaemonSet Pod.
- **`volumes` using `hostPath`**: Frequently used to access node filesystem.

---

### 6. Hands-on Commands

```bash
# Create DaemonSet
kubectl apply -f fluentd-daemonset.yaml

# Check status
kubectl get daemonsets -n kube-system

# See which nodes are running the Pods
kubectl get pods -l app=fluentd -o wide

# Describe a DaemonSet
kubectl describe daemonset fluentd-daemon -n kube-system

# View logs
kubectl logs -f <pod-name> -n kube-system
```

**Check DaemonSet Status**:
```bash
kubectl get ds fluentd-daemon -o wide
# Shows DESIRED, CURRENT, READY, UP-TO-DATE, AVAILABLE
```

---

### 7. Updating DaemonSets

```bash
# Update container image
kubectl set image daemonset/fluentd-daemon fluentd=fluent/fluentd:v1.18-debian

# Monitor rollout
kubectl rollout status daemonset/fluentd-daemon -n kube-system

# Rollback
kubectl rollout undo daemonset/fluentd-daemon -n kube-system
```

---

### 8. Advanced Features

- **Node Affinity / Anti-Affinity**: Schedule based on node labels.
- **Tolerations**: Bypass taints.
- **Pod Disruption Budget (PDB)**: Protect DaemonSet Pods during node drain.
- **MaxUnavailable**: Control how many nodes can be updated simultaneously.
- **Revision History**: Keeps track of previous versions.

---

### 9. Best Practices (2026)

1. Keep DaemonSet Pods **lightweight** (low resource usage).
2. Always add proper `requests` and `limits`.
3. Use `hostPath` carefully (security risk).
4. Add health probes (`livenessProbe`, `readinessProbe`).
5. Use `tolerations` to run on control-plane nodes when needed.
6. Prefer **DaemonSet** over `hostNetwork: true` when possible.
7. Monitor DaemonSet Pods with Prometheus.
8. Use `OnDelete` strategy for critical agents during upgrades.

---

### 10. Common Issues & Troubleshooting

| Issue                        | Solution |
|-----------------------------|----------|
| Pods not getting created     | Check node taints & tolerations |
| Pods in Pending state        | Check resource limits or StorageClass |
| DaemonSet not updating       | Use `OnDelete` strategy or delete old Pods |
| High resource usage          | Tune requests/limits |
| Security concerns            | Use `securityContext` + read-only volumes |

**Useful Debug Commands**:
```bash
kubectl get nodes
kubectl describe node <node-name> | grep -i taint
kubectl get events --sort-by=.metadata.creationTimestamp
```

---

### 11. Real-World Examples

- **kube-proxy** → Runs as DaemonSet on every node.
- **Calico / Cilium** → Networking DaemonSets.
- **Node Exporter** → Prometheus metrics.
- **Logs collectors** → Fluent Bit / Vector.

---

**Summary Table**

| Aspect                  | Details |
|------------------------|--------|
| Purpose                | Run one Pod per node |
| Identity               | Tied to node |
| Scaling                | Automatic with cluster size |
| Storage                | Usually `hostPath` |
| Best For               | Logging, monitoring, networking, security agents |

---

You have now covered **all major workload types** in Kubernetes:
- Pods
- Deployments
- StatefulSets
- **DaemonSets**

------------------------

**Hands-on Lab: Real-World Combination of Deployment + StatefulSet + DaemonSet**  
**(Kubernetes v1.35 – Complete Practical Lab)**

---

### **Lab Objective**

Build a **mini production-like stack** that uses all three major workload types together:

- **Deployment** → Frontend (Nginx)
- **StatefulSet** → Database (PostgreSQL)
- **DaemonSet** → Logging Agent (Fluent Bit)

You will also use **ConfigMap**, **Secret**, **PVC**, **Services**, and basic **Networking**.

---

### **Step 0: Preparation**

```bash
# 1. Create a dedicated namespace
kubectl create namespace fullstack-lab
kubectl config set-context --current --namespace=fullstack-lab

# 2. Enable required Minikube addons
minikube addons enable ingress
minikube addons enable metrics-server
```

---

### **Step 1: Create ConfigMap & Secret**

**01-config.yaml**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  APP_ENV: production
  LOG_LEVEL: info

---
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  POSTGRES_PASSWORD: cG9zdGdyZXMxMjM=   # base64 of "postgres123"
```

Apply:
```bash
kubectl apply -f 01-config.yaml
```

---

### **Step 2: StatefulSet – PostgreSQL Database**

**02-postgres-statefulset.yaml**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:17-alpine
        env:
        - name: POSTGRES_USER
          value: postgres
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: POSTGRES_PASSWORD
        - name: POSTGRES_DB
          value: myapp
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 2Gi
```

Apply:
```bash
kubectl apply -f 02-postgres-statefulset.yaml
```

---

### **Step 3: Deployment – Frontend (Nginx)**

**03-frontend-deployment.yaml**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: nginx
        image: nginx:1.27-alpine
        ports:
        - containerPort: 80
        envFrom:
        - configMapRef:
            name: app-config
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "300m"
            memory: "256Mi"
```

**Service for Frontend**
```yaml
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 80
  type: NodePort
```

Apply:
```bash
kubectl apply -f 03-frontend-deployment.yaml
```

---

### **Step 4: DaemonSet – Logging Agent (Fluent Bit)**

**04-fluentbit-daemonset.yaml**
```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentbit
spec:
  selector:
    matchLabels:
      app: fluentbit
  template:
    metadata:
      labels:
        app: fluentbit
    spec:
      tolerations:
      - operator: Exists
        effect: NoSchedule

      containers:
      - name: fluentbit
        image: fluent/fluent-bit:3.2
        resources:
          requests:
            cpu: "50m"
            memory: "100Mi"
          limits:
            cpu: "150m"
            memory: "200Mi"
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdocker
          mountPath: /var/lib/docker/containers
          readOnly: true

      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdocker
        hostPath:
          path: /var/lib/docker/containers
```

Apply:
```bash
kubectl apply -f 04-fluentbit-daemonset.yaml
```

---

### **Step 5: Apply Everything & Verify**

```bash
# Apply all files
kubectl apply -f 01-config.yaml
kubectl apply -f 02-postgres-statefulset.yaml
kubectl apply -f 03-frontend-deployment.yaml
kubectl apply -f 04-fluentbit-daemonset.yaml
```

**Verify the Full Stack**:
```bash
# See all resources
kubectl get all

# See StatefulSet, Deployment, DaemonSet specifically
kubectl get statefulset,deployment,daemonset

# See Pods with node assignment
kubectl get pods -o wide

# Check PVCs (for StatefulSet)
kubectl get pvc
```

---

### **Step 6: Test the Application**

```bash
# Get Frontend URL
minikube service frontend --url

# Open in browser or test
curl $(minikube service frontend --url)
```

**Access Database from another Pod**:
```bash
kubectl run -it postgres-client --image=postgres:17-alpine --rm -- psql -h postgres -U postgres
# Password = postgres123
```

---

### **Step 7: Lab Exercises (Practice These)**

1. **Scale the Deployment** → `kubectl scale deployment frontend --replicas=6`
2. **Delete one Frontend Pod** → Observe Deployment self-healing
3. **Delete one Postgres Pod** → Observe StatefulSet recreates with same name + data preserved
4. **Add a new node** (if using multi-node Minikube) → See DaemonSet automatically deploys Fluent Bit
5. **Update Frontend image** → Perform rolling update
6. **Check logs** from Fluent Bit DaemonSet Pods

---

### **Cleanup**

```bash
kubectl delete namespace fullstack-lab
```

---

**What You Practiced in This Lab**:

- **Deployment** → Scalable stateless frontend
- **StatefulSet** → Persistent database with stable identity
- **DaemonSet** → Node-level logging agent
- Storage, Config, Secrets, Services, Probes (indirectly)

