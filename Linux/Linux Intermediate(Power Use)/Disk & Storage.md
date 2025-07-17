### 5. Disk & Storage

Managing disk space and storage devices is critical for system administration.

#### `df`
- **Purpose**: Shows disk usage for mounted file systems.
- **Example**:
  ```bash
  df -h  # Human-readable (e.g., GB)
  # Output: Filesystem, Size, Used, Avail, Use%, Mounted on
  ```

#### `du`
- **Purpose**: Estimates disk usage for files/directories.
- **Example**:
  ```bash
  du -sh /home  # Total size of /home
  du -h --max-depth=1 /home  # Size of each subdirectory
  ```

#### `mount`
- **Purpose**: Mounts a file system (e.g., USB drive) to a directory.
- **Example**:
  ```bash
  sudo mount /dev/sdb1 /mnt  # Mount device to /mnt
  ```

#### `umount`
- **Purpose**: Unmounts a file system.
- **Example**:
  ```bash
  sudo umount /mnt
  ```

#### `fdisk`
- **Purpose**: Manages disk partitions (requires root).
- **Example**:
  ```bash
  sudo fdisk /dev/sda  # Interactive partition editor
  ```
- **Warning**: Be cautious; changes can destroy data.

#### `lsblk`
- **Purpose**: Lists block devices and their mount points.
- **Example**:
  ```bash
  lsblk
  # Output: Tree of disks, partitions, and mount points
  ```

#### `blkid`
- **Purpose**: Shows UUIDs and types of block devices.
- **Example**:
  ```bash
  sudo blkid
  # Output: /dev/sda1: UUID="1234-5678" TYPE="ext4"
  ```

**Workflow**:
1. Check disk usage: `df -h`.
2. Find large directories: `du -sh /home/*`.
3. Mount a USB: `sudo mount /dev/sdb1 /mnt`.
4. Verify: `lsblk`.

---
