### 4. Trap Signals and Debugging

#### `trap`
- **What is it?**: Captures signals (e.g., Ctrl+C) to run custom commands.
- **Signals**:
  - `SIGINT`: Ctrl+C.
  - `SIGTERM`: Termination request.
  - `EXIT`: Script exits.
- **Example**:
  ```bash
  #!/bin/bash
  trap 'echo "Script interrupted!"; exit 1' SIGINT
  echo "Running..."
  sleep 10
  ```
  **Output**: If you press Ctrl+C, it prints “Script interrupted!” and exits.
- **Use Case**: Clean up temporary files on script interruption.

#### `set -x`
- **What is it?**: Enables debug mode, printing each command before execution.
- **Example**:
  ```bash
  #!/bin/bash
  set -x
  echo "Test"
  ls
  ```
  **Output**: Shows commands (`+ echo Test`, `+ ls`) before results.
- **Use Case**: Debug scripts to find errors.

---
