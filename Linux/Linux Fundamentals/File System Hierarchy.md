###  File System Hierarchy

The **Linux File System Hierarchy** organizes files and directories in a tree-like structure, starting from the root directory (`/`). Unlike Windows (with drives like `C:\`), Linux has a single unified file system. Here’s an overview of key directories:

- **`/` (Root)**:
  - The top-level directory, the starting point of the file system.
  - All other directories and files branch from here.

- **`/home`**:
  - Contains user home directories (e.g., `/home/john` for user "john").
  - Stores personal files, settings, and configurations (like `~/.bashrc`).
  - Each user has their own subdirectory.

- **`/etc`**:
  - Stores system-wide configuration files.
  - Examples:
    - `/etc/passwd`: User account information.
    - `/etc/apt/sources.list`: Software repository settings (Ubuntu).
  - Think of it as the system’s control panel.

- **`/bin`**:
  - Contains essential binary (executable) files for basic commands.
  - Examples: `ls`, `cp`, `mv`, `cat`.
  - These are available to all users.

- **`/var`**:
  - Stores variable data that changes during system operation.
  - Examples:
    - `/var/log`: System logs (e.g., `syslog` for troubleshooting).
    - `/var/www`: Web server files.
    - `/var/tmp`: Temporary files.

- **Other Important Directories**:
  - **`/usr`**: User-installed software and libraries (e.g., `/usr/bin` for additional commands).
  - **`/tmp`**: Temporary files, often cleared on reboot.
  - **`/root`**: Home directory for the root user (admin).
  - **`/dev`**: Device files (e.g., `/dev/sda` for a hard drive).
  - **`/proc`**: Virtual directory with system process and hardware info.

**Key Concept**:
- Everything in Linux is treated as a file, including directories and hardware devices.
- Use `ls /` in a terminal to see the root directory’s contents.

---
