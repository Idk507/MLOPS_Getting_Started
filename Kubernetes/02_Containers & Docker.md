**Complete End-to-End Containers & Docker Mastery (Dockerfile, Images, Containers, Volumes, Networking, Docker Compose) – 2026 Edition**

**Latest as of March 27, 2026**:  
- **Docker Engine**: v29.3.1 (released March 25, 2026)  
- **Docker Desktop**: v4.66.1 (includes Engine 29.3.1)  
- **Docker Compose**: v2 (integrated as `docker compose` plugin — the only supported way now)

**Why this matters for Kubernetes**  
Kubernetes orchestrates **containers**, not VMs. Docker is the easiest way to build, test, and understand containers locally. (Production Kubernetes uses containerd directly, but every developer still uses Docker daily for local dev, testing manifests, and building images.)

**Time commitment**: 5–10 days (3–5 hours/day + heavy practice).  
**Environment**: Ubuntu 24.04 LTS (or your existing Linux setup from previous guide). If on Windows/Mac → install **Docker Desktop**.

---

### 1. What Are Containers? (Containers vs Virtual Machines)

| Aspect              | Virtual Machine (VM)                  | Container                              |
|---------------------|---------------------------------------|----------------------------------------|
| Size                | GBs (full OS)                         | MBs (only app + dependencies)          |
| Boot time           | Minutes                               | Milliseconds                           |
| Resource usage      | High (emulates full hardware)         | Low (shares host kernel)               |
| Portability         | Good                                  | Excellent (build once, run anywhere)   |
| Isolation           | Full (hypervisor)                     | Process + namespace isolation          |

**Containers = lightweight, portable, isolated application packages.**

They use Linux kernel features:
- **Namespaces** (isolate processes, network, mounts)
- **cgroups** (limit CPU/memory)
- **Union filesystem** (layers for images)

**Docker** is the most popular tool to build and run containers.

---

### 2. Docker Architecture (High-Level)

```
Docker Client (CLI)  ←→  Docker Daemon (dockerd)
                               │
                               ▼
                     containerd + runc
                               │
                               ▼
                     Images ←→ Registry (Docker Hub)
```

- **Docker CLI** (`docker` command) → you interact with this.
- **Docker Daemon** (`dockerd`) → manages containers on your machine.
- **containerd** → modern lightweight runtime (Docker uses it internally since 2017).
- **Registry** → Docker Hub (or private like Harbor, ECR).

---

### 3. Installation (Ubuntu 24.04+)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker Engine (official 2026 method)
sudo apt install ca-certificates curl -y
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y

# Add your user to docker group (no sudo needed)
sudo usermod -aG docker $USER
newgrp docker   # or log out & back in

# Verify
docker --version          # Should show Docker Engine v29.3.1
docker compose version    # v2.x
```

Test: `docker run hello-world`

---

### 4. Docker Images (The Blueprint)

An **image** is a read-only template (like a ZIP of your app + OS layers).

**Commands**:
```bash
docker pull nginx:alpine                  # download from Docker Hub
docker images                             # list images
docker image ls -q                        # only IDs
docker rmi nginx:alpine                   # remove
docker pull ghcr.io/user/myimage:latest   # from GitHub Container Registry
```

**Image layers**: Every `RUN`, `COPY`, `ADD` creates a layer (cached for fast rebuilds).

---

### 5. Dockerfile – How to Build Your Own Images (2026 Best Practices)

A `Dockerfile` is a text file with instructions to build an image.

**Modern 2026 Best Practices**:
- Use **multi-stage builds** (tiny final image)
- Start with minimal base (`alpine`, `slim`, `distroless`)
- Non-root user (`USER 1000`)
- `.dockerignore` file (ignore `node_modules`, `.git`, etc.)
- Cache efficiently (copy package files first)
- Scan images with `docker scout` or Trivy

**Complete Example: Node.js App (2026 standard)**

Create `Dockerfile`:
```dockerfile
# Stage 1: Build
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Stage 2: Runtime (tiny final image)
FROM node:22-alpine
WORKDIR /app
RUN addgroup -g 1001 -S nodejs && \
    adduser -S -u 1001 nodejs
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
USER 1001
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

**Build & Run**:
```bash
docker build -t myapp:v1 .                  # build
docker build --no-cache -t myapp:v2 .       # force rebuild
docker run -d -p 3000:3000 --name myapp myapp:v1
docker logs myapp -f
```

**Full Dockerfile Reference (most used instructions)**:

| Instruction     | Purpose                              | 2026 Tip                          |
|-----------------|--------------------------------------|-----------------------------------|
| `FROM`          | Base image                           | Use `:alpine` or `:slim`          |
| `WORKDIR`       | Set working directory                | Always use                        |
| `COPY` / `ADD`  | Copy files                           | Prefer `COPY`; use `--chmod`      |
| `RUN`           | Execute during build                 | Combine commands with `&&`        |
| `ENV`           | Set environment variables            | Use for config                    |
| `EXPOSE`        | Document port                        | Not a firewall rule               |
| `CMD` / `ENTRYPOINT` | Default command               | Use `CMD` for overrides           |
| `USER`          | Run as non-root                      | Mandatory for security            |
| `HEALTHCHECK`   | Health probe                         | Use in production                 |

---

### 6. Containers (The Running Instance)

A **container** is a running (or stopped) instance of an image.

**Lifecycle Commands** (2026):
```bash
docker run -d --name web -p 8080:80 nginx:alpine     # start detached
docker ps                                            # running containers
docker ps -a                                         # all (including stopped)
docker stop web                                      # graceful stop
docker start web
docker restart web
docker rm -f web                                     # force remove
docker exec -it web sh                               # shell inside
docker logs web -f                                   # follow logs
docker inspect web                                   # full JSON config
```

**Resource limits**:
```bash
docker run -d --memory=512m --cpus=1.5 --name limited nginx
```

---

### 7. Volumes – Persistent Data (Solve "Data disappears on container delete")

**Types**:
- **Bind mount**: Mount host folder (`-v /host/path:/container/path`)
- **Named volume**: Docker-managed (`-v mydata:/container/path`)

**Example** (PostgreSQL):
```bash
docker volume create pgdata
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=secret \
  -v pgdata:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:17-alpine
```

Data survives even if container is deleted.

**Inspect**: `docker volume ls` / `docker volume inspect pgdata`

---

### 8. Docker Networking

Docker creates networks so containers can talk to each other.

**Default networks**:
- `bridge` (default) → containers on same host can talk via container name
- `host` → uses host network stack (no isolation)
- `none` → no networking
- `overlay` → for Swarm (multi-host, used in advanced K8s)

**Commands**:
```bash
docker network ls
docker network create mynet --driver bridge
docker run --network mynet --name db postgres
docker run --network mynet --name app -e DB_HOST=db myapp
```

Inside containers: use service name as hostname (DNS magic by Docker).

**Port mapping**: `-p host_port:container_port`

---

### 9. Docker Compose – Multi-Container Apps (The Real Power)

`docker compose` lets you define entire stacks in one `compose.yaml` file.

**Example: Full-Stack App (2026 style)**

`compose.yaml`:
```yaml
services:
  web:
    build: .
    ports:
      - "3000:3000"
    depends_on:
      db:
        condition: service_healthy
    environment:
      - DB_HOST=db

  db:
    image: postgres:17-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=secret
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s

volumes:
  pgdata:
```

**Commands**:
```bash
docker compose up -d          # start everything
docker compose logs -f web    # follow logs
docker compose ps
docker compose down --volumes # destroy everything
docker compose build --no-cache
```

**Advanced features** (2026):
- `profiles` for dev/prod
- `secrets` & `configs`
- Healthchecks, restart policies
- Multiple compose files (`-f compose.prod.yaml`)

---

### 10. Hands-On Labs (Do These in Order)

**Lab 1**: Build & run a simple NGINX static site.  
**Lab 2**: Create a Node.js/Express app with Dockerfile (multi-stage).  
**Lab 3**: PostgreSQL + volume + environment variables.  
**Lab 4**: Full-stack with Docker Compose (React + Node + Postgres).  
**Lab 5**: Add networking, healthchecks, and non-root user.

GitHub repo for practice: Search “docker-compose-examples” or use the official samples.

---

### 11. Security & 2026 Best Practices

- Never run as root (`USER 1001`)
- Scan images: `docker scout quickview`
- Use `.dockerignore`
- Pin versions (`postgres:17.2-alpine`)
- Enable Docker Content Trust
- Use secrets instead of env vars for passwords

---

### 12. Best Resources (2026)

- **Official Docs**: docs.docker.com (best in class)
- **Free Course**: Docker Docs “Get Started” + “Docker for Developers”
- **YouTube**: TechWorld with Nana – “Docker in 2026” playlist
- **Practice**: Play with Docker (labs.play-with-docker.com) or Killercoda
- **Book**: “Docker Deep Dive” by Nigel Poulton (latest edition)

**Milestone**: You must be able to build a multi-container app with Docker Compose, persistent volumes, custom networking, and a proper multi-stage Dockerfile **without looking at notes**.

Once you finish this, you are 100% ready for **Phase 1: Kubernetes Fundamentals** (Minikube + first cluster).

Tell me when you complete the labs or if you want a **specific project** (e.g., full MERN stack with Docker Compose) to practice before moving to Kubernetes.

You’ve got this, Dhanush!  
Start right now with `docker run hello-world`. 🚀
