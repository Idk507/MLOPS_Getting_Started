**Complete End-to-End Guide to Basic Networking for Kubernetes (TCP/IP, DNS, Ports, Load Balancing) – Updated April 2026**

This guide builds directly on your previous Linux, Docker, YAML, and foundational networking knowledge. It focuses on concepts you'll use **every day** in Kubernetes.

Kubernetes networking follows a simple but powerful model:  
- Every **Pod** gets its own IP address.  
- Pods can communicate with every other Pod without NAT.  
- **Services** provide stable access and load balancing.  
- **CoreDNS** handles service discovery.  
- **Ingress** (or modern Gateway API) manages external HTTP/HTTPS traffic.

**Time to master**: 4–7 days (theory + labs). Practice with Docker Compose first, then Minikube.

---

### 1. TCP/IP Model – Foundation of All Networking (Including Kubernetes)

The **TCP/IP model** (4 layers) is the real-world standard used on the internet and inside Kubernetes clusters:

| Layer              | Responsibility                                      | Key Protocols                  | Kubernetes Example                          |
|--------------------|-----------------------------------------------------|--------------------------------|---------------------------------------------|
| **Application**    | High-level data exchange (your app logic)           | HTTP, HTTPS, DNS, gRPC         | Your microservice APIs                      |
| **Transport**      | End-to-end delivery, ports, reliability             | TCP (reliable), UDP (fast)     | Connections between Pods/Services           |
| **Internet**       | Addressing and routing packets                      | IP (IPv4/IPv6), ICMP           | Pod IPs, Cluster CIDR, routing via CNI      |
| **Network Access** | Physical/hardware transmission                      | Ethernet, Wi-Fi                | Node network interfaces                     |

**How data moves** (encapsulation):  
Application data gets wrapped with Transport header (ports) → IP header (source/dest IP) → Link layer frame.

In Kubernetes:
- CNI plugins (Calico, Cilium, Flannel, etc.) implement the networking layer.
- Pods behave like mini VMs with their own IP and network namespace.

**Key Commands** (review from Linux guide):
```bash
ip addr show          # Interfaces and IPs
ip route              # Routing table
ping 8.8.8.8          # Basic reachability (ICMP)
traceroute google.com # Path of packets
ss -tulnp             # Listening ports and processes
```

---

### 2. TCP vs UDP (Transport Layer – Critical for Services)

| Feature             | TCP                                      | UDP                                      |
|---------------------|------------------------------------------|------------------------------------------|
| Connection          | Yes (3-way handshake: SYN → SYN-ACK → ACK) | No                                       |
| Reliability         | Guaranteed delivery, ordering, retransmission | Best-effort (no guarantees)              |
| Speed               | Slower (acknowledgments)                 | Faster                                   |
| Use in K8s          | Most services (HTTP, databases)          | DNS queries, some metrics                |

Almost all Kubernetes application traffic uses **TCP**. DNS inside the cluster uses both TCP and UDP on port 53.

---

### 3. Ports – How Applications Are Identified

Ports (0–65535) allow multiple applications to run on the same IP.

**Categories**:
- 0–1023: Well-known (privileged, e.g., 80 for HTTP)
- 1024–49151: Registered
- 49152–65535: Ephemeral (client-side temporary ports)

**Must-Know Ports in Kubernetes (2026)**:

| Port          | Protocol | Component                          | Purpose                                      |
|---------------|----------|------------------------------------|----------------------------------------------|
| 80 / 443      | TCP      | HTTP / HTTPS                       | Web apps, Ingress default                    |
| 53            | UDP/TCP  | CoreDNS                            | Service discovery inside cluster             |
| 6443          | TCP      | kube-apiserver                     | kubectl and control plane communication      |
| 10250         | TCP      | kubelet                            | Node agent (API server talks to it)          |
| 30000–32767   | TCP      | NodePort Services                  | External access via node IPs                 |

**In Docker**:
```bash
docker run -p 8080:80 nginx   # Host port 8080 → Container port 80
```

**In Kubernetes**:
- `containerPort` in Pod spec: Just documentation (the app must actually listen on it).
- Service `port` and `targetPort`: Mapping logic.

Check ports on a node:
```bash
ss -tulnp | grep -E '6443|10250'
```

---

### 4. DNS – Service Discovery in Kubernetes

DNS translates names → IPs.

