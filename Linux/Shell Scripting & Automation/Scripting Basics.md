### 1. Scripting Basics

Bash (Bourne Again Shell) scripting lets you automate tasks by writing programs that run Linux commands. Let’s break down the core components.

#### `#!/bin/bash`
- **What is it?**: The shebang line at the start of a script tells the system to use the Bash interpreter (`/bin/bash`) to run the script.
- **Why use it?**: Ensures the script runs with Bash, regardless of the user’s default shell.
- **Example**:
  ```bash
  #!/bin/bash
  echo "Hello, World!"
  ```
- **Use Case**: Start every Bash script with this line to guarantee compatibility.
- **How to Run**:
  - Save as `hello.sh`, make executable: `chmod +x hello.sh`.
  - Run: `./hello.sh`.

#### Variables
- **What are they?**: Variables store data (e.g., text, numbers) for use in scripts.
- **Syntax**: `name=value` (no spaces). Access with `$name` or `${name}`.
- **Rules**:
  - No spaces around `=`.
  - Use quotes for strings with spaces.
  - Variables are case-sensitive.
- **Example**:
  ```bash
  #!/bin/bash
  name="Alice"
  count=5
  echo "Hello, $name! You have $count messages."
  ```
  **Output**: `Hello, Alice! You have 5 messages.`
- **Use Case**: Store file paths, user input, or counters for reuse in scripts.

#### Quoting
- **What is it?**: Quoting controls how Bash interprets text (e.g., spaces, variables).
- **Types**:
  - **Single Quotes (`'`)**: Treat everything literally (no variable expansion).
  - **Double Quotes (`"`)**: Allow variable expansion and command substitution.
  - **No Quotes**: Variables expand, but spaces split words (can cause issues).
- **Example**:
  ```bash
  #!/bin/bash
  name="Bob"
  echo 'Name: $name'          # Output: Name: $name (literal)
  echo "Name: $name"          # Output: Name: Bob (variable expanded)
  echo Name: $name            # Output: Name: Bob (but risky with spaces)
  ```
- **Use Case**: Use double quotes for variables in commands, single quotes for literal text (e.g., regex patterns).

#### Conditionals (`if`, `case`)
- **What are they?**: Let scripts make decisions based on conditions.
- **If Statement**:
  - Syntax:
    ```bash
    if [ condition ]; then
      # Commands
    else
      # Other commands
    fi
    ```
  - Common tests:
    - `[ -f file ]`: Check if file exists.
    - `[ -d dir ]`: Check if directory exists.
    - `[ "$var" = "value" ]`: Compare strings.
    - `[ $num -eq 5 ]`: Compare numbers (`-eq`, `-ne`, `-lt`, `-gt`).
- **Example**:
  ```bash
  #!/bin/bash
  file="data.txt"
  if [ -f "$file" ]; then
    echo "$file exists!"
  else
    echo "$file does not exist."
  fi
  ```
  **Output**: Depends on whether `data.txt` exists.
- **Case Statement**:
  - Syntax:
    ```bash
    case $variable in
      pattern1) commands ;;
      pattern2) commands ;;
      *) default commands ;;
    esac
    ```
  - Matches variable against patterns.
- **Example**:
  ```bash
  #!/bin/bash
  day="Monday"
  case $day in
    Monday) echo "Start of the week!" ;;
    Friday) echo "Weekend soon!" ;;
    *) echo "Just another day." ;;
  esac
  ```
  **Output**: `Start of the week!`
- **Use Case**: Use `if` for complex conditions (e.g., file checks) and `case` for multiple-choice scenarios (e.g., menu scripts).

#### Loops (`for`, `while`, `until`)
- **What are they?**: Repeat commands multiple times.
- **For Loop**:
  - Iterates over a list (e.g., files, numbers).
  - Syntax:
    ```bash
    for item in list; do
      # Commands
    done
    ```
  - Example:
    ```bash
    #!/bin/bash
    for file in *.txt; do
      echo "Found: $file"
    done
    ```
    **Output**: Lists all `.txt` files in the current directory.
- **While Loop**:
  - Runs as long as a condition is true.
  - Syntax:
    ```bash
    while [ condition ]; do
      # Commands
    done
    ```
  - Example:
    ```bash
    #!/bin/bash
    count=1
    while [ $count -le 5 ]; do
      echo "Count: $count"
      ((count++))
    done
    ```
    **Output**: `Count: 1` to `Count: 5`.
- **Until Loop**:
  - Runs until a condition is true (opposite of `while`).
  - Example:
    ```bash
    #!/bin/bash
    count=1
    until [ $count -gt 5 ]; do
      echo "Count: $count"
      ((count++))
    done
    ```
    **Output**: Same as `while` example.
- **Use Case**: Use `for` for known lists (e.g., files), `while` for dynamic conditions (e.g., reading input), and `until` for rare cases where you wait for a condition to become true.

#### Functions, Exit Codes, Return Values
- **Functions**:
  - Reusable blocks of code.
  - Syntax:
    ```bash
    function_name() {
      # Commands
    }
    ```
  - Example:
    ```bash
    #!/bin/bash
    greet() {
      echo "Hello, $1!"
    }
    greet "Alice"
    ```
    **Output**: `Hello, Alice!`
  - `$1`, `$2`: Function arguments.
- **Exit Codes**:
  - Every command returns an exit code (0 = success, non-zero = failure).
  - Check with `$?`.
  - Example:
    ```bash
    ls /nonexistent
    echo $?
    # Output: 2 (ls failed)
    ```
  - Use in scripts:
    ```bash
    #!/bin/bash
    ls /tmp
    if [ $? -eq 0 ]; then
      echo "Command succeeded."
    else
      echo "Command failed."
    fi
    ```
- **Return Values**:
  - Functions can return values using `return` (for numbers) or `echo` (for strings).
  - Example:
    ```bash
    #!/bin/bash
    add() {
      result=$(( $1 + $2 ))
      echo $result
    }
    sum=$(add 3 5)
    echo "Sum: $sum"
    ```
    **Output**: `Sum: 8`
- **Use Case**: Functions modularize scripts (e.g., reusable backup logic). Exit codes ensure error handling.

---
