**ConfigMaps** and **Secrets** are two fundamental Kubernetes API objects for managing configuration and sensitive data separately from your container images. This separation makes applications portable, environment-agnostic, and easier to manage without rebuilding images.

### ConfigMaps

A **ConfigMap** stores non-confidential data in key-value pairs. It decouples configuration from the container image so the same image can run in different environments (dev, staging, prod) with different settings.

**Key Characteristics**:
- Data is stored as plain text.
- Maximum size per ConfigMap: **1 MiB**.
- Not encrypted or secret — anyone with read access to the object can see the values.
- Immutable option available for better security and performance.

#### Creating ConfigMaps

**1. Imperative (CLI)**:
```bash
# From literal values
kubectl create configmap my-config --from-literal=APP_ENV=production --from-literal=LOG_LEVEL=info

# From files
kubectl create configmap my-config --from-file=app.properties --from-file=config.yaml

# From directory
kubectl create configmap my-config --from-file=./config-dir/
```

**2. Declarative (YAML)**:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: default
data:
  APP_ENV: "production"
  LOG_LEVEL: "debug"
  DB_HOST: "postgres-service.default.svc.cluster.local"
  feature_flags.yaml: |
    enabled:
      - payments
      - analytics
    rate_limit: 100
```

#### Consuming ConfigMaps in Pods

**Option 1: As Environment Variables**
```yaml
spec:
  containers:
  - name: myapp
    image: myapp:1.0
    env:
    - name: APP_ENV
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: APP_ENV
    envFrom:                  # Import all keys
    - configMapRef:
        name: app-config
```

**Option 2: Mounted as Volume (Recommended for files)**
```yaml
spec:
  containers:
  - name: myapp
    image: myapp:1.0
    volumeMounts:
    - name: config-volume
      mountPath: /app/config
      readOnly: true
  volumes:
  - name: config-volume
    configMap:
      name: app-config
      items:                    # Optional: select specific keys & paths
      - key: feature_flags.yaml
        path: features.yaml
      optional: false           # Default: Pod fails if ConfigMap missing
```

**Behavior**:
- Mounted files are updated automatically when ConfigMap changes (kubelet syncs every 60s by default).
- Environment variables are set at container start — changes require Pod restart.

#### Advanced ConfigMap Features
- **Immutable ConfigMaps** (`immutable: true`): Prevents updates after creation. Great for stability; forces new ConfigMap + rollout for changes.
- **Binary Data**: Use `binaryData` field (base64-encoded) for non-UTF8 data.
- **Optional**: Set `optional: true` so Pod starts even if ConfigMap is missing.

**Use Cases**:
- Application settings, feature flags, log levels.
- Configuration files (nginx.conf, application.yml).
- Environment-specific endpoints, timeouts.

**Limitations**:
- 1 MiB size limit.
- Not suitable for sensitive data.
- Large numbers of ConfigMaps can increase etcd load.

### Secrets

**Secrets** are like ConfigMaps but designed for confidential data (passwords, tokens, keys, certificates). They are base64-encoded (not encrypted) by default.

**Important Security Note (2026)**: Secrets are stored unencrypted in etcd by default. You **must** enable encryption at rest and follow other best practices.

#### Types of Secrets
- **Opaque** (default): Generic key-value.
- **kubernetes.io/tls**: For TLS certificates (`tls.crt`, `tls.key`).
- **kubernetes.io/dockerconfigjson**: For image pull secrets.
- **kubernetes.io/service-account-token** (deprecated in favor of TokenRequests).
- Others: SSH auth, etc.

#### Creating Secrets

**CLI**:
```bash
kubectl create secret generic db-secret \
  --from-literal=DB_PASSWORD=SuperSecret123 \
  --from-literal=API_KEY=xyz789

kubectl create secret tls my-tls-secret \
  --cert=tls.crt --key=tls.key
```

**YAML (Opaque)**:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
data:
  DB_PASSWORD: U3VwZXJTZWNyZXQxMjM=  # base64("SuperSecret123")
  DB_USER: YWRtaW4=
stringData:                        # Optional: plain text (gets encoded)
  ANOTHER_KEY: plainvalue
```

#### Consuming Secrets

Similar to ConfigMaps:
- `env` / `envFrom` with `secretKeyRef`.
- Volume mount (files appear decoded).

**Example Volume Mount**:
```yaml
volumes:
- name: secret-volume
  secret:
    secretName: db-credentials
    items:
    - key: DB_PASSWORD
      path: db_pass.txt
```

#### Advanced Features
- **Immutable Secrets**: Same as ConfigMaps (`immutable: true`).
- **Projected Volumes**: Combine ConfigMap + Secret + DownwardAPI into one directory.

**Example**:
```yaml
volumes:
- name: all-in-one
  projected:
    sources:
    - configMap:
        name: app-config
    - secret:
        name: db-credentials
```

### Key Differences: ConfigMap vs Secret