**How DNS Works (High-Level)**:
1. App asks for `google.com`.
2. Local resolver → Recursive resolver (e.g., 8.8.8.8) → Root → TLD → Authoritative server → Returns IP (A/AAAA record).
3. Result cached with TTL.

**In Kubernetes**:
- **CoreDNS** runs as a Deployment and provides cluster-internal DNS.
- Every Service gets a DNS name: `<service-name>.<namespace>.svc.cluster.local`
- Pods can also get DNS names (but less commonly used).
- Example: A Service named `postgres` in namespace `default` is reachable as `postgres.default.svc.cluster.local` or simply `postgres` (from same namespace).

This enables **stable service discovery** even when Pods restart with new IPs.

Test inside a cluster (later with Minikube):
```bash
nslookup postgres.default.svc.cluster.local
curl postgres:5432
```

---

### 5. Load Balancing in Kubernetes

Load balancing distributes traffic across multiple backend instances (Pods) for scalability and availability.

**Kubernetes Service** = Built-in load balancer + stable endpoint.

**Service Types** (most important for you):

| Service Type     | Scope              | How It Works                                                                 | Use Case                              |
|------------------|--------------------|------------------------------------------------------------------------------|---------------------------------------|
| **ClusterIP**    | Internal only      | Virtual IP (ClusterIP) + DNS name. kube-proxy load balances to Pods.         | Pod-to-Pod communication (default)    |
| **NodePort**     | External           | Exposes Service on every node’s IP at a high port (30000–32767).             | Quick external access, testing        |
| **LoadBalancer** | External           | Provisions a real cloud load balancer (AWS ELB, GCP, Azure, etc.).           | Production external traffic           |
| **ExternalName** | External mapping   | Maps Service to an external DNS name (no proxying).                          | Integrate external databases          |

**How Load Balancing Works Internally**:
- When you create a Service, it selects Pods using **labels** (`selector`).
- **kube-proxy** (runs on every node) watches Services and sets up rules (iptables, IPVS, or eBPF in modern CNIs).
- Traffic to the Service’s ClusterIP is distributed (default: round-robin) to healthy Pods.
- **Headless Service** (`clusterIP: None`): No load balancing, returns all Pod IPs directly (useful for StatefulSets).

**Layer 4 vs Layer 7**:
- **L4** (Services): TCP/UDP level (IP + port). Simple and fast.
- **L7** (Ingress / Gateway API): Understands HTTP (paths, hosts, headers). Supports TLS termination, routing rules, canary deployments.

**Ingress** (still widely used in 2026):
- Defines HTTP/HTTPS routing rules.
- Requires an **Ingress Controller** (NGINX, Traefik, Contour, or modern Gateway API implementations).
- Example: Route `app.example.com/api` → one Service, `app.example.com/web` → another.

**Modern Alternative**: **Gateway API** (more expressive, role-based, progressing toward GA).

---

### 6. Kubernetes Networking Model Summary (2026)

Kubernetes defines four requirements:
1. Every Pod gets a unique IP (no NAT between Pods).
2. Pods on a node can communicate with all Pods on other nodes.
3. The IP a Pod sees for itself is the same others see.
4. Services provide stable discovery + load balancing.

This is implemented by a **CNI plugin** (Container Network Interface). Popular ones: Calico, Cilium (eBPF-based, very performant in 2026), Flannel.

---

### 7. Hands-On Labs (Do These Now)

**Lab 1: Docker Networking Basics**
- Run two containers in the same Docker network.
- Use service names as hostnames (similar to Kubernetes DNS).
- Check ports with `ss`.

**Lab 2: Simulate Services**
- Run multiple NGINX containers.
- Use a simple script or `curl` loop to hit them and observe load distribution.

**Lab 3: Docker Compose Multi-Container**
- Create `compose.yaml` with `web` and `db` services.
- Access `db` from `web` using the service name (`db:5432`).
- Add a third service and test internal DNS-like resolution.

**Lab 4: Port Exploration**
- Run services on different ports.
- Use `ss -tulnp` and `curl` to verify.

**Lab 5: Prepare for K8s**
- Write a YAML for a simple Service (ClusterIP) + Deployment (you’ll apply it soon in Minikube).

---

### 8. Common Troubleshooting Commands

```bash
kubectl get svc                  # List Services and their ClusterIPs
kubectl describe svc my-service  # Endpoints and selectors
kubectl get endpoints            # Which Pods are backing the Service
ss -tulnp | grep kube-proxy      # On nodes
dig my-service.default.svc.cluster.local   # Inside a Pod
```

---



