### 4. Networking Basics

Networking tools help you diagnose connectivity, transfer files, and interact with remote systems.

#### `ping`
- **Purpose**: Tests connectivity to a host.
- **Example**:
  ```bash
  ping google.com
  # Output: Round-trip time for packets
  ```
- **Options**:
  - `-c 4`: Send 4 pings.

#### `netstat` (Legacy)
- **Purpose**: Displays network connections, routing tables, etc.
- **Example**:
  ```bash
  netstat -tulnp  # List listening ports
  ```
- **Note**: Replaced by `ss` in modern systems.

#### `ss`
- **Purpose**: Modern replacement for `netstat`, showing socket statistics.
- **Example**:
  ```bash
  ss -tuln  # List TCP/UDP listening ports
  ```

#### `curl`
- **Purpose**: Transfers data from/to a server (supports HTTP, FTP, etc.).
- **Examples**:
  ```bash
  curl https://api.example.com  # Fetch data
  curl -o file.html https://example.com  # Save to file
  ```
- **Options**:
  - `-o`: Save output to a file.
  - `-I`: Fetch headers only.

#### `wget`
- **Purpose**: Downloads files from the web.
- **Example**:
  ```bash
  wget https://example.com/file.zip
  ```
- **Options**:
  - `-c`: Resume partial downloads.
  - `-r`: Recursive download (e.g., entire website).

#### `scp` (Secure Copy)
- **Purpose**: Copies files securely over SSH.
- **Example**:
  ```bash
  scp file.txt user@remote:/path  # Copy to remote
  scp user@remote:/path/file.txt .  # Copy from remote
  ```

#### `rsync`
- **Purpose**: Synchronizes files/directories locally or remotely with efficient delta transfers.
- **Example**:
  ```bash
  rsync -avz source/ user@remote:/dest  # Sync with compression
  ```
- **Options**:
  - `-a`: Archive mode (preserves permissions, etc.).
  - `-v`: Verbose.
  - `-z`: Compress data during transfer.

**Workflow**:
1. Test connectivity: `ping 8.8.8.8`.
2. Check open ports: `ss -tuln`.
3. Download a file: `wget https://example.com/file`.
4. Copy to a server: `scp file.txt user@server:/home/user`.

---
