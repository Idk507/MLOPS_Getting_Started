**Kubernetes Architecture: Control Plane, Worker Nodes, and Pods**  
**(Detailed Overview – Kubernetes v1.35.x, April 2026)**

This is **Phase 1** of your Kubernetes roadmap. Understanding the architecture is crucial because it explains **how** Kubernetes achieves orchestration, scaling, and self-healing you learned earlier.

A Kubernetes **cluster** consists of two main parts:
- **Control Plane** (also called master or head node) — The brain of the cluster.
- **Worker Nodes** — The muscles that actually run your applications.

Everything revolves around **Pods** — the smallest deployable unit.
<img width="2000" height="1465" alt="image" src="https://github.com/user-attachments/assets/ab0c21ca-deb9-4e35-a746-f4e7f63d7190" />


### High-Level Kubernetes Architecture (2026 View)

```
External Users / kubectl / CI/CD
          ↓ (HTTPS on port 6443)
     kube-apiserver (Control Plane)
          ↓ (watches & updates)
     etcd (cluster state database)

Control Plane Components:
- kube-scheduler
- kube-controller-manager
- (optional) cloud-controller-manager

          ↓ (scheduling decisions)
Worker Nodes (multiple)
- kubelet (agent)
- Container Runtime (containerd by default)
- kube-proxy (networking)
- Pods (your apps)
```

The **Control Plane** runs the global cluster state and decision-making.  
**Worker Nodes** execute the workloads.  
In production (HA setups), the Control Plane is replicated across 3+ nodes for high availability. For learning, Minikube or Kind runs a single-node or multi-node setup.
<img width="1024" height="698" alt="image" src="https://github.com/user-attachments/assets/7e818a16-b4f6-48a8-88f6-c52ae53d1aed" />

### 1. Control Plane Components

The Control Plane manages the **desired state** of the entire cluster. All interactions go through the **API Server**.

#### a) **kube-apiserver** (The Front Door / Heart of the Cluster)
- Exposes the Kubernetes **HTTP REST API** (port 6443 by default).
- **kubectl**, dashboards, controllers, and external tools **only** talk to the API Server — never directly to etcd or other components.
- Validates requests, authenticates/authorizes users, and persists objects to etcd.
- Handles admission control, conversion between API versions, and watches for changes.
- In v1.35, it includes improvements in certificate validation and node feature enforcement.

**Key Role**: Single point of entry. Everything is declarative — you send YAML/JSON to the API Server via `kubectl apply`.

#### b) **etcd** (The Source of Truth / Cluster Database)
- A highly-available, distributed **key-value store** (consistent and strongly consistent).
- Stores **all cluster state**: Pods, Deployments, Services, Nodes, ConfigMaps, Secrets, etc.
- Everything the API Server reads/writes goes here.
- Uses Raft consensus for high availability (odd number of etcd instances recommended: 3 or 5).
- Data is critical — always back it up (tools like Velero later).

**Tip**: Never lose etcd data — it's the brain's memory.

#### c) **kube-scheduler** (The Matchmaker)
- Watches the API Server for newly created **Pods** that have no `nodeName` assigned (unscheduled Pods).
- Scores candidate nodes based on many factors:
  - Resource requirements (CPU/memory requests/limits)
  - Node affinity/anti-affinity, taints/tolerations
  - Topology spread constraints
  - Data locality, pod affinity, custom policies
  - In v1.35: New alpha "node declared features" helps avoid scheduling Pods on incompatible nodes.
- Binds the Pod to the best node (updates the Pod object in etcd via API Server).

**Key Role**: Decides **where** a Pod should run. Smart scheduling prevents resource waste and ensures constraints are met.

#### d) **kube-controller-manager** (The Reconciliation Engine)
- Runs multiple **controllers** as a single process (or multiple in HA).
- Each controller watches the API Server for objects and reconciles **actual state** → **desired state**.
- Important controllers:
  - **ReplicaSet / Deployment controller** — Maintains the correct number of Pods.
  - **Node controller** — Monitors node health.
  - **Endpoints controller** — Populates Service endpoints.
  - **Job controller**, **Namespace controller**, etc.
- This is where **self-healing** and **scaling** happen continuously.

**Cloud Controller Manager** (optional, in cloud environments):
- Handles cloud-specific logic (load balancers, node lifecycle, persistent volumes) so the core control plane stays cloud-agnostic.

**Control Plane Summary**:  
API Server + etcd = state & communication.  
Scheduler = placement decisions.  
Controller Manager = continuous reconciliation (the magic behind self-healing).

### 2. Worker Nodes (Node Components)
<img width="1710" height="1179" alt="image" src="https://github.com/user-attachments/assets/33cf6cc3-3b5d-46c0-b4af-01e0b27e6ab3" />

