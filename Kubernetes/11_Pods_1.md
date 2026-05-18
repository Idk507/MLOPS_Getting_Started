

### Part 1: Advanced Pod Scenarios (Init Containers, Probes, Resource Limits)
### Part 2: ConfigMaps & Secrets (with hands-on injection into Pods)

---

### **Part 1: Advanced Pod Features (Hands-on)**

#### 1. Resource Requests & Limits (Very Important)

This prevents one Pod from starving others on the node.

```yaml
# File: pod-resources.yaml
apiVersion: v1
kind: Pod
metadata:
  name: resource-demo
spec:
  containers:
  - name: nginx
    image: nginx:1.27-alpine
    resources:
      requests:           # Kubernetes uses this for scheduling
        cpu: "200m"       # 0.2 CPU core
        memory: "256Mi"
      limits:             # Hard cap - Pod can be throttled or killed
        cpu: "500m"
        memory: "512Mi"
    ports:
    - containerPort: 80
```

**Apply & Check**:
```bash
kubectl apply -f pod-resources.yaml
kubectl describe pod resource-demo | grep -A 10 "Requests"
```

---

#### 2. Probes (Health Checks) – Critical for Self-Healing

- **Startup Probe**: Gives time for slow-starting apps (e.g., Java apps).
- **Readiness Probe**: Tells Service whether the Pod can receive traffic.
- **Liveness Probe**: If fails → container is restarted.

```yaml
# File: pod-probes.yaml
apiVersion: v1
kind: Pod
metadata:
  name: probe-demo
spec:
  containers:
  - name: nginx
    image: nginx:1.27-alpine
    ports:
    - containerPort: 80

    startupProbe:                    # Runs first
      httpGet:
        path: /
        port: 80
      failureThreshold: 30
      periodSeconds: 10

    readinessProbe:                  # Ready to receive traffic?
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 5

    livenessProbe:                   # Is container alive?
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 15
      periodSeconds: 10
      timeoutSeconds: 5
```

**Hands-on**:
```bash
kubectl apply -f pod-probes.yaml
kubectl describe pod probe-demo | grep -A 20 "Probes"
```

---

#### 3. Init Containers (Run Before Main Containers)

Init containers are perfect for initialization tasks (database migration, config download, etc.).

```yaml
# File: pod-init.yaml
apiVersion: v1
kind: Pod
metadata:
  name: init-demo
spec:
  initContainers:
  - name: init-myservice
    image: busybox:1.36
    command: ['sh', '-c', 'echo "Initializing... waiting for service" && sleep 10']

  containers:
  - name: nginx
    image: nginx:1.27-alpine
    ports:
    - containerPort: 80
```

**Apply & Observe**:
```bash
kubectl apply -f pod-init.yaml
kubectl get pods -w                    # Watch init container run first
kubectl logs init-demo -c init-myservice
```

---

### **Part 2: ConfigMaps & Secrets**

#### What’s the Difference?

| Feature         | ConfigMap                          | Secret                              |
|-----------------|------------------------------------|-------------------------------------|
| Purpose         | Non-sensitive configuration        | Sensitive data (passwords, keys)    |
| Storage         | Base64 encoded (plain text)        | Base64 encoded + obfuscated         |
| Size Limit      | 1 MiB                              | 1 MiB                               |
| Use Case        | Config files, env vars, commands   | Passwords, API keys, TLS certs      |

---

#### 1. ConfigMap (Two Ways: Environment Variables & Volume)

**Create ConfigMap**

```yaml
# File: app-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  APP_ENV: production
  LOG_LEVEL: debug
  DATABASE_HOST: postgres.default.svc.cluster.local
  FEATURE_FLAG: "true"
```

**Pod consuming ConfigMap**

```yaml
# File: pod-with-config.yaml
apiVersion: v1
kind: Pod
metadata:
  name: config-demo
spec:
  containers:
  - name: nginx
    image: nginx:1.27-alpine
    envFrom:                          # Inject all keys as env vars
    - configMapRef:
        name: app-config

    # Alternative: Mount as volume (for config files)
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config

  volumes:
  - name: config-volume
    configMap:
      name: app-config
```

**Hands-on**:
```bash
kubectl apply -f app-config.yaml
kubectl apply -f pod-with-config.yaml

kubectl exec -it config-demo -- env | grep -E 'APP_ENV|LOG_LEVEL'
kubectl exec -it config-demo -- ls /etc/config
```

---

#### 2. Secrets (Best Practices 2026)

```yaml
# File: app-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
type: Opaque
data:
  DB_PASSWORD: c2VjcmV0MTIz      # base64 encoded "secret123"
  API_KEY:      YWJjMTIz         # base64 encoded "abc123"
```

**Pod using Secret**

```yaml
# File: pod-with-secret.yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-demo
spec:
  containers:
  - name: nginx
    image: nginx:1.27-alpine
    env:
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: app-secret
          key: DB_PASSWORD
    volumeMounts:
    - name: secret-volume
      mountPath: /etc/secrets
      readOnly: true

  volumes:
  - name: secret-volume
    secret:
      secretName: app-secret
```

**Hands-on**:
```bash
kubectl apply -f app-secret.yaml
kubectl apply -f pod-with-secret.yaml

kubectl exec -it secret-demo -- env | grep DB_PASSWORD
kubectl exec -it secret-demo -- cat /etc/secrets/DB_PASSWORD
```

---

### Combined Best Practice Pod (All Together)

```yaml
# production-style-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: full-featured-pod
spec:
  initContainers:
  - name: init
    image: busybox
    command: ['sh', '-c', 'echo "Ready to start"']

  containers:
  - name: app
    image: nginx:1.27-alpine
    resources:
      requests:
        cpu: "100m"
        memory: "128Mi"
      limits:
        cpu: "400m"
        memory: "512Mi"

    envFrom:
    - configMapRef:
        name: app-config
    - secretRef:
        name: app-secret

    ports:
    - containerPort: 80

    livenessProbe:
      httpGet:
        path: /
        port: 80
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /
        port: 80
      periodSeconds: 5
```

---


Just say what you want next, Dhanush. Keep practicing the commands — you're doing really well! 🚀
