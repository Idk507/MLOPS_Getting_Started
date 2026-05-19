**Complete End-to-End Guide to Kubernetes Jobs & CronJobs**  
**(Kubernetes v1.35.x – April 2026)**

### 1. Introduction to Jobs & CronJobs

- **Job**: A Kubernetes workload that runs a **finite task** to completion. Once the task finishes successfully, the Job stops.
- **CronJob**: A scheduled Job that runs automatically based on a cron schedule (like Linux cron).

These are **batch workloads** — different from Deployments (long-running) or StatefulSets (stateful long-running).

---

### 2. Kubernetes Workload Types Comparison

| Workload       | Purpose                        | Runs Until          | Use Case Examples                     |
|----------------|--------------------------------|---------------------|---------------------------------------|
| Deployment     | Long-running stateless         | Forever             | Web apps, APIs                        |
| StatefulSet    | Long-running stateful          | Forever             | Databases                             |
| DaemonSet      | One per node                   | Forever             | Logging, monitoring agents            |
| **Job**        | Run to completion              | Task finishes       | Data processing, backups, ML training |
| **CronJob**    | Scheduled Job                  | Task finishes       | Nightly backups, reports, ETL jobs    |

---

### 2.1. When to Use Jobs & CronJobs

**Jobs**:
- Data processing / ETL pipelines
- Machine Learning model training
- Batch backups and database dumps
- Report generation
- File processing / conversion
- One-time migration or seeding scripts

**CronJobs**:
- Nightly backups
- Daily report generation
- Periodic cleanup jobs
- Scheduled cache refresh
- Compliance / audit jobs
- Log rotation

---


### 3. Kubernetes Jobs – Deep Dive

A **Job** creates one or more Pods and ensures they run successfully to completion.

#### Key Features of Jobs

- Runs Pods until they complete successfully (`restartPolicy: Never` or `OnFailure`).
- Supports parallelism and completions.
- Automatic retries on failure (`backoffLimit`).
- Can be deleted after completion (`ttlSecondsAfterFinished`).

#### Job Types

| Job Type                  | Behavior                                      | `completions` | `parallelism` |
|---------------------------|-----------------------------------------------|---------------|---------------|
| Single Completion         | 1 Pod runs once                               | 1             | 1             |
| Parallel Jobs with Fixed Completions | Multiple Pods run until N succeed       | >1            | Any           |
| Parallel Jobs with Work Queue | Pods run in parallel until all work done | -             | High          |

---

#### Complete Job YAML Examples

**Example 1: Simple One-Time Job**

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: backup-job
spec:
  template:
    spec:
      containers:
      - name: backup
        image: busybox:1.36
        command: ["sh", "-c", "echo 'Backup started...' && sleep 10 && echo 'Backup completed successfully!'"]
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
      restartPolicy: Never          # Very Important for Jobs
  backoffLimit: 4                   # Retry 4 times on failure
  ttlSecondsAfterFinished: 3600     # Auto-delete Job after 1 hour
```

**Example 2: Parallel Job (5 completions, max 2 in parallel)**

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: data-processing-job
spec:
  completions: 5                    # Need 5 successful Pods
  parallelism: 2                    # Run 2 at a time
  template:
    spec:
      containers:
      - name: processor
        image: busybox:1.36
        command: ["sh", "-c", "echo 'Processing item' && sleep 15"]
      restartPolicy: Never
  backoffLimit: 3
```

---

### 4. Hands-on with Jobs

```bash
# 1. Create a Job
kubectl apply -f simple-job.yaml

# 2. Monitor Job status
kubectl get jobs
kubectl get pods -l job-name=backup-job

# 3. Watch completion
kubectl get jobs -w

# 4. See detailed info
kubectl describe job backup-job

# 5. View logs
kubectl logs <pod-name>

# 6. Delete Job
kubectl delete job backup-job
```

---


#### Key Fields in Job Spec

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: example-job
spec:
  completions: 1                    # How many successful Pods needed
  parallelism: 1                    # How many Pods can run simultaneously
  backoffLimit: 6                   # Number of retries before marking Job as failed
  activeDeadlineSeconds: 7200       # Max runtime (2 hours) - kills Job if exceeded
  ttlSecondsAfterFinished: 86400    # Auto-delete Job after 24 hours
  suspend: false                    # Pause/resume the Job

  template:
    spec:
      containers:
      - name: task
        image: busybox:1.36
        command: ["sh", "-c", "echo 'Task completed'"]
      restartPolicy: Never            # Almost always "Never" for Jobs
```

#### Job Types (Completion Modes)

| Type                          | completions | parallelism | Behavior |
|-------------------------------|-------------|-------------|----------|
| **Single Pod Job**            | 1           | 1           | One Pod runs once |
| **Parallel Jobs (Fixed Completions)** | 10     | 3           | Runs 3 at a time until 10 succeed |
| **Work Queue / Parallel Jobs** | Not set    | High        | Pods coordinate via external queue |

---

### 4. Complete Practical Job Examples

**Example 1: Simple Backup Job**

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: daily-backup
spec:
  ttlSecondsAfterFinished: 7200     # Delete after 2 hours
  backoffLimit: 3
  template:
    spec:
      containers:
      - name: backup
        image: postgres:17-alpine
        command: ["sh", "-c", "pg_dump -U postgres -h postgres mydb > /backup/backup.sql"]
        volumeMounts:
        - name: backup-volume
          mountPath: /backup
      restartPolicy: Never
      volumes:
      - name: backup-volume
        persistentVolumeClaim:
          claimName: backup-pvc
```