Worker nodes run your actual containerized workloads.

#### a) **kubelet** (The Node Agent)
- The primary Kubernetes agent running on **every** node (including control plane nodes in single-node setups).
- Registers the node with the API Server.
- Watches the API Server for Pods scheduled to this node.
- Pulls the container image, starts/stops containers via the container runtime.
- Reports node and Pod status, metrics, and health back to the control plane.
- Enforces resource limits, restarts failed containers (based on restartPolicy), and runs probes (liveness/readiness/startup).
- In v1.35: Enhanced features around Pod restarts and node feature declaration.

**Key Role**: Makes sure the Pods assigned to this node are actually running as desired.

#### b) **Container Runtime** (Where Containers Actually Run)
- Default in modern Kubernetes: **containerd** (lightweight, CRI-compliant).
- Others: CRI-O, Docker (via dockershim — deprecated long ago).
- kubelet talks to the runtime using the **Container Runtime Interface (CRI)**.

#### c) **kube-proxy** (Networking Glue)
- Runs on every node.
- Maintains network rules (using iptables, IPVS, or eBPF in modern CNIs) so that:
  - Services get stable virtual IPs and DNS names.
  - Traffic to a Service is load-balanced to the correct Pods.
- Implements most of the Kubernetes **Service** abstraction.

**Note**: The actual Pod-to-Pod networking across nodes is handled by a **CNI plugin** (Calico, Cilium, Flannel, etc.) — not by core Kubernetes.

### 3. Pods – The Smallest Deployable Unit

A **Pod** is the atomic unit in Kubernetes:
- One or more tightly coupled containers (usually just one).
- Shares the same:
  - Network namespace (same IP address, same localhost).
  - Storage volumes (can share data easily).
  - IPC namespace, etc.
- Has its own **Pod IP** (ephemeral — changes if Pod restarts).
- Defined in YAML with `kind: Pod` or created by higher-level controllers (Deployment, StatefulSet, etc.).

**Why Pods instead of individual containers?**
- Multi-container Pods solve sidecar use cases (logging, proxy, monitoring).
- Kubernetes schedules, restarts, and manages at Pod level, not container level.

**Pod Lifecycle**:
- Pending → Scheduling → Running → Succeeded/Failed.
- Self-healing: If a container dies, kubelet restarts it (or the controller creates a new Pod).

### How Everything Works Together (The Reconciliation Loop)

1. You run `kubectl apply -f deployment.yaml` → API Server validates and stores in etcd.
2. Controller Manager sees the desired replicas → creates Pod objects.
3. Scheduler watches unscheduled Pods → assigns them to nodes.
4. kubelet on the target node sees the Pod → pulls image and starts containers via containerd.
5. kube-proxy sets up networking rules.
6. If anything fails (Pod crashes, node dies), controllers notice the mismatch and fix it automatically.

This **watch + reconcile** pattern is the core of Kubernetes' power.

### Quick Comparison Table

| Component              | Layer          | Runs On          | Main Responsibility                     | Key Interaction                  |
|------------------------|----------------|------------------|-----------------------------------------|----------------------------------|
| kube-apiserver        | Control Plane  | Control nodes    | API entry point, validation             | All components talk to it        |
| etcd                  | Control Plane  | Control nodes    | Persistent cluster state                | Only API Server reads/writes     |
| kube-scheduler        | Control Plane  | Control nodes    | Pod placement decisions                 | Watches API for unbound Pods     |
| kube-controller-manager | Control Plane | Control nodes    | Reconciliation loops (self-healing)     | Watches and updates via API      |
| kubelet               | Worker         | Every node       | Runs Pods, reports status               | Talks to API & container runtime |
| kube-proxy            | Worker         | Every node       | Service networking & load balancing     | Watches Services/Endpoints       |
| Pod                   | Workload       | Worker nodes     | Smallest unit running your containers   | Scheduled by control plane       |


You now understand **why** Kubernetes works the way it does.

**Recommended Hands-on (Do This Next)**:
1. Install **Minikube** (easiest for beginners) or **Kind**.
2. Start a cluster and explore components with:
   ```bash
   kubectl get nodes
   kubectl get pods -n kube-system
   kubectl describe node <node-name>
   ```
   <img width="1463" height="116" alt="image" src="https://github.com/user-attachments/assets/dd60fb17-9f15-4cda-bcb5-934eab0b3324" />



Or do you want to continue with **Core Kubernetes Objects** (Pods, Deployments, Services) first?

You're making great progress, Dhanush — this architecture knowledge will make every future concept (Deployments, Services, etc.) click much faster. Let me know what you want next! 🚀