| Aspect              | ConfigMap                          | Secret                              |
|---------------------|------------------------------------|-------------------------------------|
| Purpose             | Non-sensitive config               | Sensitive data                      |
| Storage             | Plain text                         | Base64-encoded                      |
| Size Limit          | 1 MiB                              | 1 MiB                               |
| Encryption          | None                               | None by default (enable at rest)    |
| Visibility          | Easier to view                     | Slightly more protected             |
| Use in Pods         | env or volume                      | env or volume                       |
| Best For            | Config files, settings             | Passwords, keys, certs              |

### Best Practices & Security (Critical)

**For Both**:
- Use consistent naming and namespaces.
- Reference via volumes when possible (better for large configs, auto-updates).
- Use `immutable: true` where updates should be controlled via new objects + rollouts.
- Monitor etcd size and ConfigMap/Secret count.

**Secrets-Specific**:
1. **Enable Encryption at Rest** in etcd (use KMS for best security).
2. **RBAC**: Restrict `get`/`watch` on Secrets to only necessary ServiceAccounts.
3. **External Secrets** (strongly recommended for production): Use **External Secrets Operator (ESO)** with Vault, AWS Secrets Manager, Azure Key Vault, etc. Secrets never live in etcd long-term.
4. Rotate secrets regularly.
5. Avoid committing plain Secrets to Git (use Sealed Secrets, SOPS, or external tools).
6. Use `externalTrafficPolicy` and NetworkPolicies to limit exposure.
7. Never log secret values.

### End-to-End Workflow

1. **Design** — Identify config vs sensitive data.
2. **Create** — Use YAML or `kubectl create secret/configmap`.
3. **Reference** in Deployment/StatefulSet/DaemonSet.
4. **Deploy** — Rolling updates handle changes (restart Pods for env vars).
5. **Verify**:
   ```bash
   kubectl get configmap/app-config -o yaml
   kubectl get secret/db-secret -o yaml   # Shows base64
   kubectl describe pod mypod
   ```
6. **Test** inside Pod: `env | grep APP` or `cat /app/config/file`.
7. **Monitor & Update** — Use GitOps (ArgoCD/Flux) for declarative management.

### Common Pitfalls & Troubleshooting
- Mismatched key names.
- Forgetting base64 for Secret `data` (use `stringData`).
- Pod failing to start due to missing ConfigMap/Secret (check `optional`).
- Updates not reflected (env vars need restart; use volume mounts).
- etcd bloat from too many/large objects.
- Security leaks via logs or misconfigured RBAC.

**Production Recommendation (2026)**: For most real-world clusters, combine native ConfigMaps/Secrets for simple cases with **External Secrets Operator** + a proper secrets manager (Vault, etc.) for anything sensitive or at scale.

**Kubernetes Volume Snapshots** provide a standardized, CSI-based mechanism to create point-in-time copies of PersistentVolumes (PVs). These snapshots enable backups, disaster recovery, testing, cloning, and data migration without downtime.

### Why Use Volume Snapshots?
- **Point-in-time consistency** (crash-consistent by default; application-consistent depends on the driver and pre-snapshot hooks).
- **Efficient storage**: Many backends use copy-on-write or metadata-only snapshots (space-efficient).
- **Fast provisioning**: Create new volumes pre-populated from a snapshot (cloning).
- **Backup & Restore**: Integrate with tools like Velero, or custom operators.
- **Zero-downtime operations**: Clone for testing, auditing, or blue/green deployments.
- **Compliance & Auditing**: Retain historical data states.

**Important**: Snapshots work **only with CSI drivers** that implement the snapshot functionality (most major cloud and on-prem drivers do). In-tree volumes are not supported.

### Core API Objects (v1, GA since Kubernetes 1.20)

1. **VolumeSnapshot** (namespace-scoped): User-facing request, similar to a PVC.
2. **VolumeSnapshotContent** (cluster-scoped): The actual snapshot object, similar to a PV.
3. **VolumeSnapshotClass**: Defines the driver and parameters, similar to a StorageClass.

These are **Custom Resource Definitions (CRDs)** provided by the `external-snapshotter` project, not core Kubernetes APIs.

### Prerequisites

- CSI driver that supports snapshots (check driver documentation).
- **Snapshot CRDs** installed.
- **Snapshot Controller** (`snapshot-controller`) running in the cluster (usually in `kube-system` or a dedicated namespace). One controller serves the entire cluster.

**Install CRDs & Controller (if missing)**:
```bash
# Latest from external-snapshotter
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/master/client/config/crd/snapshot.storage.k8s.io_volumesnapshotclasses.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/master/client/config/crd/snapshot.storage.k8s.io_volumesnapshotcontents.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/master/client/config/crd/snapshot.storage.k8s.io_volumesnapshots.yaml

# Deploy snapshot-controller (via Helm or manifests)
```

### VolumeSnapshotClass

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: fast-snapshot
  annotations:
    snapshot.storage.kubernetes.io/is-default-class: "true"  # Optional
driver: ebs.csi.aws.com          # Or your CSI driver
deletionPolicy: Delete           # Delete | Retain
parameters:
  # Driver-specific, e.g., tags, encryption, snapshot type
  csi.storage.k8s.io/snapshotter-secret-name: my-secret
