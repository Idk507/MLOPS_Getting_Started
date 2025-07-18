### 3. Scheduling

#### `cron` and `crontab`
- **What is it?**: `cron` schedules recurring tasks; `crontab` manages cron jobs.
- **Syntax**: `min hour day month weekday command`
  - Example: `0 2 * * * /script.sh` (runs at 2 AM daily).
- **Example**:
  ```bash
  # Edit crontab
  crontab -e
  # Add job
  0 0 * * 0 /backup.sh  # Run weekly at midnight
  ```
- **View Jobs**: `crontab -l`.
- **Use Case**: Automate backups, cleanups, or reports.

#### `at`
- **What is it?**: Schedules a one-time task.
- **Example**:
  ```bash
  echo "backup.sh" | at 10pm tomorrow
  ```
- **View Queue**: `atq`.
- **Use Case**: Run a task once at a specific time (e.g., a reminder).

#### `sleep`
- **What is it?**: Pauses script execution for a specified time.
- **Example**:
  ```bash
  #!/bin/bash
  echo "Start"
  sleep 5  # Wait 5 seconds
  echo "End"
  ```
- **Use Case**: Add delays in scripts (e.g., retry loops).

---
