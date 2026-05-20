**Vertical Pod Autoscaler (VPA)** automatically adjusts CPU and memory **requests** (and often **limits**) for containers in Pods based on observed historical and real-time usage. It helps "right-size" workloads, improving resource utilization, reducing costs, and preventing OOMKills or throttling.

Unlike **Horizontal Pod Autoscaler (HPA)**, which adds/removes Pod replicas, VPA changes the resource *requests/limits* of existing Pods (vertically).

### Why Use VPA?
- Eliminates guesswork in setting resource requests/limits.
- Improves bin-packing and cluster efficiency.
- Reduces over-provisioning (cost savings) and under-provisioning (crashes).
- Works well for workloads with unpredictable or evolving resource needs (e.g., Java apps with GC, ML inference, stateful services).
- Complements HPA when used carefully (different metrics).

**Key 2026 Updates**:
- In-place Pod vertical resizing reached GA in Kubernetes ~1.35.
- VPA supports `InPlaceOrRecreate` mode (attempt live resize, fallback to restart).
- `Auto` mode is deprecated (alias for `Recreate` in newer versions).

### VPA Components (Architecture)

VPA consists of three main controllers (deployed as Deployments):

1. **Recommender**:
   - Collects metrics (via Metrics Server or custom metrics).
   - Analyzes usage history (CPU/memory histograms).
   - Computes recommendations (target, lower/upper bounds) using percentiles + safety margins.
   - Stores recommendations in the `VerticalPodAutoscaler` object.

2. **Updater** (or Admission Controller interaction):
   - Decides when and how to apply recommendations.
   - Evicts Pods (for Recreate) or triggers in-place resize.

3. **Admission Controller** (Webhook):
   - Mutating webhook that injects recommended resources into new or recreated Pods.
   - Ensures Pods are created with the right sizes.

All components run in the `kube-system` or a dedicated namespace.

### VPA Update Modes (Critical Choice)

Configure via `.spec.updatePolicy.updateMode`:

| Mode                | Applies to New Pods | Applies to Running Pods | Disruption          | Best For                          | Notes |
|---------------------|---------------------|-------------------------|---------------------|-----------------------------------|-------|
| **Off**             | No                  | No                      | None                | Observation, dry-run, manual     | Safest starting point |
| **Initial**         | Yes                 | No                      | None                | Batch jobs, CronJobs, stateful   | Sets once at creation |
| **Recreate**        | Yes                 | Yes (evict)             | Pod restart         | Most production workloads        | Respects PDBs |
| **InPlaceOrRecreate**| Yes                | Yes (prefer in-place)   | Minimal / Restart   | Modern clusters (K8s 1.27+)      | Best balance in 2026 |

**Recommendation**: Start with `Off`, observe for days/weeks, then move to `Initial` or `InPlaceOrRecreate`.

### VPA Resource Object (YAML Example)

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: my-app-vpa
  namespace: production
spec:
  targetRef:
    apiVersion: "apps/v1"
    kind: Deployment          # or StatefulSet, DaemonSet, etc.
    name: my-app
  updatePolicy:
    updateMode: "InPlaceOrRecreate"   # or "Off", "Initial", "Recreate"
  resourcePolicy:
    containerPolicies:
    - containerName: "*"          # or specific container name
      minAllowed:
        cpu: 100m
        memory: 256Mi
      maxAllowed:
        cpu: "4"
        memory: 8Gi
      controlledResources: ["cpu", "memory"]
      controlledValues: RequestsAndLimits  # or RequestsOnly
```

**Key Fields**:
- `targetRef`: Which workload to manage.
- `resourcePolicy`: Per-container min/max bounds and controls.
- Multiple recommenders possible in advanced setups.

### Installation (2026)

```bash
# Official way (check latest release)
git clone https://github.com/kubernetes/autoscaler.git
cd vertical-pod-autoscaler
./hack/vpa-up.sh
```

Or use Helm charts (popular in production). Verify with:
```bash
kubectl get pods -n kube-system | grep vpa
kubectl get crd | grep verticalpodautoscaler
```

Requires **Metrics Server** (or equivalent) for usage data.

### How VPA Works End-to-End

1. Deploy VPA components.
2. Create a VPA CR targeting your Deployment/StatefulSet.
3. Recommender observes usage (collects histograms over time).
4. Recommendations generated periodically.
5. Depending on mode:
   - Admission webhook applies on Pod creation.
   - Updater evicts Pods (or resizes in-place) when deviation is significant.
6. New Pods get updated resources → better scheduling and runtime behavior.

VPA also creates **Checkpoints** for persisting historical data.

### VPA + HPA Integration

**General Rule**: Avoid using both on the same resource (CPU/memory) on the same workload — leads to conflicts and oscillation.

**Safe Patterns**:
- VPA for memory + HPA for CPU.
- VPA in `Off` mode (recommendations only) + HPA for scaling.
- VPA for baseline right-sizing + HPA for burst traffic.

### Best Practices (2026)

1. **Start Safe**: Always begin with `updateMode: Off`. Review recommendations with `kubectl describe vpa`.
2. **Set Bounds**: Use `minAllowed`/`maxAllowed` to prevent extreme recommendations.
3. **Observe First**: Run for 7–14 days before enabling updates.
4. **Use with PDBs**: Protect against mass evictions.
5. **Stateful Workloads**: Prefer `Initial` or careful `InPlaceOrRecreate`.
6. **Multiple VPAs**: Possible but avoid overlapping targets.
7. **Monitoring**: Track VPA status, recommendations, eviction events, and resource utilization.
8. **In-Place Resizing**: Leverage on supported clusters for zero-disruption scaling.
9. **Combine with Cluster Autoscaler / Karpenter**: VPA improves packing → better node utilization.
10. **Policy Enforcement**: Use Kyverno/Gatekeeper to enforce VPA usage.

### Limitations & Considerations

- **Disruption**: Recreate mode causes Pod restarts (downtime for single-replica apps).
- **Short-lived Pods**: Insufficient history for good recommendations.
- **Metric Scope**: Primarily CPU/memory (not custom metrics natively).
- **Not for All Workloads**: Avoid for DaemonSets or highly bursty short jobs.
- **Feedback Loops**: Aggressive scaling can cause oscillation (mitigated by bounds and safety margins).
- **In-Place Support**: Requires recent Kubernetes + VPA versions; not universal yet.

### Troubleshooting

- **No Recommendations**: Check Metrics Server, VPA Recommender logs, Pod age.
- **Pods Not Updating**: Wrong `updateMode`, PDB blocking, Admission Controller not running.
- **Pending Pods**: Recommendations too high for node capacity.
- **Commands**:
  ```bash
  kubectl describe vpa my-app-vpa
  kubectl get vpa
  kubectl logs -n kube-system -l app=vpa-recommender
  ```

### End-to-End Workflow

1. Install Metrics Server + VPA.
2. Deploy application with conservative requests.
3. Create VPA in `Off` mode.
4. Monitor usage and recommendations for sufficient time.
5. Adjust bounds → switch to `InPlaceOrRecreate` or `Recreate`.
6. Integrate with GitOps, monitoring, and alerting.
7. Review periodically (VPA adapts to changing workloads).

**VPA** is a mature, powerful tool for resource optimization in 2026, especially with in-place resizing. It shines for long-running, memory-heavy, or variable workloads where manual tuning is painful. Combine thoughtfully with HPA for comprehensive autoscaling.

