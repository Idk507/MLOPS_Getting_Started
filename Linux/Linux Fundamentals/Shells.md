

### Shells (Bash, Zsh, Fish)

A **shell** is a command-line interface that lets you interact with the Linux system by typing commands. It interprets your input and communicates with the kernel to execute tasks.

- **Bash (Bourne Again Shell)**:
  - The default shell in most Linux distributions.
  - Features:
    - Simple syntax for commands and scripts.
    - Supports scripting (e.g., `.sh` files).
    - Tab completion for commands and files.
  - Example: Type `ls` to list files or `echo $PATH` to see environment variables.
  - File: Configuration is in `~/.bashrc`.

- **Zsh (Z Shell)**:
  - An enhanced version of Bash with more features.
  - Features:
    - Advanced tab completion (e.g., suggests options for commands).
    - Better customization (e.g., themes via **Oh My Zsh**).
    - Improved scripting capabilities.
  - Example: Popular on macOS (default since 2019) and among developers.
  - File: Configuration is in `~/.zshrc`.

- **Fish (Friendly Interactive Shell)**:
  - Designed for user-friendliness, especially for beginners.
  - Features:
    - Autosuggestions as you type.
    - Colorful syntax highlighting.
    - No complex configuration needed out of the box.
  - Example: Type `ls` and Fish suggests commands based on history.
  - File: Configuration is in `~/.config/fish/config.fish`.

**Choosing a Shell**:
- **Bash**: Stick with it as a beginner; it’s universal and widely supported.
- **Zsh**: Try it for advanced features and customization.
- **Fish**: Great for interactive use but less common for scripting.

**How to Check Your Shell**:
- Run `echo $SHELL` in the terminal (e.g., `/bin/bash` means Bash).

---
