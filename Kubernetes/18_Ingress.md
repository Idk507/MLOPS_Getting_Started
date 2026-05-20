**Kubernetes Ingress** provides a powerful, declarative way to manage external (primarily HTTP/HTTPS) access to Services in your cluster. It acts as a smart reverse proxy and load balancer at Layer 7, enabling features like host-based and path-based routing, TLS termination, and name-based virtual hosting.

### Why Ingress? (vs. Services)
- **ClusterIP**: Internal only.
- **NodePort/LoadBalancer**: Expose ports/IPs but lack intelligent HTTP routing (no host/path rules, limited TLS handling per hostname, no easy URL rewriting).
- **Ingress**: Single entry point with rules. One LoadBalancer/NodePort for the controller + many logical routes. Saves costs, simplifies management, adds features (rewrites, redirects, auth, rate limiting via controller).

**Limitations**: HTTP(S) focused (use TCP/UDP Services or extensions for others). Requires a running **Ingress Controller**.

**Note on Status (2026)**: The Ingress API is stable/frozen (no new features). Kubernetes recommends **Gateway API** as the future. The popular community `ingress-nginx` project reached end-of-life in March 2026. Many migrate to F5 NGINX Ingress Controller, Traefik, Contour, HAProxy, or Gateway API implementations.

### Ingress Resource (The Declarative Config)
An `Ingress` object defines rules. It does nothing without a controller.

**Minimal Example**:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: minimal-ingress
spec:
  ingressClassName: nginx  # References IngressClass
  rules:
  - http:
      paths:
      - path: /testpath
        pathType: Prefix      # Exact | Prefix | ImplementationSpecific
        backend:
          service:
            name: test-service
            port:
              number: 80
```

**Key Fields**:
- **`ingressClassName`**: Links to `IngressClass` (preferred over deprecated annotation).
- **`rules`**: Array of host + HTTP paths.
  - **Host**: e.g., `foo.example.com` (exact or wildcard `*.example.com`).
  - **Paths**: With `pathType`.
- **`defaultBackend`**: Catch-all for unmatched requests.
- **`tls`**: List of secrets for TLS termination (per host).

**Path Types**:
- **Exact**: `/foo` matches only `/foo`.
- **Prefix**: `/foo` matches `/foo`, `/foo/`, `/foo/bar` (element-wise).
- **ImplementationSpecific**: Controller-dependent.

**TLS Example**:
```yaml
spec:
  tls:
  - hosts:
    - example.com
    secretName: tls-secret  # Contains tls.crt and tls.key
  rules:
  - host: example.com
    ...
```

**Multi-host / Multi-path** examples are common for microservices (e.g., `api.example.com/*` → backend, `app.example.com/*` → frontend).

### IngressClass
```yaml
apiVersion: networking.k8s.io/v1
kind: IngressClass
metadata:
  name: nginx
  annotations:
    ingressclass.kubernetes.io/is-default-class: "true"  # Optional
spec:
  controller: k8s.io/ingress-nginx  # Or other value for different controllers
```

Multiple classes allow co-existence of controllers.

### Ingress Controllers: The Implementers
An **Ingress Controller** watches Ingress (and related) resources, configures a proxy/load balancer (NGINX, Envoy, etc.), and handles traffic. It usually runs as a Deployment + Service (LoadBalancer or NodePort).

**How It Works**:
1. Controller Pod watches API server.
2. On changes, regenerates config (e.g., NGINX `nginx.conf`).
3. Reloads the data plane.
4. Traffic → Controller Pod(s) → Backend Pods (via Services).

### NGINX Ingress Controller (Starting Point)
NGINX-based controllers are popular due to performance, familiarity, and rich features.

**Two Main Options**:
- **Community `ingress-nginx`** (kubernetes/ingress-nginx): Retired March 2026 — avoid new deployments.
- **F5 NGINX Ingress Controller** (nginx/kubernetes-ingress): Actively maintained, supports NGINX Open Source or Plus (enterprise features like WAF, advanced monitoring).

**Installation (Helm - Recommended for F5 NGINX or updated ingress-nginx)**:
```bash
helm repo add nginx-stable https://helm.nginx.com/stable
helm repo update
helm install my-nginx nginx-stable/nginx-ingress --namespace ingress-nginx --create-namespace
```

Or use manifests. For cloud, the controller often pairs with a cloud LoadBalancer.

**Key Configuration Methods** (for NGINX-style):
1. **Annotations** (per-Ingress): `nginx.ingress.kubernetes.io/rewrite-target`, `nginx.ingress.kubernetes.io/ssl-redirect`, rate limiting, auth, canary, etc.
2. **ConfigMap**: Global settings (proxy timeouts, keepalive, log format, etc.).
3. **Custom Templates**: Advanced NGINX config snippets (enable with care).

**Common Annotations** (NGINX):
- `nginx.ingress.kubernetes.io/rewrite-target: /$2`
- `nginx.ingress.kubernetes.io/use-regex: "true"`
- `nginx.ingress.kubernetes.io/canary-weight: "20"` (for canary deployments)
- `nginx.ingress.kubernetes.io/proxy-body-size: "10m"`
- `nginx.ingress.kubernetes.io/auth-type: basic` + secret for auth.

**Advanced**:
- **External Authentication**, **CORS**, **Session Affinity**, **gRPC**, **WebSocket**.
- **TCP/UDP Passthrough** (via ConfigMap or specific resources).
- NGINX Plus: JWT, WAF, active health checks, etc.

**Deployment Best Practices**:
- Multiple replicas + HPA.
- Resource requests/limits.
- `externalTrafficPolicy: Local` for source IP preservation.
- Separate namespace (`ingress-nginx`).
- Monitor with Prometheus + Grafana dashboards.

### Other Popular Controllers
- **Traefik**: Auto-discovery, simple, middleware (rate limit, auth, retries).
- **Contour** (Envoy): High performance, HTTPProxy CRD for advanced routing.
- **HAProxy Ingress**.
- **AWS ALB Ingress Controller**, **GCE**, cloud-specific.
- **Istio, Cilium, Kong**, etc. (often with service mesh capabilities).

### End-to-End Workflow
1. Deploy apps + Services (ClusterIP).
2. Install & configure Ingress Controller (expose via LoadBalancer).
3. Create `IngressClass` if needed.
4. Apply Ingress resources.
5. Verify: `kubectl get ingress`, `kubectl describe ingress`, check controller logs.
6. Test routing, TLS (use `curl -v`), DNS pointing to external IP.
7. Monitor & scale.

**Production Tips**:
- Use cert-manager for TLS (Let's Encrypt).
- Rate limiting, WAF, bot protection.
- Blue/Green or Canary via annotations or advanced CRDs.
- NetworkPolicies for security.
- Logging & observability (access logs, metrics).
- Backup Ingress configs or use GitOps (ArgoCD/Flux).
- Plan migration to Gateway API.

### Troubleshooting
- **No rules working**: Check `ingressClassName`, controller logs, Endpoints populated.
- **502/503**: Backend Pods not ready, port mismatch, selector issues.
- **TLS errors**: Secret format, host matching.
- **Reload loops**: Invalid annotations/config.
- Use `kubectl port-forward` or test from inside cluster.
- Controller-specific debug (e.g., NGINX: `kubectl exec -it ... -- cat /etc/nginx/nginx.conf`).

### Future: Kubernetes Gateway API
Gateway API is the successor — more expressive, role-oriented (GatewayClass, Gateway, HTTPRoute, etc.), better multi-tenancy, and extensible. Many controllers now support it alongside or instead of Ingress.

