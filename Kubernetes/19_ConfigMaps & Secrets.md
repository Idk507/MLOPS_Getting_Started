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

