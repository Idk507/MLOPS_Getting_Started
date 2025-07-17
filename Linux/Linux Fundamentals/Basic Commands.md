

###  Basic Commands

Let’s explore the basic terminal commands grouped by category. I’ll explain each command, its purpose, and provide examples. The **terminal** is where you type these commands to interact with Linux.

#### Navigation Commands

- **`pwd` (Print Working Directory)**:
  - Shows the current directory you’re in.
  - Example:
    ```bash
    pwd
    # Output: /home/user
    ```
  - Use it to confirm your location in the file system.

- **`cd` (Change Directory)**:
  - Moves you to another directory.
  - Examples:
    ```bash
    cd /home/user/documents  # Go to documents directory
    cd ..                    # Move up one directory
    cd ~                     # Go to your home directory
    cd /                     # Go to root directory
    ```
  - Tip: Use `cd` without arguments to return to your home directory.

- **`ls` (List)**:
  - Lists files and directories in the current directory.
  - Examples:
    ```bash
    ls               # Basic list
    ls -l            # Detailed list (permissions, size, etc.)
    ls -a            # Show hidden files (starting with .)
    ls -lh           # Human-readable file sizes (e.g., KB, MB)
    ```
  - Output might look like: `file1.txt  folder1  image.jpg`.

- **`tree`**:
  - Displays directory contents in a tree-like format.
  - Example:
    ```bash
    tree
    # Output:
    # .
    # ├── file1.txt
    # └── folder1
    #     └── file2.txt
    ```
  - Install if needed (e.g., `sudo apt install tree` on Ubuntu).

#### File Operations

- **`cp` (Copy)**:
  - Copies files or directories.
  - Syntax: `cp source destination`
  - Examples:
    ```bash
    cp file1.txt file2.txt           # Copy file1.txt to file2.txt
    cp -r folder1 folder2            # Copy folder1 and its contents
    ```
  - Use `-r` (recursive) for directories.

- **`mv` (Move)**:
  - Moves or renames files/directories.
  - Syntax: `mv source destination`
  - Examples:
    ```bash
    mv file1.txt documents/          # Move file to documents folder
    mv file1.txt file2.txt           # Rename file1.txt to file2.txt
    ```
  - Unlike `cp`, `mv` doesn’t leave the original file.

- **`rm` (Remove)**:
  - Deletes files or directories.
  - Examples:
    ```bash
    rm file1.txt                     # Delete a file
    rm -r folder1                    # Delete a folder and its contents
    rm -f file1.txt                  # Force delete without prompt
    ```
  - **Warning**: `rm` is permanent; there’s no recycle bin. Use with caution.

- **`touch`**:
  - Creates an empty file or updates the timestamp of an existing file.
  - Example:
    ```bash
    touch newfile.txt                # Create newfile.txt
    touch existingfile.txt           # Update timestamp
    ```

- **`mkdir` (Make Directory)**:
  - Creates a new directory.
  - Examples:
    ```bash
    mkdir newfolder                  # Create a folder named newfolder
    mkdir -p parent/child            # Create nested directories
    ```

#### Viewing Files

- **`cat` (Concatenate)**:
  - Displays the entire content of a file.
  - Example:
    ```bash
    cat file1.txt
    # Output: (contents of file1.txt)
    ```
  - Can also combine files: `cat file1.txt file2.txt > combined.txt`.

- **`less`**:
  - Views file contents one page at a time (useful for large files).
  - Example:
    ```bash
    less file1.txt
    ```
  - Navigation: Use arrow keys, `q` to quit.

- **`more`**:
  - Similar to `less`, but only scrolls down.
  - Example:
    ```bash
    more file1.txt
    ```
  - Press `Enter` to scroll, `q` to quit.

- **`head`**:
  - Shows the first 10 lines of a file (or specify with `-n`).
  - Example:
    ```bash
    head file1.txt                   # First 10 lines
    head -n 5 file1.txt              # First 5 lines
    ```

