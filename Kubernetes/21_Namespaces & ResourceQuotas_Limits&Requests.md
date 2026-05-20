**Namespaces, ResourceQuotas, Resource Requests & Limits, and LimitRanges** are essential Kubernetes features for **multi-tenancy**, resource governance, organization, and isolation in a shared cluster.

### 1. Namespaces

**Namespaces** provide logical isolation and partitioning within a single Kubernetes cluster. They are the primary way to divide cluster resources among teams, environments, or applications.

#### Key Characteristics
- **Isolation**:
  - Most resources (Pods, Services, Deployments, ConfigMaps, Secrets, etc.) are **namespace-scoped**.
  - Some are **cluster-scoped** (Nodes, PersistentVolumes, StorageClasses, ClusterRoles, etc.).
- **DNS**: Services within a namespace can be reached as `<service>.<namespace>.svc.cluster.local`.
- **Default Namespaces**:
  - `default`
  - `kube-system` (system components)
  - `kube-public`
  - `kube-node-lease`
- **Resource Quotas & Limits** apply per namespace.

**Creating Namespaces**:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    environment: prod
  annotations:
    purpose: "Production workloads"
```

CLI:
```bash
kubectl create namespace staging
kubectl get ns
```

**Best Practice**: Use labels/annotations for organization and policy enforcement (e.g., with Kyverno or Gatekeeper).

#### Use Cases
- Separate environments (dev, staging, prod)
- Multi-team isolation (team-a, team-b)
- SaaS / multi-tenancy
- Application grouping

**Network Isolation**: Namespaces are **not** network-isolated by default. Use **NetworkPolicies** for that.

**RBAC**: Roles and RoleBindings are namespace-scoped. Use ClusterRoles + ClusterRoleBindings for cross-namespace access.

### 2. Resource Requests & Limits (Container Level)

These define how much CPU and memory a **container** can consume.

#### Requests
- The amount of resources Kubernetes **guarantees** to the container.
- Used by the **scheduler** to decide which node can run the Pod (based on available allocatable resources).
- Influences **QoS (Quality of Service)**.

#### Limits
- The maximum resources a container can use.
- If exceeded:
  - **CPU**: Throttled (cgroups).
  - **Memory**: Container can be OOMKilled.

**Example in a Deployment**:
```yaml
spec:
  containers:
  - name: api
    image: myapp:1.0
    resources:
      requests:
        cpu: "500m"      # 0.5 cores
        memory: "512Mi"
      limits:
        cpu: "1"
        memory: "1Gi"
    # Other fields: ephemeral-storage, hugepages, etc.
```

**Units**:
- CPU: `m` (millicores) or whole numbers (1 = 1 core).
- Memory: `Mi` (mebibytes), `Gi`, `M`, `G`, etc.

**QoS Classes** (determined automatically):
1. **Guaranteed**: Requests = Limits for all containers.
2. **Burstable**: Requests < Limits (or only some resources requested).
3. **BestEffort**: No requests or limits.

**Eviction Priority**: BestEffort → Burstable → Guaranteed (lowest chance of eviction).

### 3. LimitRanges (Namespace Level)

**LimitRange** enforces default requests/limits and min/max constraints per namespace.

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: production
spec:
  limits:
  - type: Container
    default:
      cpu: 500m
      memory: 512Mi
    defaultRequest:
      cpu: 200m
      memory: 256Mi
    max:
      cpu: "2"
      memory: "4Gi"
    min:
      cpu: "100m"
      memory: "128Mi"
  - type: Pod
    max:
      cpu: "4"
      memory: "8Gi"
```

**Benefits**:
- Prevents Pods from being created without resources.
- Sets sane defaults.
- Enforces upper/lower bounds.

### 4. ResourceQuota (Namespace Level)

**ResourceQuota** limits the **total** amount of resources that can be consumed by all objects in a namespace.

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-resources
  namespace: staging
spec:
  hard:
    requests.cpu: "4"
    requests.memory: "8Gi"
    limits.cpu: "8"
    limits.memory: "16Gi"
    pods: "20"                    # Max number of Pods
    configmaps: "50"
    persistentvolumeclaims: "10"
    services.loadbalancers: "5"
    # requests.storage, etc.
```

**Scoped Quotas** (more granular):
- `scopes`: `BestEffort`, `NotBestEffort`, `Terminating`, `NotTerminating`, etc.

**Multiple Quotas** per namespace are allowed (they add up).

### Complete End-to-End Example

```yaml
# 1. Namespace
apiVersion: v1
kind: Namespace
metadata:
  name: myteam-prod

# 2. LimitRange
apiVersion: v1
kind: LimitRange
metadata:
  name: limits
  namespace: myteam-prod
spec: { ... }

# 3. ResourceQuota
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-quota
  namespace: myteam-prod
spec:
  hard:
    requests.cpu: "10"
    requests.memory: "20Gi"
    limits.cpu: "20"
    limits.memory: "40Gi"
    pods: "50"
```

Then deploy workloads in that namespace.

### Best Practices (2026)

1. **Always set Requests & Limits** — Never run with BestEffort in production.
2. **Right-size resources** using monitoring (Vertical Pod Autoscaler can help initially).
3. **Use Guaranteed QoS** for critical workloads.
4. **Namespace Strategy**:
   - One namespace per team/environment.
   - Apply NetworkPolicy, ResourceQuota, and LimitRange by default.
5. **Policy Enforcement**:
   - Use OPA/Gatekeeper or Kyverno to enforce resource requests, namespace usage, etc.
6. **Monitoring & Alerts**:
   - Prometheus + Grafana for namespace resource usage.
   - Alert on quota nearing limits.
7. **Multi-tenancy**:
   - Soft (namespaces + RBAC) vs Hard (with network/storage isolation).
8. **Ephemeral Storage**:
   - Also set `requests.ephemeral-storage` and `limits.ephemeral-storage`.
9. **HugePages, GPU, other extended resources** — Can also be quotaed and limited.

### Troubleshooting

- **Pod Pending (Insufficient resources)**: `kubectl describe pod` → Events. Check node capacity and quota.
- **Quota Exceeded**: "exceeded quota" error.
- **OOMKilled**: Memory limit too low.
- **Throttling**: CPU limit too low.
- **Commands**:
  ```bash
  kubectl describe resourcequota -n <ns>
  kubectl describe limitrange -n <ns>
  kubectl top pods -n <ns>
  kubectl get pods -n <ns> -o wide --show-labels
  ```

### Advanced Topics
- **Dynamic Quotas**: Use operators or admission webhooks.
- **Hierarchical Namespaces** (via Hierarchical Namespace Controller).
- **ResourceQuotaScopeSelectors** for label-based quotas.
- **Cluster Resource Quotas** (via projects like Kubefed or custom).

**Production Workflow**:
1. Create Namespace.
2. Apply NetworkPolicy, LimitRange, ResourceQuota.
3. Onboard teams with templates (Helm/ArgoCD).
4. Monitor usage and adjust quotas.
5. Use VPA / HPA for autoscaling.

This forms the foundation of stable, fair, and secure multi-tenant Kubernetes clusters. Namespaces + proper resource governance prevent "noisy neighbor" problems and enable reliable scaling.

