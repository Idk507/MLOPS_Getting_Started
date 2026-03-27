**Complete End-to-End Linux Command Line Mastery (Bash, Filesystem, Processes, Networking, Permissions) – 2026 Edition**


**Why this matters for Kubernetes**  
- You’ll edit YAML manifests, manage container images, troubleshoot pods, debug network policies, and run production commands on control-plane nodes.

---

### 1. Getting Started with the Terminal & Bash

**Bash** (Bourne Again SHell) is the default shell on almost all Linux systems.

**Open the terminal**:
- Ubuntu: `Ctrl + Alt + T`
- First commands:
  ```bash
  whoami          # your username
  pwd             # current directory (Print Working Directory)
  echo "Hello Kubernetes!"   # print text
  echo $SHELL     # shows /bin/bash
  ```

**Essential keyboard shortcuts**:
- `Tab` → auto-complete
- `Ctrl + C` → kill running command
- `Ctrl + Z` → suspend (bg/fg later)
- `Ctrl + L` → clear screen
- `↑/↓` → command history
- `Ctrl + R` → reverse search history
- `Ctrl + D` → logout/exit

**Help commands**:
```bash
command --help          # quick help
man ls                  # full manual (q to quit)
whatis ls               # one-line description
```

---

### 2. Linux Filesystem Hierarchy Standard (FHS) – 2026

Linux follows **FHS 3.0** (latest as of 2025 update).

**Key directories you must know**:

| Directory       | Purpose                                      | Kubernetes Relevance                  |
|-----------------|----------------------------------------------|---------------------------------------|
| `/`             | Root of everything                           | Base of the system                    |
| `/bin`          | Essential user binaries (symlink to `/usr/bin`) | Common commands                       |
| `/etc`          | Configuration files (editable by admin)      | kubeadm config, containerd, systemd   |
| `/home`         | User home directories                        | Your working area                     |
| `/root`         | Root user’s home                             | Rare (use `sudo`)                     |
| `/usr`          | User programs & data                         | Most installed software               |
| `/var`          | Variable data (logs, caches)                 | `/var/log/kubernetes`, container logs |
| `/tmp`          | Temporary files (cleared on reboot)          | Scratch space                         |
| `/dev`          | Device files                                 | Special files                         |
| `/proc`         | Virtual filesystem for processes             | Live process info (`cat /proc/cpuinfo`) |
| `/sys`          | Kernel & hardware info                       | Advanced tuning                       |

**Practice**:
```bash
tree / -L 2 | head -20     # install tree first: sudo apt install tree
ls /etc/kubernetes         # (after you install K8s later)
```

---

### 3. Filesystem Navigation & Management

**Navigation commands**:
```bash
pwd                    # where am I?
cd /etc                # absolute path
cd ~                   # go to home (~ = /home/youruser)
cd ..                  # one level up
cd -                   # back to previous directory
ls                     # list
ls -la                 # long + hidden (dot files)
ls -lh                 # human-readable sizes
```

**File & directory operations**:
```bash
touch file.txt                  # create empty file
mkdir -p dir1/dir2/dir3         # create nested
cp file.txt /tmp/               # copy
cp -r dir1 /tmp/                # recursive copy
mv file.txt newname.txt         # rename/move
rm file.txt                     # delete file
rm -rf dir1                     # DANGER: recursive force delete
cat file.txt                    # view content
less file.txt                   # scrollable view
head -n 5 file.txt              # first 5 lines
tail -f /var/log/syslog         # follow live logs (great for K8s)
```

**Wildcards & searching**:
```bash
ls *.yaml                  # all YAML files
find /etc -name "*.conf"   # recursive search
grep "apiVersion" *.yaml   # search inside files
```

---

### 4. Text Processing, Redirection & Piping (The Real Power)

**Redirection**:
```bash
echo "Kubernetes is awesome" > config.txt     # overwrite
echo "version: v1.35" >> config.txt          # append
cat config.txt > /dev/null                    # discard output
command 2> error.log                          # stderr only
command &> all.log                            # both stdout + stderr
```

**Piping (`|`)** – chain commands:
```bash
ls -la | wc -l                    # count lines
cat /etc/passwd | grep bash       # filter
kubectl get pods | grep Running   # (later)
ps aux | grep kubelet | awk '{print $2}' | xargs kill
```

**Advanced text tools**:
```bash
awk '{print $1}' file.txt         # column extraction
sed 's/old/new/g' file.txt        # search-replace
sort | uniq -c                    # unique + count
```

---

### 5. Permissions & Ownership (Critical for Security)

Every file has **owner**, **group**, and **permissions**.

**View permissions**:
```bash
ls -l
# Example output: -rwxr-xr-- 1 dhanush docker  1234 Mar 27 08:00 script.sh
# Breakdown:     type  owner  group  others
```

**Permission bits**:
- `r` = read (4), `w` = write (2), `x` = execute (1)
- Three categories: owner | group | others

**Change permissions** (`chmod`):
```bash
chmod 755 script.sh          # rwxr-xr-x (owner full, others read+exec)
chmod +x script.sh           # add execute
chmod -w file.txt            # remove write
chmod -R 644 dir/            # recursive
```

**Change owner/group** (`chown`):
```bash
sudo chown dhanush:docker file.txt
sudo chown -R root:root /etc/kubernetes
```

**Special bits**:
- `sudo` → run as root (use sparingly)
- `umask` → default permissions for new files (check with `umask`)