- **`tail`**:
  - Shows the last 10 lines of a file (or specify with `-n`).
  - Example:
    ```bash
    tail file1.txt                   # Last 10 lines
    tail -n 5 file1.txt              # Last 5 lines
    tail -f file1.txt                # Follow file for real-time updates (e.g., logs)
    ```

#### Permissions

Linux uses a permission system to control access to files and directories. Each file has permissions for three groups: **owner**, **group**, and **others**.

- **Permission Types**:
  - `r` (read): View file contents or list directory.
  - `w` (write): Modify or delete file/directory.
  - `x` (execute): Run a file as a program or enter a directory.
  - Example (from `ls -l`): `-rwxr-xr-x`
    - First character: `-` (file) or `d` (directory).
    - Next three: Owner permissions (`rwx`).
    - Next three: Group permissions (`r-x`).
    - Last three: Others permissions (`r-x`).

- **`chmod` (Change Mode)**:
  - Changes file permissions.
  - Two methods:
    - **Symbolic**: `chmod u+x file1.txt` (add execute for user).
    - **Numeric**: Uses numbers (e.g., `755` = `rwxr-xr-x`).
      - `r = 4`, `w = 2`, `x = 1`.
      - Example: `chmod 755 script.sh` (owner: rwx, group/others: r-x).
  - Example:
    ```bash
    chmod u+w file1.txt              # Add write permission for owner
    chmod 644 file1.txt              # Set rw-r--r--
    ```

- **`chown` (Change Owner)**:
  - Changes the owner or group of a file.
  - Example:
    ```bash
    sudo chown john file1.txt         # Change owner to john
    sudo chown john:users file1.txt  # Change owner to john, group to users
    ```

- **`umask`**:
  - Sets default permissions for new files/directories.
  - Example: Default `umask` is often `022`, meaning new files get `644` (rw-r--r--) and directories get `755` (rwxr-xr-x).
  - Check: `umask`.
  - Set: `umask 002` (for more permissive defaults).

#### Searching

- **`find`**:
  - Searches for files/directories based on criteria (name, size, type).
  - Examples:
    ```bash
    find /home -name "file1.txt"     # Find file1.txt in /home
    find . -type d                   # Find directories in current folder
    find . -size +10M                # Find files larger than 10MB
    ```

- **`locate`**:
  - Faster search using a database (updated with `sudo updatedb`).
  - Example:
    ```bash
    locate file1.txt                 # Find file1.txt system-wide
    ```
  - Note: Less accurate if database is outdated.

- **`grep` (Global Regular Expression Print)**:
  - Searches for text patterns within files.
  - Examples:
    ```bash
    grep "error" file1.txt           # Find "error" in file1.txt
    grep -r "error" /home            # Search recursively in /home
    grep -i "error" file1.txt        # Case-insensitive search
    ```

---

### Putting It All Together

Here’s a quick workflow to practice these concepts:
1. Open a terminal (e.g., on Ubuntu, press `Ctrl + Alt + T`).
2. Check your current directory: `pwd`.
3. List files: `ls -l`.
4. Create a folder: `mkdir test`.
5. Navigate to it: `cd test`.
6. Create a file: `touch example.txt`.
7. Add text: `echo "Hello, Linux!" > example.txt`.
8. View it: `cat example.txt`.
9. Copy it: `cp example.txt example2.txt`.
10. Change permissions: `chmod 600 example.txt`.
11. Search for text: `grep "Linux" example.txt`.

---

### Additional Tips for Beginners

- **Man Pages**: Use `man <command>` (e.g., `man ls`) to read documentation for any command.
- **Tab Completion**: Press `Tab` to auto-complete commands or file names.
- **Root Privileges**: Use `sudo` before commands requiring admin access (e.g., `sudo apt update`).
- **Practice Environment**: Try a virtual machine (e.g., VirtualBox) with Ubuntu to experiment safely.
- **Online Resources**: Check the Arch Wiki, Ubuntu documentation, or Linux forums for help.

---

