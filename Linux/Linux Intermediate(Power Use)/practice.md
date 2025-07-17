### 8. Practice Tasks

#### Automate File Cleanup
**Goal**: Write a script to delete files older than 30 days in a specific directory (e.g., `/tmp/logs`).

**Script** (`cleanup.sh`):
```bash
#!/bin/bash
# Delete files older than 30 days in /tmp/logs
find /tmp/logs -type f -mtime +30 -exec rm -v {} \;
# Alternative with xargs
# find /tmp/logs -type f -mtime +30 | xargs rm -v
echo "Cleanup complete: $(date)" >> /tmp/cleanup.log
```

**Explanation**:
- `#!/bin/bash`: Specifies Bash as the interpreter.
- `find /tmp/logs -type f -mtime +30`: Finds files (`-type f`) older than 30 days (`-mtime +30`).
- `-exec rm -v {} \;`: Deletes found files verbosely.
- `tee` or `>>`: Logs completion time.

**Run**:
```bash
chmod +x cleanup.sh
./cleanup.sh
```

**Automate with Cron**:
1. Edit crontab: `crontab -e`.
2. Add: `0 2 * * * /path/to/cleanup.sh` (runs daily at 2 AM).

#### Set Up Aliases and Functions in `.bashrc`
**Goal**: Add shortcuts and custom functions to streamline tasks.

**Edit `~/.bashrc`**:
```bash
nano ~/.bashrc
```

**Add Aliases**:
```bash
# Shortcuts for common commands
alias ll='ls -lh'
alias update='sudo apt update && sudo apt upgrade -y'
alias cleanup='find /tmp/logs -type f -mtime +30 -delete'
```

**Add Functions**:
```bash
# Function to search and kill a process
killproc() {
  ps aux | grep "$1" | grep -v grep | awk '{print $2}' | xargs kill -9
}

# Function to check disk usage and sort
diskusage() {
  du -h --max-depth=1 "$1" | sort -h
}
```

**Apply Changes**:
```bash
source ~/.bashrc
```

**Usage**:
- `ll`: Lists files with human-readable sizes.
- `update`: Updates packages.
- `killproc firefox`: Kills all Firefox processes.
- `diskusage /home`: Shows sorted disk usage.

---






### 9. Resources

- **Explainshell**:
  - Website: `explainshell.com`
  - Purpose: Breaks down Linux commands and their options.
  - Example: Enter `find . -name "*.txt" | xargs rm` to see each part explained.
  - Use Case: Learn complex commands or debug scripts.

- **Vim Adventures**:
  - Website: `vim-adventures.com`
  - Purpose: Interactive game to learn Vim keybindings.
  - Use Case: Practice `hjkl` navigation, editing commands, and modes in a fun way.

**Additional Resources**:
- **Arch Wiki**: Comprehensive Linux documentation (wiki.archlinux.org).
- **Linux man pages**: `man <command>` (e.g., `man awk`).
- **TLDR Pages**: Simplified command examples (`sudo apt install tldr`, then `tldr ls`).

---

### Full Workflow Example

Let’s combine concepts into a practical scenario:
1. **Check System**: Run `htop` to monitor processes and `df -h` for disk space.
2. **Clean Logs**: Run `find /var/log -type f -name "*.log" -mtime +30 -delete`.
3. **Backup Files**: Use `rsync -avz /home/user/docs user@remote:/backup`.
4. **Analyze Logs**: Use `awk '/ERROR/ {print}' /var/log/syslog | sort | uniq -c`.
5. **Automate**: Add cleanup script to cron and aliases to `.bashrc`.
6. **Edit Config**: Use `vim /etc/ssh/sshd_config` to tweak SSH settings.

---