**Real-world K8s example**:
```bash
chmod 600 ~/.kube/config     # protect kubeconfig!
```

---

### 6. Processes & Job Control

**View processes**:
```bash
ps aux                      # all processes
ps -ef | grep kube          # filter
top                         # live view (q to quit)
htop                        # better version (install: sudo apt install htop)
```

**Kill & signals**:
```bash
kill PID                    # graceful (SIGTERM)
kill -9 PID                 # force (SIGKILL) – last resort
pkill -f "kubelet"          # kill by name
```

**Job control** (background/foreground):
```bash
sleep 100 &                 # run in background
jobs                        # list jobs
fg %1                       # bring job 1 to foreground
bg %1                       # send to background
Ctrl + Z → bg               # suspend & background
```

**Process priorities**:
```bash
nice -n 10 command          # lower priority
renice -n -5 -p PID         # increase priority
```

**System info**:
```bash
free -h                     # memory
df -h                       # disk
du -sh /var/log             # directory size
uptime
```

---

### 7. Networking Commands (Modern 2026 Way)

**Deprecated**: `ifconfig`, `netstat` → still work but **do not use in production/scripts**.

**Modern replacements**:

| Task                    | Old Command       | Modern Command (2026)                  |
|-------------------------|-------------------|----------------------------------------|
| Show interfaces         | `ifconfig`        | `ip addr` or `ip -brief link`         |
| Add IP / configure      | `ifconfig`        | `ip addr add`                          |
| Routing table           | `route`           | `ip route`                             |
| Listening ports         | `netstat -tuln`   | `ss -tulnp`                            |
| Connections             | `netstat`         | `ss -t`                                |

**Essential networking commands**:
```bash
ip addr show                    # interfaces + IPs
ip route                        # routing
ss -tulnp                       # what is listening? (MUST KNOW for K8s)
ping 8.8.8.8                    # test connectivity
curl -I https://kubernetes.io   # HTTP headers
wget https://example.com/file   # download
ssh user@server                 # remote login
scp file.txt user@server:/tmp/  # secure copy
traceroute 8.8.8.8              # path to destination
dig kubernetes.io               # DNS lookup (or `nslookup`)
```

**Kubernetes-relevant**:
```bash
ss -tulnp | grep 6443          # kube-apiserver port
curl -k https://localhost:6443 # test API server
```

---

### 8. Bash Scripting Basics (The Next Level)

Create your first script:
```bash
cat > hello-k8s.sh << EOF
#!/bin/bash
echo "Hello from Kubernetes prep!"
echo "Current date: $(date)"
echo "Free memory: $(free -h | grep Mem | awk '{print $4}')"
EOF

chmod +x hello-k8s.sh
./hello-k8s.sh
```

**Scripting fundamentals**:
- Shebang: `#!/bin/bash`
- Variables: `NAME="Dhanush"; echo $NAME`
- Conditionals:
  ```bash
  if [ -f /etc/kubernetes/admin.conf ]; then
    echo "K8s is installed"
  fi
  ```
- Loops:
  ```bash
  for pod in $(kubectl get pods -o name); do
    echo "Checking $pod"
  done
  ```

**Best practice**: Always add `set -euo pipefail` at top of scripts.

---

### 9. Best Practices & Troubleshooting (Production Mindset)

1. **Never `rm -rf /`** (obviously).
2. Use `sudo` only when needed.
3. Always check exit codes: `echo $?` (0 = success).
4. Log everything: redirect to files.
5. Use aliases: `alias k='kubectl'`, `alias ll='ls -lh'`.
6. Keep history clean: `history | tail`.
7. For Kubernetes nodes: always work as non-root when possible.

**Common troubleshooting commands**:
```bash
journalctl -u kubelet -f     # systemd logs
dmesg | tail                 # kernel messages
strace command               # trace system calls (advanced)
```

---

### 10. Hands-On Labs (Do These Today)

**Lab 1**: Filesystem & Permissions
- Create `/tmp/k8s-lab/`, add files with different permissions, change owner.

**Lab 2**: Processes & Monitoring
- Run a long sleep in background, monitor with `htop`, kill it gracefully.

**Lab 3**: Networking
- Use `ss -tulnp` to find ports used by any service.
- Download a Kubernetes manifest with `curl`.

**Lab 4**: Mini Script
- Write a script that checks free disk space and emails you if < 20% (use `mail` or just echo).

**Lab 5** (Advanced): Combine everything
- Script that finds all `.yaml` files in a dir, checks permissions, and lists processes listening on port 6443.

---

### 11. Best Resources (Updated for 2026)

- **Free Book** (still the gold standard): *The Linux Command Line* by William Shotts (free PDF).
- **Interactive**: Ryan’s Tutorials (ryanstutorials.net/linuxtutorial) – 13-part beginner course.
- **YouTube Full Courses (2026)**:
  - “Linux Command Line & Bash Scripting Full Course 2026” (YouTube).
  - “Linux Mastery 2026: Master the Command Line in 11 Hours”.
- **Official**: GNU Bash Manual + `man bash`.
- **Cheat Sheets**: linuxteck.com (shell scripting cheat sheet).
- **Practice Platforms**: OverTheWire Bandit, Linux Journey, Killercoda (free Linux terminals).

Master this guide **before** touching Minikube or Docker. Once finished, you’ll be able to:
- Navigate any Linux server blindfolded
- Debug Kubernetes node issues
- Write automation scripts
- Secure files and processes

