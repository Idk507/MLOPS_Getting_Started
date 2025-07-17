### 6. Package Managers

Package managers install, update, and remove software on Linux.

#### Debian: `apt`
- **Purpose**: Manages Debian/Ubuntu packages.
- **Examples**:
  ```bash
  sudo apt update           # Refresh package lists
  sudo apt upgrade          # Update installed packages
  sudo apt install vim      # Install vim
  sudo apt remove vim       # Remove vim
  ```
- **Files**: `/etc/apt/sources.list` (repositories).

#### RedHat: `yum`/`dnf`
- **Purpose**: Manages packages on Red Hat, CentOS, Fedora (`dnf` is newer).
- **Examples**:
  ```bash
  sudo dnf install vim      # Install vim
  sudo dnf update           # Update all packages
  sudo dnf remove vim       # Remove vim
  ```
- **Note**: `yum` is similar but older; `dnf` is preferred on Fedora.

#### Arch: `pacman`
- **Purpose**: Manages packages on Arch Linux.
- **Examples**:
  ```bash
  sudo pacman -S vim        # Install vim
  sudo pacman -Syu          # Update system
  sudo pacman -R vim        # Remove vim
  ```
- **Files**: `/etc/pacman.conf` (configuration).

**Workflow**:
1. Update package lists: `sudo apt update` (or `dnf`, `pacman`).
2. Install a tool: `sudo apt install htop`.
3. Clean up: `sudo apt autoremove`.

---
