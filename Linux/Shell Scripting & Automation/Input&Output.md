### 2. Input/Output

#### `read`
- **What is it?**: Reads user input or file data into variables.
- **Example**:
  ```bash
  #!/bin/bash
  echo "Enter your name:"
  read name
  echo "Hello, $name!"
  ```
  **Output**: Prompts for input, then prints it.
- **Options**:
  - `-p "Prompt"`: Show prompt.
  - `-s`: Silent mode (e.g., for passwords).
- **Use Case**: Collect user input for interactive scripts.

#### Redirections
- **Types**:
  - `>`: Overwrite output to a file.
  - `>>`: Append output to a file.
  - `2>`: Redirect errors.
  - `<`: Input from a file.
- **Examples**:
  ```bash
  # Overwrite
  echo "Log" > log.txt
  # Append
  echo "More" >> log.txt
  # Redirect errors
  ls /nonexistent 2> error.log
  # Input from file
  sort < input.txt
  ```
- **Use Case**: Save command output, log errors, or feed input to commands.

#### Here Documents
- **What is it?**: Provides multi-line input to a command using `<<`.
- **Example**:
  ```bash
  #!/bin/bash
  cat << EOF > file.txt
  Line 1
  Line 2
  EOF
  ```
  **Output**: Creates `file.txt` with two lines.
- **Use Case**: Write configuration files or multi-line input to commands.

#### String Manipulation
- **Techniques**:
  - **Parameter Expansion**: `${var#pattern}` (remove prefix), `${var%pattern}` (remove suffix).
  - **Substring**: `${var:start:length}`.
- **Example**:
  ```bash
  #!/bin/bash
  file="data.txt"
  echo "${file%.txt}"  # Remove .txt -> data
  echo "${file:0:4}"   # First 4 chars -> data
  ```
- **Use Case**: Clean file names or extract parts of strings.

#### Arrays
- **What are they?**: Store multiple values in a single variable.
- **Syntax**:
  - Declare: `array=(item1 item2 item3)`
  - Access: `${array[0]}` (first item), `${array[@]}` (all items).
- **Example**:
  ```bash
  #!/bin/bash
  files=(file1.txt file2.txt file3.txt)
  echo "First file: ${files[0]}"
  for file in "${files[@]}"; do
    echo "Processing: $file"
  done
  ```
  **Output**:
  ```
  First file: file1.txt
  Processing: file1.txt
  Processing: file2.txt
  Processing: file3.txt
  ```
- **Use Case**: Manage lists of files, users, or options.

---
