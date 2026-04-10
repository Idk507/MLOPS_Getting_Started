**Kubernetes Architecture Deep Dive with Diagrams**  
**(Kubernetes v1.35.x – April 2026)**

Here are clean, accurate diagrams that show the complete architecture. I'll explain each one step-by-step so you build a strong mental model.

### 1. High-Level Kubernetes Cluster Overview


<img width="824" height="524" alt="image" src="https://github.com/user-attachments/assets/065ed337-d950-4c2a-8a7b-fc12f95d6de2" />


**Explanation of this diagram:**

- **Left side (Control Plane)**: This is the **brain** of the cluster.
  - **kube-apiserver** sits in the center — it is the **only entry point**. Every request from `kubectl`, controllers, or external systems goes through it.
  - **etcd** (key-value store) is connected to the API Server — it holds the **entire desired state** of the cluster (all Pods, Services, Deployments, etc.).
  - **kube-scheduler** decides **where** new Pods should run.
  - **kube-controller-manager** runs reconciliation loops (self-healing, scaling, etc.).
  - **cloud-control-manager** (optional) handles cloud-specific tasks.

- **Right side (Worker Nodes)**: Multiple nodes (Node 1, Node 2, etc.).
  - Each node runs:
    - **kubelet** — the agent that manages Pods on that node.
    - **kube-proxy** — handles networking and load balancing for Services.
    - **Container Runtime Interface (CRI)** — usually **containerd** — actually runs the containers.
  - **Pods** (small blue boxes) live here. Each Pod contains one or more containers.

- **Communication flow**:
  - All components talk **only through the API Server** (using mTLS for security).
  - kubelet watches the API Server for Pods assigned to its node and starts them.
  - The Control Plane continuously reconciles the actual state with your declared YAML.

This diagram clearly shows the separation: **Control Plane = Decision & State**, **Worker Nodes = Execution**.

### 2. Another Clean View – Control Plane vs Worker Nodes

<img width="820" height="447" alt="image" src="https://github.com/user-attachments/assets/8614335a-a5a0-48f7-afd1-6b0dbefea0a4" />



**Explanation of this diagram:**

- **Left (Control Plane)**:
  - **API Server** is the central hub (yellow box).
  - **Scheduler** and **Controller Manager** connect to it.
  - **etcd** (distributed key-value store) stores everything.
  - User (`kubectl`) and Cloud Provider talk to the API Server.

- **Right (Worker Nodes)**:
  - Multiple nodes shown.
  - On each node:
    - **kubelet**
    - **kube-proxy**
    - **Container Runtime**
    - Multiple **Pods** (each containing containers)

- Dashed lines show communication flow from the API Server to the nodes.

This is one of the clearest modern diagrams. Notice how **Pods** are shown as the workload units running on the nodes, managed by kubelet.

### Key Components Explained with the Diagrams

**Control Plane Components** (Brain – usually runs on dedicated nodes):

1. **kube-apiserver**
   - The **front door**. All CRUD operations (create, read, update, delete) for Kubernetes objects go here.
   - Validates YAML, authenticates users, and writes to etcd.
   - Runs on port **6443** (HTTPS).

2. **etcd**
   - The **database** of the cluster.
   - Stores the complete cluster state in a consistent way.
   - Critical: If etcd is down or data is lost, the cluster loses its memory.

3. **kube-scheduler**
   - Watches for unscheduled Pods.
   - Scores nodes based on resources (CPU/memory requests), affinity, taints, topology spread, etc.
   - Assigns the best node to the Pod.

4. **kube-controller-manager**
   - Runs many **controllers** (Deployment controller, ReplicaSet controller, etc.).
   - Continuously checks: "Is the actual state matching the desired state?"
   - This loop enables **self-healing** and **autoscaling**.

**Worker Node Components** (Muscles):

1. **kubelet**
   - The Kubernetes **agent** on every node.
   - Takes Pods assigned by the scheduler and tells the container runtime to start them.
   - Monitors container health, runs probes, reports status back to the API Server.

2. **Container Runtime** (containerd by default)
   - Actually starts and stops containers inside Pods.

3. **kube-proxy**
   - Sets up networking rules so **Services** can load-balance traffic to Pods.

**Pods**
   - The smallest deployable unit.
   - One or more containers that share network and storage.
   - Ephemeral — they can be killed and recreated anywhere.

### How the Whole System Works Together (The Magic)

1. You run `kubectl apply -f deployment.yaml` → request hits **API Server**.
2. API Server stores the object in **etcd**.
3. **Controller Manager** sees the new Deployment and creates Pod objects.
4. **Scheduler** assigns Pods to suitable **Worker Nodes**.
5. **kubelet** on the chosen node starts the containers via the **container runtime**.
6. **kube-proxy** makes the Pods reachable via Services.
7. If a Pod crashes → kubelet restarts it, or the controller creates a replacement → **self-healing**.

This **watch + reconcile** pattern is what makes Kubernetes powerful and resilient.

### Quick Reference Table (From the Diagrams)

| Component                  | Location          | Primary Responsibility                        |
|---------------------------|-------------------|-----------------------------------------------|
| kube-apiserver            | Control Plane     | Single API entry point, validation            |
| etcd                      | Control Plane     | Persistent storage of all cluster state       |
| kube-scheduler            | Control Plane     | Pod placement (scheduling)                    |
| kube-controller-manager   | Control Plane     | Reconciliation loops (self-healing)           |
| kubelet                   | Every Worker Node | Run & monitor Pods on the node                |
| kube-proxy                | Every Worker Node | Service networking & load balancing           |
| Container Runtime         | Every Worker Node | Execute containers                            |
| Pod                       | Worker Nodes      | Smallest unit (1+ containers)                 |

You now have a solid visual and conceptual understanding of Kubernetes architecture.


Or do you want the **Minikube/Kind installation guide** first so you can explore these components live on your machine?

Just tell me, Dhanush — you're progressing very well! 🚀
