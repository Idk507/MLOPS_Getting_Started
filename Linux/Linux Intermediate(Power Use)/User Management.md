### 2. User Management

Linux is a multi-user system, and managing users is critical for security and access control.

#### `adduser`
- **Purpose**: Adds a new user interactively, setting up home directory, password, etc.
- **Example**:
  ```bash
  sudo adduser john
  # Prompts for password, full name, etc.
  ```
- **Note**: More user-friendly than `useradd` (which requires manual setup).

#### `usermod`
- **Purpose**: Modifies user account settings.
- **Examples**:
  ```bash
  # Change user’s home directory
  sudo usermod -d /new/home/john john
  ```
  ```bash
  # Add user to a group
  sudo usermod -aG sudo john  # Add john to sudo group
  ```
- **Options**:
  - `-aG`: Append to groups (use with `-G`).
  - `-d`: Change home directory.
  - `-s`: Change default shell (e.g., `usermod -s /bin/zsh john`).

#### `groups`
- **Purpose**: Displays groups a user belongs to.
- **Example**:
  ```bash
  groups john
  # Output: john : john sudo users
  ```

#### `/etc/passwd`
- **Purpose**: Stores user account information.
- **Format**: Each line represents a user with fields (separated by `:`):
  - Username, UID, GID, comment, home directory, default shell.
  - Example: `john:x:1000:1000:John Doe:/home/john:/bin/bash`
- **How to View**:
  ```bash
  cat /etc/passwd
  ```
- **Note**: Passwords are not stored here (see `/etc/shadow`).

#### `/etc/shadow`
- **Purpose**: Stores encrypted user passwords and related info (e.g., password expiration).
- **Format**: Fields include username, hashed password, last change, etc.
- **How to View** (requires root):
  ```bash
  sudo cat /etc/shadow
  ```
- **Security**: Only root can read this file.

**Workflow**:
1. Create user: `sudo adduser john`.
2. Add to group: `sudo usermod -aG sudo john`.
3. Verify: `groups john`.
4. Check `/etc/passwd` and `/etc/shadow` for details.

---
