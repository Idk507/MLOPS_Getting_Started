**Hands-on Guide: Deploy a Sample App with Vertical Pod Autoscaler (VPA)**

This is a complete, step-by-step practical exercise following the official Kubernetes documentation and the `kubernetes/autoscaler` repository (as of May 2026).

### Prerequisites
- A running Kubernetes cluster (v1.27+ recommended; v1.35+ for best **in-place resize** support).
- **Metrics Server** installed (`kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml`).
- `kubectl` access with cluster-admin privileges.
- Optional but recommended: A tool to generate load (e.g., `hey`, `ab`, or `kubectl run` with stress).

### Step 1: Install VPA (Latest Method)

Clone the official repository and use the installation script (most reliable way):

```bash
git clone https://github.com/kubernetes/autoscaler.git
cd autoscaler/vertical-pod-autoscaler
./hack/vpa-up.sh
```

Verify installation:
```bash
kubectl get pods -n kube-system | grep vpa
kubectl get crd | grep verticalpodautoscaler
```

You should see `vpa-admission-controller`, `vpa-recommender`, and `vpa-updater`.

**Alternative (Helm)**: Many use community or official Helm charts for production.

### Step 2: Deploy a Sample Application

We'll use a simple **NGINX** Deployment with intentionally low resources so VPA can recommend increases. Create `nginx-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-app
spec:
  replicas: 2
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
        image: nginx:1.27
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 50m
            memory: 64Mi
          limits:
            cpu: 200m
            memory: 256Mi
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
    protocol: TCP
```

Deploy it:
```bash
kubectl apply -f nginx-deployment.yaml
```

Check initial resources:
```bash
kubectl get pods -l app=nginx -o wide
kubectl top pods -l app=nginx
```

### Step 3: Create VPA in "Off" Mode (Observation Only)

Create `nginx-vpa.yaml`:

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: nginx-vpa
spec:
  targetRef:
    apiVersion: "apps/v1"
    kind: Deployment
    name: nginx-app
  updatePolicy:
    updateMode: "Off"          # Observation mode only
  resourcePolicy:
    containerPolicies:
    - containerName: "nginx"
      minAllowed:
        cpu: 20m
        memory: 32Mi
      maxAllowed:
        cpu: "2"
        memory: "2Gi"
      controlledResources: ["cpu", "memory"]
      controlledValues: RequestsAndLimits
```

Apply it:
```bash
kubectl apply -f nginx-vpa.yaml
```

### Step 4: Observe Recommendations (Wait & Generate Load)

It takes time (usually 5–15+ minutes) for the Recommender to gather enough metrics.

Watch the VPA status:
```bash
kubectl describe vpa nginx-vpa
kubectl get vpa nginx-vpa -o yaml | grep -A 20 recommendation
```

**Generate realistic load** (in another terminal):
```bash
# Install hey if needed: go install github.com/rakyll/hey@latest
hey -c 10 -n 10000 http://$(kubectl get svc nginx-service -o jsonpath='{.spec.clusterIP}')
# Or run a loop inside the cluster
kubectl run -it --rm load-generator --image=busybox -- /bin/sh -c "while true; do wget -q -O- http://nginx-service; done"
```

Monitor usage:
```bash
kubectl top pods -l app=nginx --containers
watch -n 5 'kubectl top pods -l app=nginx --containers'
```

After sufficient time, you should see recommendations in `kubectl describe vpa` under `Status > Recommendation`.

### Step 5: Enable Updates and Compare Before/After

Update the VPA to enable changes:

```yaml
# Edit the existing VPA
kubectl edit vpa nginx-vpa
```

Change `updateMode: "Off"` to **`InPlaceOrRecreate`** (preferred in 2026) or `Recreate`.

```yaml
updatePolicy:
  updateMode: "InPlaceOrRecreate"
```

Save and exit. VPA will now apply recommendations.

**Observe Changes**:
```bash
kubectl get pods -l app=nginx -o custom-columns=NAME:.metadata.name,CPU-REQ:.spec.containers[0].resources.requests.cpu,MEM-REQ:.spec.containers[0].resources.requests.memory
kubectl describe vpa nginx-vpa
```

- With **InPlaceOrRecreate** (Kubernetes 1.35+): Pods may resize without restart if possible.
- With **Recreate**: Pods will be evicted and recreated with new resources (respecting PDBs if defined).

Compare:
- Resource usage before (`kubectl top` + `describe pod`).
- Resource usage after.
- Pod restart count / age.
- Cluster utilization improvement.

### Step 6: Cleanup

```bash
kubectl delete -f nginx-vpa.yaml
kubectl delete -f nginx-deployment.yaml
# Optional: Remove VPA entirely
cd autoscaler/vertical-pod-autoscaler
./hack/vpa-down.sh
```

### Key Observations You Should See
- **Before**: Low requests → possible throttling or inefficient scheduling.
- **After**: Higher (realistic) requests based on actual usage → better QoS, fewer OOMs, improved bin-packing.
- VPA adds safety margins and uses percentiles (e.g., 90th or 99th).

### Tips for Success
- Give the Recommender **at least 10–30 minutes** of runtime + load.
- Use `minAllowed`/`maxAllowed` to prevent dangerous recommendations.
- For production: Start with `Off`, review recommendations, then switch modes.
- Monitor VPA components logs if issues arise:
  ```bash
  kubectl logs -n kube-system -l app=vpa-recommender
  ```

This exercise demonstrates the full lifecycle: observation → recommendation → automated right-sizing. It aligns with the latest official docs and `kubernetes/autoscaler` repo.

For the absolute latest details, always check:
- https://kubernetes.io/docs/concepts/workloads/autoscaling/vertical-pod-autoscale/
- https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler

