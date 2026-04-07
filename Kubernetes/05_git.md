**Complete End-to-End Git Basics Guide (2026 Edition) – From Zero to Kubernetes-Ready**

This is the **final prerequisite** before diving into **Phase 1: Kubernetes Fundamentals**.  
Git is essential because in real-world Kubernetes work (and DevOps), **everything is declarative and stored in Git**:
- Kubernetes YAML manifests
- Helm charts
- Dockerfiles and Docker Compose files
- GitOps tools like ArgoCD or Flux (they watch Git repos for changes)

**Current Git version (April 2026)**: Git 2.52.x (released early 2026). Git 3.0 is expected late 2026 with SHA-256 as default hash (longer commit hashes).

**Time commitment**: 4–7 days (2–4 hours/day + daily practice).  
**Goal**: By the end, you can create repos, commit Kubernetes YAMLs, work with branches, push to GitHub, and handle basic collaboration.

---

### 1. What is Git? Why Do You Need It?

**Git** is a **distributed version control system** (VCS) created by Linus Torvalds in 2005.  
It tracks changes to files over time, allows you to go back to any previous version, and enables safe collaboration.

**Key Benefits**:
- Full history of every change (who, what, when, why).
- Work offline (local commits).
- Branching is cheap and fast → experiment without breaking main code.
- Perfect for Infrastructure as Code (IaC) like Kubernetes YAML.

**Git vs GitHub**:
- **Git** = the tool (runs locally).
- **GitHub** = a hosting platform for remote repositories (plus collaboration features like Pull Requests, Issues).

Other hosts: GitLab, Bitbucket, Gitea, etc.

---

### 2. Installation & Initial Setup (2026)

**On Ubuntu/Debian (your Linux setup)**:
```bash
sudo apt update
sudo apt install git -y

git --version   # Should show git version 2.52.x or newer
```

**Global Configuration** (do this once):
```bash
git config --global user.name "Dhanush"
git config --global user.email "your.email@example.com"

# Recommended: Use main as default branch (modern standard)
git config --global init.defaultBranch main

# Editor for commit messages (VS Code)
git config --global core.editor "code --wait"

# Nice aliases (optional but very useful)
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
```

Check config:
```bash
git config --global --list
```

---

### 3. Git Core Concepts

- **Repository (Repo)**: A folder tracked by Git (contains `.git` hidden folder).
- **Working Directory**: Where you edit files.
- **Staging Area (Index)**: Files prepared for commit (`git add`).
- **Commit**: A snapshot of changes with a message and unique SHA hash.
- **Branch**: Independent line of development (default: `main`).
- **Remote**: Another copy of the repo (usually on GitHub).

**The Basic Workflow** (remember this forever):
1. `git status` → check state
2. `git add` → stage changes
3. `git commit` → save snapshot
4. `git push` → send to remote (if needed)

---

### 4. Essential Git Commands (Beginner Level)

**Initialize a Repository**:
```bash
mkdir my-k8s-project
cd my-k8s-project
git init
ls -la          # You will see .git folder
```

**Create your first file and commit**:
```bash
echo "# My Kubernetes Project" > README.md
git status                     # Shows untracked files
git add README.md              # Stage the file
git commit -m "Initial commit: Add README"   # Commit with message

git log --oneline              # View history
```

**Clone an existing repo** (most common way to start):
```bash
git clone https://github.com/username/repo-name.git
cd repo-name
```

**Daily Commands**:
```bash
git status                     # Always run first
git add file.yaml              # Stage one file
git add .                      # Stage all changes
git commit -m "Add nginx deployment yaml"
git commit -am "Update service"   # Add + commit tracked files in one go (careful)

git log                        # Full history
git log --oneline --graph      # Nice view
git diff                       # See unstaged changes
git diff --staged              # See staged changes
```

**Undo Mistakes (Very Important)**:
```bash
git checkout -- file.yaml      # Discard changes to a file
git restore file.yaml          # Modern way (Git 2.23+)
git reset --soft HEAD~1        # Undo last commit but keep changes staged
git reset --hard HEAD~1        # Dangerous: undo commit + discard changes
```

---

### 5. Branching & Merging (The Real Power of Git)

Branching lets you work on features safely without touching `main`.

