**Kubernetes Services** provide a stable abstraction layer for exposing a group of Pods (or other backends) over the network. Pods are ephemeral—their IPs change on restarts, rescheduling, or scaling—so Services decouple clients from individual Pod lifecycles and IPs.

### Why Services Exist
- Pods have individual, unstable IPs.
- You need reliable access (via a single IP/DNS name) even as Pods scale, fail, or move.
- Load balancing across ready Pods (via selectors and EndpointSlices).
- Service discovery (DNS + environment variables).
- Abstraction for internal or external access without changing application code.

**Core Components of a Service**:
- **Selector**: Label selector to match Pods (most common). The Endpoints controller creates/updates EndpointSlices.
- **Ports**: `port` (Service port), `targetPort` (Pod/container port; can be a name or number), `protocol` (TCP/UDP/SCTP), optional `name`.
- **ClusterIP**: Virtual IP (VIP) assigned from the service-cluster-ip-range (default type).
- **EndpointSlices**: Modern (v1.21+ stable) way to track subsets of endpoints (Pods). Replaces the older Endpoints API.

Services are implemented by **kube-proxy** on every node (or alternatives), which watches the API server and programs network rules.

### Service Discovery
- **DNS** (recommended, via CoreDNS): `<service-name>.<namespace>.svc.cluster.local` resolves to ClusterIP (or individual Pod IPs for headless).
- **Environment Variables**: Injected into Pods (e.g., `MY_SERVICE_SERVICE_HOST`). Create Service *before* client Pods.
- SRV records for named ports.

### How Traffic Routing Works (kube-proxy Modes)
**kube-proxy** handles VIPs and load balancing (except for headless/ExternalName).

- **iptables** (traditional default): Uses netfilter rules. O(n) for many Services (sequential matching). Good for small/medium clusters.
- **IPVS** (better scalability): Hash tables + advanced schedulers (rr, leastconn, source hashing, etc.). Deprecated in favor of nftables in newer Kubernetes but still used.
- **nftables** (modern replacement): Better performance than both.
- Others (userspace, kernelspace on Windows) are less common.

Traffic is DNATed to backend Pods. Session affinity (ClientIP) and traffic policies control behavior.

### The Four Main Service Types + ExternalName

#### 1. ClusterIP (Default)
- Exposes the Service on a **cluster-internal VIP** only.
- Reachable only from within the cluster.
- Ideal for microservices talking to each other (backend APIs, databases).

**Example YAML**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-clusterip-service
spec:
  selector:
    app: my-app
  ports:
    - protocol: TCP
      port: 80          # Service port
      targetPort: 8080  # Pod port
  type: ClusterIP       # Optional, default
```

- Access: `http://my-clusterip-service:80` or full DNS.
- You can specify your own `.spec.clusterIP` (must be in service range).

**Use Cases**: Internal communication, stable endpoint for frontends/backends.

#### 2. NodePort
- Builds on ClusterIP.
- Exposes a **static port** (default range 30000-32767) on **every node's IP**.
- External access: `<NodeIP>:<NodePort>`.
- kube-proxy listens on that port on all nodes and forwards to ClusterIP or directly to Pods.

**Example**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-nodeport-service
spec:
  type: NodePort
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 8080
      nodePort: 30007  # Optional; auto-assigned if omitted
```

**Pros**: Simple external access without cloud provider. Good for testing, on-prem, or when you manage your own LB.
**Cons**: Port range limits, exposes ports on all nodes (security/firewall considerations), no built-in HA LB (use external LB in front).

**Custom NodePort Addresses**: Use `--nodeport-addresses` in kube-proxy config.

#### 3. LoadBalancer
- Builds on NodePort (unless `allocateLoadBalancerNodePorts: false`).
- Provisions an **external load balancer** via the cloud provider (or load-balancer controller).
- `.status.loadBalancer.ingress` shows the external IP/hostname once ready.

**Example**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-lb-service
spec:
  type: LoadBalancer
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 8080
  # allocateLoadBalancerNodePorts: false  # Optional: direct to Pods
```

**Annotations** for cloud-specific config (internal LB, IP, etc.).

**Pros**: Cloud-native, HA, scalable.
**Cons**: Costs money; depends on cloud provider support.

**Key Fields**:
- `loadBalancerClass` (v1.24+): Select specific LB implementation.
- `externalTrafficPolicy: Local` (vs Cluster): Preserves source IP, routes only to local-Pod nodes (may cause uneven load).

#### 4. Headless Services
- No ClusterIP (`clusterIP: None`).
- No load balancing/proxying by kube-proxy.
- DNS returns **individual Pod IPs** (A/AAAA records) or enables direct discovery.

**Example**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-headless
spec:
  clusterIP: None
  selector:
    app: my-stateful-app
  ports:
    - port: 80
      targetPort: 8080
```

**Behavior**:
- With selector: DNS returns ready Pod IPs.
- Without selector: Manual Endpoints; useful for external backends.
- Pods get predictable DNS: `<pod-name>.<service-name>.<namespace>.svc.cluster.local`.

**Primary Use Cases**:
- **StatefulSets**: Stable network identities for databases (MongoDB, Cassandra, MySQL clusters), where you need to address specific replicas (e.g., master vs replicas).
- Distributed systems needing peer discovery or direct Pod access.
- When you want Kubernetes-managed grouping without the VIP/LB.

#### Bonus: ExternalName
- No selector, no endpoints, no proxying.
- Maps to an external DNS name (CNAME).
- Useful for aliasing or migrating services.

**Example**:
```yaml
spec:
  type: ExternalName
  externalName: external-db.example.com
```

### Advanced Concepts
- **Multi-Port Services**: Multiple ports in one Service (different protocols/names).
- **Services Without Selectors**: Manual EndpointSlices for external or non-Pod backends.
- **Traffic Policies**:
  - `internalTrafficPolicy`: Cluster (default) or Local.
  - `externalTrafficPolicy`: Cluster or Local.
  - `trafficDistribution` (preferences like PreferSameZone/Node).
- **Session Affinity**: `ClientIP` (sticky based on source IP).
- **ExternalIPs**: Manually assign external IPs (rare, security risks).
- **Topology-Aware Routing / Hints**: For zone-aware traffic.

### Best Practices & End-to-End Workflow
1. **Design**: Use Deployments for stateless, StatefulSets + Headless for stateful.
2. **Labels**: Consistent, specific selectors.
3. **Security**: NetworkPolicies, RBAC, least-privilege ports.
4. **Production**:
   - ClusterIP internally + Ingress/Gateway for external HTTP/HTTPS.
   - LoadBalancer for non-HTTP or simple cases.
   - Avoid NodePort in prod if possible.
5. **Monitoring**: Check `kubectl get svc,ep,endpointslice`, `kubectl describe svc`.
6. **Scaling & Updates**: Services handle rolling updates seamlessly via selectors.
7. **Troubleshooting**:
   - Pods ready? (`kubectl get pods -o wide`).
   - Endpoints populated?
   - kube-proxy logs/mode.
   - DNS resolution (`nslookup` from a Pod).
   - Firewall/NodePort range.
   - `kubectl port-forward` for testing.

**Creation/Verification Commands**:
- `kubectl apply -f service.yaml`
- `kubectl get svc`
- `kubectl describe svc <name>`
- `kubectl get endpointslice`
- Test: `curl <service-dns>:<port>`

**Common Pitfalls**:
- Mismatched selectors/labels.
- targetPort vs port confusion.
- Assuming stable Pod IPs (use Services or headless).
- NodePort firewall rules.
- Forgetting that LoadBalancer is async.