**Example 2: Parallel Processing Job**

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: process-images
spec:
  completions: 20
  parallelism: 5
  template:
    spec:
      containers:
      - name: processor
        image: yourcompany/image-processor:v1
        command: ["python", "process.py"]
      restartPolicy: Never
```

---




### 5. CronJobs – Scheduled Jobs

A **CronJob** creates a new **Job** automatically according to a cron schedule.

#### Cron Schedule Format
`minute hour day-of-month month day-of-week`

**Common Examples**:
- `0 2 * * *` → Every day at 2:00 AM
- `0 */6 * * *` → Every 6 hours
- `30 23 * * 5` → Every Friday at 11:30 PM
- `@daily`, `@hourly`, `@weekly` (convenience syntax)

---

#### Complete CronJob YAML

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: nightly-backup
spec:
  schedule: "0 2 * * *"                    # Daily at 2 AM
  timeZone: "Asia/Kolkata"                 # Important in 2026
  concurrencyPolicy: Forbid                # Options: Allow, Forbid, Replace
  successfulJobsHistoryLimit: 5            # Keep last 5 successful jobs
  failedJobsHistoryLimit: 3                # Keep last 3 failed jobs
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: busybox:1.36
            command: ["sh", "-c", "echo 'Starting backup at $(date)' && sleep 30 && echo 'Backup done'"]
          restartPolicy: Never
      backoffLimit: 3
```

---

### 6. Hands-on with CronJobs

```bash
kubectl apply -f cronjob.yaml

# List CronJobs
kubectl get cronjobs

# See created Jobs
kubectl get jobs

# Manually trigger a CronJob (very useful for testing)
kubectl create job manual-backup --from=cronjob/nightly-backup

# Delete CronJob
kubectl delete cronjob nightly-backup
```

---


#### CronJob Spec Fields

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: nightly-report
spec:
  schedule: "0 2 * * *"                    # Daily at 2:00 AM
  timeZone: "Asia/Kolkata"                 # Critical field
  concurrencyPolicy: Forbid                # Allow | Forbid | Replace
  startingDeadlineSeconds: 300             # If missed, skip if older than 5 mins
  successfulJobsHistoryLimit: 10
  failedJobsHistoryLimit: 5
  suspend: false

  jobTemplate:
    spec:
      ttlSecondsAfterFinished: 86400
      backoffLimit: 4
      template:
        spec:
          containers:
          - name: report
            image: busybox:1.36
            command: ["sh", "-c", "echo 'Report generated at $(date)'"]
          restartPolicy: Never
```

#### Cron Schedule Reference

- `* * * * *` → Every minute
- `0 */6 * * *` → Every 6 hours
- `0 0 * * 0` → Every Sunday at midnight
- `@daily`, `@hourly`, `@weekly`, `@monthly`

---

### 6. All Important Commands (Must Know)

**For Jobs**:
```bash
kubectl get jobs
kubectl get jobs -o wide
kubectl describe job <name>
kubectl logs <pod-name>
kubectl delete job <name>
```

**For CronJobs**:
```bash
kubectl get cronjobs
kubectl describe cronjob <name>
kubectl create job test-run --from=cronjob/<name>   # Manual trigger
kubectl suspend cronjob <name>                     # Pause
```

---





### 7. Best Practices (2026)

**For Jobs**:
- Always set `restartPolicy: Never`
- Use reasonable `backoffLimit`
- Set `ttlSecondsAfterFinished` to avoid clutter
- Use `activeDeadlineSeconds` for time-bound jobs
- Add proper resource requests/limits

**For CronJobs**:
- Use `Forbid` concurrency policy for most cases
- Keep history limits low (5/3 is good)
- Always specify `timeZone`
- Monitor Job failures with alerts
- Use Init Containers if needed for setup

---

### 8. Common Issues & Troubleshooting

| Issue                        | Fix |
|-----------------------------|-----|
| Job stays in `Active` state | Check Pod logs, increase `activeDeadlineSeconds` |
| Too many old Jobs            | Set `ttlSecondsAfterFinished` |
| CronJob not triggering       | Check schedule + timeZone |
| Pods failing repeatedly      | Increase `backoffLimit`, fix command |

**Useful Commands**:
```bash
kubectl get jobs --field-selector status.successful=1
kubectl get cronjobs
kubectl get events --sort-by=.metadata.creationTimestamp
```

---

**Practice Exercise**

1. Create a simple Job that prints "Hello Kubernetes" and sleeps 20 seconds.
2. Create a CronJob that runs every minute (for testing: `* * * * *`).
3. Manually trigger the CronJob.
4. Observe Job history.

