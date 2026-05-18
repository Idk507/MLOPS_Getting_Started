**Complete End-to-End Guide: Volumes & PersistentVolumes + Services + Ingress + Full 3-Tier Application Demo**  
**(Kubernetes v1.35.x – Very Detailed, Practical Guide)**

This is one of the most important sections in your Kubernetes journey. We'll cover everything in depth and then build a **realistic 3-tier application**.

---

### 1. Volumes & PersistentVolumes (Storage in Kubernetes)

#### Why Storage is Tricky in Kubernetes

- Containers are **ephemeral** by default — data is lost when a Pod restarts or is rescheduled.
- Pods can move between nodes.
- Different applications need different storage types (fast cache vs durable database).

Kubernetes solves this with two main concepts:

- **Volumes** → Ephemeral or simple storage attached to a Pod.
- **PersistentVolumes (PV)** → Durable storage that survives Pod deletion.

---

### Volume Types (Most Commonly Used)

| Volume Type           | Lifespan          | Use Case                              | Persistent? |
|-----------------------|-------------------|---------------------------------------|-----------|
| `emptyDir`            | Pod lifetime      | Cache, temporary data, shared between containers | No |
| `hostPath`            | Node lifetime     | Development, logs                     | Sort of |
| `configMap` / `secret`| Pod lifetime      | Configuration                         | No |
| `persistentVolumeClaim` | Until deleted   | Databases, user files                 | **Yes** |

#### PersistentVolume (PV) + PersistentVolumeClaim (PVC) + StorageClass

This is the standard pattern for production:

- **StorageClass** — Defines the type of storage (fast SSD, HDD, cloud storage).
- **PersistentVolume (PV)** — Actual storage resource in the cluster.
- **PersistentVolumeClaim (PVC)** — A request for storage by a user/Pod.

**Flow**: Pod → PVC → PV → Actual Storage

---

### 2. Services – In Depth

A **Service** provides **stable networking** and **load balancing** for Pods.

#### Service Types

| Type              | Scope             | How it Works                                      | Use Case                              |
|-------------------|-------------------|---------------------------------------------------|---------------------------------------|
| **ClusterIP**     | Internal only     | Virtual IP inside cluster                         | Backend services, microservices       |
| **NodePort**      | External          | Exposes on every node at high port (30000-32767)  | Testing, quick external access        |
| **LoadBalancer**  | External          | Provisions cloud Load Balancer                    | Production external traffic           |
| **Headless**      | Internal          | `clusterIP: None` — returns all Pod IPs directly  | StatefulSets, databases               |

**Key Fields**:
- `selector` → Matches Pods using labels
- `port` → Service port
- `targetPort` → Container port

---

### 3. Ingress – HTTP/S Routing (Layer 7)

**Ingress** is **not** a Service type. It sits in front of Services and provides:
- Host-based routing (`app.example.com`)
- Path-based routing (`/api`, `/web`)
- TLS termination
- Load balancing rules

You need an **Ingress Controller** (NGINX, Traefik, etc.) to make Ingress work.

---

### 4. Full 3-Tier Application Demo (Runnable on Minikube)

We will deploy:
- **Frontend**: NGINX (static website)
- **Backend**: Node.js API
- **Database**: PostgreSQL (with PersistentVolume)

#### Step 1: Create Namespace

```bash
kubectl create namespace 3tier-app
kubectl config set-context --current --namespace=3tier-app
```

---

#### Step 2: Persistent Storage for Database

```yaml
# 01-postgres-pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
  storageClassName: standard          # Minikube default
```

---

#### Step 3: PostgreSQL Deployment + Service

```yaml
# 02-postgres.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
spec:
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
          value: admin
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
        - name: POSTGRES_DB
          value: myapp
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data

      volumes:
      - name: postgres-data
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
  type: ClusterIP
```

---

#### Step 4: Backend (Node.js API) + ConfigMap + Secret

```yaml
# 03-backend.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: backend-config
data:
  NODE_ENV: production
  DB_HOST: postgres
---
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  password: YWRtaW4xMjM=          # base64 of "admin123"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: yourusername/node-api:latest   # Replace with your image
        envFrom:
        - configMapRef:
            name: backend-config
        - secretRef:
            name: db-secret
        ports:
        - containerPort: 3000
---
apiVersion: v1
kind: Service
metadata:
  name: backend
spec:
  selector:
    app: backend
  ports:
  - port: 3000
    targetPort: 3000
  type: ClusterIP
```

---

#### Step 5: Frontend + Ingress

```yaml
# 04-frontend.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
spec:
  replicas: 2
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
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: main-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: myapp.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 3000
```

---

### Apply Everything

```bash
kubectl apply -f 01-postgres-pvc.yaml
kubectl apply -f 02-postgres.yaml
kubectl apply -f 03-backend.yaml
kubectl apply -f 04-frontend.yaml
```

Wait for all Pods to be Ready:
```bash
kubectl get pods -w
```

---

### Access Your Application

```bash
# Enable Ingress Controller in Minikube
minikube addons enable ingress

# Get the URL
minikube service frontend --url

# Or add to /etc/hosts for custom domain
echo "$(minikube ip) myapp.local" | sudo tee -a /etc/hosts

# Open in browser
curl http://myapp.local
```

---


You now have very strong coverage of core Kubernetes concepts. What's next on your learning path?