```

**deletionPolicy**:
- **Delete** (common): Delete the underlying storage snapshot when VolumeSnapshot is deleted.
- **Retain**: Keep the snapshot even after deleting the Kubernetes object (manual cleanup required).

### Creating a Volume Snapshot

**Dynamic Snapshot from PVC**:
```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: myapp-snapshot
  namespace: default
spec:
  volumeSnapshotClassName: fast-snapshot
  source:
    persistentVolumeClaimName: myapp-pvc   # Source PVC must be bound
```

**Pre-provisioned (import existing snapshot)**:
Create a `VolumeSnapshotContent` manually with `snapshotHandle`, then bind it.

**Status Fields** (important):
- `readyToUse: true`
- `creationTime`
- `restoreSize`
- `error` (if failed)

### Restoring from a Snapshot (Create New PVC)

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: restored-pvc
spec:
  storageClassName: standard
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  dataSource:
    kind: VolumeSnapshot
    name: myapp-snapshot
    apiGroup: snapshot.storage.k8s.io
  # Or dataSourceRef for more options
```

This provisions a new volume pre-populated with the snapshot data.

**Volume Cloning** (directly from another PVC, if supported) uses `dataSource` with `kind: PersistentVolumeClaim`.

### Deleting Snapshots

- Delete the `VolumeSnapshot` object.
- Behavior depends on `deletionPolicy` in the associated `VolumeSnapshotClass`.
- For `Retain`, manually delete the `VolumeSnapshotContent` after cleanup.

### Advanced Features & Concepts

- **VolumeGroupSnapshot** (in progress / CRDs available): Atomic snapshots of multiple volumes (e.g., app with data + logs volumes).
- **Cross-Namespace Restore**: Manually create `VolumeSnapshotContent` with the snapshot handle and reference it in the target namespace.
- **Application-Consistent Snapshots**: Use pre/post hooks (e.g., freeze filesystem, quiesce database) via sidecars or external tools.
- **VolumeSnapshotContent Binding**:
  - Dynamic: Controller creates `VolumeSnapshotContent`.
  - Static: Pre-provisioned.
- **CSI Sidecar**: `csi-snapshotter` runs with the driver and calls `CreateSnapshot`/`DeleteSnapshot` RPCs.

### Best Practices (2026)

1. **Choose the Right Driver** — Verify snapshot support, performance, and consistency guarantees.
2. **Default SnapshotClass** — Useful but be explicit in production.
3. **Automate with Tools**:
   - Velero (with CSI support).
   - Custom operators or CronJobs + VolumeSnapshot.
   - External backup solutions (Kasten, Trilio, etc.).
4. **Retention Policies** — Combine with `Retain` + external lifecycle management.
5. **Testing** — Regularly test restores.
6. **Monitoring** — Watch `VolumeSnapshot` status, errors, and storage backend metrics.
7. **Security**:
   - RBAC: Limit who can create/delete snapshots.
   - Use encryption.
   - Namespace isolation.
8. **Performance**:
   - Snapshots are usually fast (metadata ops), but test impact on production workloads.
   - Use `WaitForFirstConsumer` where applicable.
9. **StatefulSets** — Combine with PVC templates for easy per-replica snapshots.

### Troubleshooting Common Issues

- **Pending/ReadyToUse: false**: Check CSI driver logs, snapshot-controller logs, events (`kubectl describe volumesnapshot`).
- **Missing CRDs/Controller**: Snapshots won't work.
- **Driver Not Supported**: Verify with `kubectl get csidrivers`.
- **Deletion Stuck**: Finalizers (e.g., bound-protection) — check `VolumeSnapshotContent`.
- **Size Mismatch**: Ensure new PVC requests enough storage (`restoreSize`).
- **Cross-Namespace/Cluster**: Use manual `VolumeSnapshotContent` with `snapshotHandle`.
- **Consistency Problems**: Application not quiesced → corrupted data in snapshot.

**Commands**:
```bash
kubectl get volumesnapshot,volumesnapshotcontent,volumesnapshotclass -A
kubectl describe volumesnapshot my-snap
kubectl get events --field-selector involvedObject.name=my-snap
```

### Integration with Broader Ecosystem

- **Velero**: CSI snapshot support for backups.
- **Data Protection**: Combine with Volume Populators, clones, and external snapshot tools.
- **GitOps**: Declarative snapshots via ArgoCD/Flux (with care for mutable nature).

Volume Snapshots are a mature, production-ready feature that completes the persistent storage story in Kubernetes. They bridge the gap between ephemeral containers and durable data. For the absolute latest driver-specific parameters or VolumeGroupSnapshot status, refer to your CSI driver's documentation and the official Kubernetes Volume Snapshots page.

**Practice Recommendation**: Deploy a MySQL/PostgreSQL StatefulSet with a PVC, take a snapshot while writing data, restore to a new PVC, and verify data integrity. This end-to-end exercise solidifies understanding.
