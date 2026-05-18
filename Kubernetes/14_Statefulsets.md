**Complete End-to-End Guide to Kubernetes StatefulSets**  
**(For Databases & Stateful Applications – Kubernetes v1.35.x, April 2026)**

### What is a StatefulSet?

A **StatefulSet** is a Kubernetes workload controller designed specifically for **stateful applications** — applications that require:

- Stable, unique network identity (persistent hostname)
- Stable, persistent storage
- Ordered deployment, scaling, and termination
- Ability to maintain identity even after Pod restart or rescheduling

**Classic Use Cases**:
- Databases (PostgreSQL, MySQL, MongoDB, Redis, Cassandra, Elasticsearch)
- Message brokers (Kafka, RabbitMQ)
- Distributed systems (ZooKeeper, etcd)
- Any app that needs persistent identity and storage

---

### Deployment vs StatefulSet – Deep Comparison

| Feature                      | Deployment (Stateless)               | StatefulSet (Stateful)                     |
|-----------------------------|--------------------------------------|--------------------------------------------|
| Pod Identity                | Ephemeral (random name)              | Stable & predictable (`db-0`, `db-1`)      |
| Network Identity            | Changes on restart                   | Stable via Headless Service                |
| Storage                     | Shared or ephemeral                  | Individual PersistentVolume per Pod        |
| Scaling Order               | No guarantee                         | Ordered (0 → 1 → 2)                        |
| Termination Order           | No guarantee                         | Reverse order (2 → 1 → 0)                  |
| Rolling Updates             | Yes                                  | Yes (with partition support)               |
| Recommended For             | Frontend, APIs, microservices        | Databases, distributed systems             |

---

### Key Features of StatefulSets

1. **Stable Pod Identity**
   - Pods are named with ordinal indices: `postgres-0`, `postgres-1`, `postgres-2`
   - These names remain the same even if the Pod is deleted and recreated.

2. **Stable Network Identity**
   - Each Pod gets a unique DNS name: `<pod-name>.<service-name>.<namespace>.svc.cluster.local`
   - Example: `postgres-0.postgres.default.svc.cluster.local`

3. **Persistent Storage per Pod**
   - Uses `volumeClaimTemplates` to create individual PVCs for each Pod.

4. **Ordered Operations**
   - Pods are created, scaled, and deleted in **ordinal order**.
   - This is critical for databases (primary → replicas).

---

### Complete StatefulSet YAML for PostgreSQL (Production Style)

```yaml
# 01-postgres-statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: "postgres"           # Required for headless service
  replicas: 3
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
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_USER
          value: "admin"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
        - name: POSTGRES_DB
          value: "mydb"
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data

  volumeClaimTemplates:             # Creates separate PVC for each Pod
  - metadata:
      name: postgres-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "standard"
      resources:
        requests:
          storage: 5Gi
```

---

### Headless Service (Mandatory for StatefulSets)

```yaml
# 02-headless-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres
spec:
  clusterIP: None                    # This makes it Headless
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
```

**Why Headless?**  
It allows direct communication with individual Pods using their stable DNS names instead of load balancing.

---

### Hands-on: Deploy & Explore StatefulSet

```bash
# 1. Create Secret first
kubectl create secret generic db-secret --from-literal=password=admin123

# 2. Apply files
kubectl apply -f 02-headless-service.yaml
kubectl apply -f 01-postgres-statefulset.yaml

# 3. Watch creation (notice ordered rollout)
kubectl get pods -w -l app=postgres
```

**Expected Pod names**:
- `postgres-0`
- `postgres-1`
- `postgres-2`

```bash
# Check stable DNS
kubectl run -it --rm test --image=busybox -- nslookup postgres-0.postgres

# Check individual storage
kubectl get pvc
# You should see postgres-data-postgres-0, postgres-data-postgres-1, etc.
```

---

### Scaling StatefulSets

```bash
# Scale up
kubectl scale statefulset postgres --replicas=5

# Scale down (removes highest ordinal first)
kubectl scale statefulset postgres --replicas=3
```

**Important**: When scaling down, the highest numbered Pod is deleted first, and its PVC **remains** (data is preserved).

---

### Update Strategies

```yaml
spec:
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      partition: 0          # Update all pods
```

- `OnDelete`: Only update when you manually delete a Pod (safe for databases).
- `RollingUpdate`: Gradually updates Pods in reverse ordinal order.

---

### All Important Topics Covered

| Topic                        | Explanation                                                                 |
|-----------------------------|-----------------------------------------------------------------------------|
| **Pod Management Policy**   | `OrderedReady` (default) or `Parallel`                                      |
| **Termination Grace Period**| Graceful shutdown (important for databases)                                 |
| **Init Containers**         | Can be used for initialization before main container starts                 |
| **Node Affinity**           | Can be added for database performance (e.g., pin to specific nodes)         |
| **Backup Strategy**         | Use Velero or database-specific tools (pg_dump, etc.)                       |
| **Readiness & Liveness**    | Must be configured properly for databases                                   |
| **Data Recovery**           | PVCs survive Pod deletion → easy recovery                                   |

---

### Best Practices for StatefulSets (2026)

1. Always use a **Headless Service**.
2. Use `volumeClaimTemplates` for per-Pod storage.
3. Start with 1 replica for primary, then scale for replicas (in many databases).
4. Use `OnDelete` update strategy for major database version upgrades.
5. Monitor PVC usage carefully.
6. Consider **Operators** (like Postgres Operator, MongoDB Operator) for complex databases instead of raw StatefulSets.
7. Take regular backups.
8. Use Resource Requests & Limits.

---

### When to Use StatefulSet vs Deployment

- **Use Deployment** → Stateless apps (frontend, APIs, backend services)
- **Use StatefulSet** → Any application that needs:
  - Persistent identity
  - Persistent storage per instance
  - Ordered operations

---

**Practice Exercise**

1. Deploy the PostgreSQL StatefulSet above.
2. Connect to `postgres-0` and create a table.
3. Delete `postgres-0` Pod → Observe it comes back with same data.
4. Scale to 5 replicas.
5. Try scaling down.


Run the StatefulSet example and tell me what you observe.