**Commands**:
```bash
git branch                     # List branches
git branch feature/nginx       # Create branch
git switch feature/nginx       # Switch (modern, preferred over checkout)
# or: git checkout -b feature/nginx   # Create + switch

# Work on your feature...
git add .
git commit -m "Add nginx deployment with resources"

git switch main                # Go back to main
git merge feature/nginx        # Merge changes into main

git branch -d feature/nginx    # Delete branch after merge
```

**Best Practice in 2026**:
- Never commit directly to `main` in team projects.
- Use **feature branches** (e.g., `feature/add-deployment`, `bugfix/fix-service`).
- Keep commits small and focused ("one logical change per commit").
- Write good commit messages: "Add" / "Update" / "Fix" / "Refactor" + description.

---

### 6. Working with Remote Repositories (GitHub)

1. Create a repo on GitHub (do **not** initialize with README if you already have local).
2. Link your local repo:
```bash
git remote add origin https://github.com/yourusername/my-k8s-project.git
git push -u origin main        # Push and set upstream
```

**Common Remote Commands**:
```bash
git remote -v                  # Show remotes
git fetch                      # Download remote changes (without merging)
git pull                       # Fetch + merge (most common)
git push                       # Upload your commits
```

**Pull Request (PR) Workflow** (Standard in 2026):
- Create a feature branch locally.
- Push it: `git push -u origin feature/nginx`
- Go to GitHub → Open Pull Request.
- Review, discuss, then merge.

---

### 7. .gitignore – Protect Sensitive Files

Create a `.gitignore` file in the root:
```gitignore
# Ignore common Kubernetes/dev files
*.log
.env
kubeconfig
*.pem
.DS_Store
__pycache__/
node_modules/

# Ignore large files or temp
*.tfstate
*.backup
```

Good `.gitignore` templates: github.com/github/gitignore

---

### 8. Hands-On Labs (Do These in Order)

**Lab 1: Local Repo**
- Create a folder `k8s-learning`.
- Add a `README.md` and a simple `nginx-pod.yaml` (use your YAML skills).
- Make 3–4 commits with meaningful messages.

**Lab 2: Branching**
- Create a branch `feature/deployment`.
- Convert the Pod to a Deployment YAML.
- Merge back to main.

**Lab 3: GitHub**
- Create a public repo on GitHub.
- Push your project.
- Make a small change via GitHub web editor → `git pull` locally.

**Lab 4: Collaboration Simulation**
- Clone your own repo in another folder (or ask a friend).
- Make changes in both places → practice `git pull` and resolve a simple conflict.

**Lab 5: Kubernetes-Specific**
- Add multiple YAML files (Deployment + Service + ConfigMap).
- Commit them separately.
- Create a branch for "add-monitoring" and add Prometheus-related YAML.

---

### 9. Best Practices for Kubernetes/DevOps (2026)

- **Commit Early, Commit Often** — small, atomic commits.
- Use **Conventional Commits** (optional but popular): `feat:`, `fix:`, `docs:`, `chore:`.
- Always `git pull` before starting work.
- Use feature branches + Pull Requests.
- Store **all** Kubernetes manifests, Helm values, ArgoCD apps in Git.
- Enable branch protection rules on GitHub (require PRs for main).
- Learn GitOps mindset: Git = single source of truth.

**Common Pitfalls to Avoid**:
- Committing secrets (use `.gitignore` + tools like git-secrets or Trivy).
- Huge commits with unrelated changes.
- Force pushing (`git push --force`) on shared branches (very dangerous).

---

### 10. Next Level (After Mastering Basics)

- **Rebase** vs Merge (clean history).
- **Stash** (`git stash`).
- **Cherry-pick**.
- **Tags** for releases.
- GitHub Actions (CI/CD for building Docker images and deploying to K8s).
- Tools: GitHub Desktop (optional), VS Code Git integration, `lazygit` (terminal UI).

---

### 11. Best Resources (2026)

- **Free Official**: Pro Git book (progit.org) – still the best free resource.
- **YouTube Crash Courses (2026)**: “Git & GitHub Crash Course for Beginners [2026]”, “Git Tutorial for Beginners: Learn Git in 1 Hour (2026)”.
- **Interactive**: Learn Git Branching (learngitbranching.js.org).
- **Cheat Sheet**: Search “Git cheat sheet 2026”.
- **Practice**: Create repos for your Docker Compose and future Kubernetes YAMLs.


You're making fantastic progress, Dhanush! Start practicing Git commands today on a small project. Every Kubernetes engineer lives in Git. 🚀

Let me know when you're ready for the cluster setup.
