

### 3. Process Management

Linux runs multiple processes (programs) simultaneously. Managing them is key to system performance.

#### `ps`
- **Purpose**: Lists running processes.
- **Examples**:
  ```bash
  # List processes for current user
  ps
  ```
  ```bash
  # List all processes with details
  ps aux
  # Output: USER, PID, %CPU, %MEM, COMMAND
  ```
- **Options**:
  - `aux`: Show all processes (BSD style).
  - `-ef`: Show all processes (System V style).

#### `top`
- **Purpose**: Displays real-time system processes with CPU/memory usage.
- **Usage**: Run `top` and press `q` to quit.
- **Features**:
  - Sort by CPU (`P`), memory (`M`), or time (`T`).
  - Kill process: Press `k` and enter PID.
- **Example**:
  ```bash
  top
  ```

#### `htop`
- **Purpose**: A more user-friendly version of `top` with a colorful interface.
- **Features**:
  - Scrollable process list.
  - Kill processes with `F9`.
  - Filter with `F4`.
- **Install** (e.g., `sudo apt install htop`).
- **Example**:
  ```bash
  htop
  ```

#### `nice`
- **Purpose**: Sets priority for a process (lower priority = less CPU time).
- **Range**: -20 (highest) to 19 (lowest).
- **Example**:
  ```bash
  # Run a command with low priority
  nice -n 10 ./script.sh
  ```
  ```bash
  # Adjust running process priority
  renice 10 -p 1234  # PID 1234
  ```

#### `kill`
- **Purpose**: Sends signals to terminate processes.
- **Common Signals**:
  - `SIGTERM` (15): Graceful termination (default).
  - `SIGKILL` (9): Force kill.
- **Example**:
  ```bash
  kill 1234          # Terminate PID 1234
  kill -9 1234       # Force kill
  ```

#### `killall`
- **Purpose**: Kills processes by name.
- **Example**:
  ```bash
  killall firefox    # Terminate all firefox processes
  ```

#### `jobs`
- **Purpose**: Lists background jobs in the current shell.
- **Example**:
  ```bash
  jobs
  # Output: [1] Running sleep 100 &
  ```

#### `fg` and `bg`
- **Purpose**: Bring background jobs to foreground (`fg`) or send to background (`bg`).
- **Examples**:
  ```bash
  sleep 100 &        # Run in background
  jobs               # List jobs
  fg %1              # Bring job 1 to foreground
  bg %1              # Resume job 1 in background
  ```

**Workflow**:
1. Check processes: `ps aux` or `htop`.
2. Identify high-CPU process: Use `top` or `htop`.
3. Adjust priority: `renice 10 -p 1234`.
4. Terminate: `kill -9 1234`.

---
