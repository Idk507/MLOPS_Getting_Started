
# GitHub Actions — Complete Guide (Beginner to Advanced)

## Table of Contents
1. [What is GitHub Actions?](#1-what-is-github-actions)
2. [Core Concepts](#2-core-concepts)
3. [Where Workflow Files Live](#3-where-workflow-files-live)
4. [Basic YAML Structure Explained](#4-basic-yaml-structure-explained)
5. [Triggers (`on`) — Every Way to Start a Workflow](#5-triggers-on)
6. [Jobs — Deep Dive](#6-jobs--deep-dive)
7. [Steps — Deep Dive](#7-steps--deep-dive)
8. [Environment Variables & Secrets](#8-environment-variables--secrets)
9. [Conditionals (`if`)](#9-conditionals-if)
10. [Matrix Builds (Running Many Combinations)](#10-matrix-builds)
11. [Artifacts — Saving Files Between Jobs](#11-artifacts)
12. [Caching — Speeding Things Up](#12-caching)
13. [Reusable Workflows](#13-reusable-workflows)
14. [Composite Actions](#14-composite-actions)
15. [Custom Actions (Docker & JavaScript)](#15-custom-actions)
16. [Environments & Approvals](#16-environments--approvals)
17. [Permissions & Security](#17-permissions--security)
18. [Concurrency Control](#18-concurrency-control)
19. [Full Real-World Example](#19-full-real-world-example)
20. [Debugging & Troubleshooting](#20-debugging--troubleshooting)
21. [Useful CLI Commands (`gh`)](#21-useful-cli-commands-gh)
22. [Glossary — Every Keyword Cheat Sheet](#22-glossary--every-keyword-cheat-sheet)

---

## 1. What is GitHub Actions?

GitHub Actions is GitHub's built-in **automation tool**. It lets you run tasks automatically whenever something happens in your repository — like pushing code, opening a pull request, or on a schedule (like a cron job).

Think of it like a robot assistant that watches your repo. You tell it:
> "When X happens, do Y."

Common uses:
- Run tests automatically when someone pushes code (**CI** — Continuous Integration)
- Automatically deploy your app when code is merged to `main` (**CD** — Continuous Deployment)
- Auto-label issues, auto-close stale PRs, send Slack notifications, build Docker images, publish npm packages, etc.

Everything is defined in **YAML files** stored inside your repository. No external tool needed — it's free (with limits) for public repos and comes with a generous free tier for private repos too.

---

## 2. Core Concepts

Before touching YAML, understand these building blocks — they form a hierarchy:

```
Workflow
 └── Trigger (on:)
 └── Job(s)
      └── Runner (the machine that executes the job)
      └── Step(s)
           └── Action OR Shell command
```

| Term | Simple Meaning |
|---|---|
| **Workflow** | The whole automation defined in one `.yml` file. E.g., "Test and Deploy". |
| **Event/Trigger** | What causes the workflow to run (push, pull request, schedule, manual click, etc.) |
| **Job** | A group of steps that run together on the same machine. A workflow can have multiple jobs. By default, jobs run **in parallel** unless you tell them not to. |
| **Runner** | The virtual machine (Linux/Windows/Mac) that actually executes your job. GitHub provides free ones, or you can host your own. |
| **Step** | A single task inside a job — either running a shell command or using a pre-built "Action". |
| **Action** | A reusable piece of code someone already wrote (by GitHub, a third party, or you) that does one job — e.g., "checkout my code", "setup Node.js", "deploy to AWS". |
| **Artifact** | A file or folder produced by a job that you want to keep or pass to another job. |
| **Secret** | An encrypted variable (like a password or API key) stored safely in GitHub settings, used inside workflows. |

---

## 3. Where Workflow Files Live

All workflow files must be placed here:

```
your-repo/
└── .github/
    └── workflows/
        ├── ci.yml
        ├── deploy.yml
        └── nightly-tests.yml
```

Rules:
- Folder name **must** be exactly `.github/workflows/`
- File extension must be `.yml` or `.yaml`
- You can have **as many workflow files as you want** — each one is independent
- GitHub automatically detects and runs any file in this folder when its trigger condition is met

---

## 4. Basic YAML Structure Explained

Here's the smallest possible working workflow, explained line by line:

```yaml
name: My First Workflow        # (1) Display name shown in the "Actions" tab

on: push                       # (2) Trigger: run this workflow every time someone pushes code

jobs:                          # (3) Start defining jobs (you can have multiple)
  say-hello:                   # (4) Job ID (your own name, no spaces, used internally)
    runs-on: ubuntu-latest     # (5) Which OS/machine to run this job on

    steps:                     # (6) List of steps to execute, in order
      - name: Print a message  # (7) Human-readable name for this step (optional but recommended)
        run: echo "Hello World"   # (8) The actual shell command to execute
```

### Line-by-line purpose:

| Keyword | Purpose |
|---|---|
| `name` | Just a label. Shows up in GitHub's UI. Optional — if omitted, GitHub uses the file path. |
| `on` | **Required.** Defines the event(s) that trigger this workflow. |
| `jobs` | **Required.** Container for one or more jobs. |
| `<job_id>` (e.g. `say-hello`) | You choose this name. It's the internal identifier for the job. |
| `runs-on` | **Required.** Tells GitHub which virtual machine image to use (`ubuntu-latest`, `windows-latest`, `macos-latest`, or a self-hosted label). |
| `steps` | **Required.** A list (notice the `-` dash = YAML list item) of actions/commands to run in sequence. |
| `run` | Executes a shell/terminal command directly. |
| `uses` | (not in example above) Executes someone else's pre-built Action instead of a raw command. |

> **YAML basics reminder:** Indentation matters (use spaces, not tabs). A `-` means "this is one item in a list." A `key: value` pair is how you set configuration.

---

## 5. Triggers (`on`)

The `on` key defines **when** the workflow runs. This is one of the most important parts.

### Single event
```yaml
on: push
```

### Multiple events
```yaml
on: [push, pull_request]
```

### Event with filters (most common — advanced form)
```yaml
on:
  push:
    branches:
      - main
      - "release/**"
    paths:
      - "src/**"          # only run if files inside src/ changed
      - "!src/**/*.md"    # but ignore markdown file changes
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened]
```

### All common trigger types:

| Trigger | Purpose |
|---|---|
| `push` | Runs when commits are pushed to the repo |
| `pull_request` | Runs when a PR is opened/updated against a branch |
| `pull_request_target` | Like `pull_request` but runs with access to secrets (careful — security-sensitive) |
| `workflow_dispatch` | Lets you **manually** trigger the workflow from the GitHub UI (with optional input fields) |
| `schedule` | Runs on a timer using cron syntax |
| `release` | Runs when a release is published/created |
| `issues` | Runs on issue events (opened, labeled, closed, etc.) |
| `issue_comment` | Runs when someone comments on an issue or PR |
| `workflow_call` | Marks this workflow as **reusable** by other workflows |
| `workflow_run` | Runs after another specified workflow completes |
| `repository_dispatch` | Triggered via an external API call (custom events) |

### Example: Manual trigger with inputs
```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: "Which environment to deploy to"
        required: true
        default: "staging"
        type: choice
        options:
          - staging
          - production
```
This creates a "Run workflow" button in GitHub's UI where users pick an environment from a dropdown.

### Example: Scheduled (cron) trigger
```yaml
on:
  schedule:
    - cron: "0 0 * * *"   # runs every day at midnight UTC
```
Cron format: `minute hour day-of-month month day-of-week`

---

## 6. Jobs — Deep Dive

```yaml
jobs:
  build:
    name: Build the app
    runs-on: ubuntu-latest
    timeout-minutes: 15
    continue-on-error: false
    needs: []                     # jobs that must finish first (dependency)
    outputs:
      build-version: ${{ steps.get_version.outputs.version }}
    steps:
      - run: echo "building..."
```

| Keyword | Purpose |
|---|---|
| `runs-on` | The machine/OS to run the job on (`ubuntu-latest`, `windows-latest`, `macos-latest`, `self-hosted`, or custom labels) |
| `needs` | Makes this job wait for another job to finish first. `needs: build` = "don't start until the `build` job succeeds." Without this, all jobs run in parallel. |
| `if` | Conditionally skip a whole job (see section 9) |
| `timeout-minutes` | Auto-cancels the job if it runs longer than this (prevents stuck/hung jobs from running forever) |
| `continue-on-error` | If `true`, the workflow keeps going even if this job fails |
| `outputs` | Lets a job expose values that other (downstream) jobs can use |
| `strategy` | Used for matrix builds (section 10) |
| `environment` | Ties the job to a GitHub Environment (with approval gates, secrets — section 16) |
| `permissions` | Controls what the auto-generated `GITHUB_TOKEN` can access for this job |
| `defaults` | Set default shell/working-directory for all steps in this job |
| `container` | Run the job inside a specific Docker container instead of directly on the VM |

### Job dependency example
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps: [...]

  test:
    needs: build          # waits for build to finish successfully
    runs-on: ubuntu-latest
    steps: [...]

  deploy:
    needs: [build, test]  # waits for BOTH to finish
    runs-on: ubuntu-latest
    steps: [...]
```

---

## 7. Steps — Deep Dive

A step does ONE of two things: runs a **command** (`run`) or uses a pre-built **Action** (`uses`).

```yaml
steps:
  - name: Checkout code                # human-readable label
    uses: actions/checkout@v4          # use a pre-built action (checks out your repo's code)

  - name: Setup Node.js
    uses: actions/setup-node@v4
    with:                              # inputs passed to the action
      node-version: "20"

  - name: Install dependencies
    run: npm install                   # run a raw shell command

  - name: Run tests
    run: npm test
    env:                               # environment variables just for this step
      NODE_ENV: test

  - name: Save output for later steps
    id: my_step                        # give this step an ID so others can reference its output
    run: echo "result=success" >> "$GITHUB_OUTPUT"
```

| Keyword | Purpose |
|---|---|
| `name` | Label shown in logs (optional, but very helpful for readability) |
| `uses` | Points to a reusable Action, format: `owner/repo@version` or `./local-path` for local actions |
| `run` | Runs a shell command (bash by default on Linux/Mac, PowerShell on Windows) |
| `with` | Passes input parameters into an action (like function arguments) |
| `env` | Sets environment variables available only to this step |
| `id` | Names this step so you can reference its outputs elsewhere: `${{ steps.my_step.outputs.result }}` |
| `if` | Run this step only if a condition is true |
| `working-directory` | Run the command from inside a specific folder |
| `continue-on-error` | Don't fail the whole job if this one step fails |
| `shell` | Force a specific shell (`bash`, `pwsh`, `cmd`, `python`, etc.) |

### Why `uses` vs `run`?
- Use `run` for simple shell commands (`npm install`, `pytest`, `echo`, etc.)
- Use `uses` when someone has already built a reusable, tested component for a common task (checkout code, setup a language, deploy to cloud, send a Slack message). This saves you from reinventing the wheel. Browse them at the [GitHub Marketplace](https://github.com/marketplace?type=actions).

### `@v4` — what does the version mean?
Actions are versioned like packages. `actions/checkout@v4` means "use version 4 of the checkout action." Always pin a version (avoid `@main` in production) so your workflow doesn't break if the action changes.

---

## 8. Environment Variables & Secrets

### Environment variables — 3 levels (workflow, job, step)
```yaml
env:                          # available to ALL jobs in the workflow
  GLOBAL_VAR: "hello"

jobs:
  build:
    env:                       # available to all steps in THIS job only
      JOB_VAR: "world"
    runs-on: ubuntu-latest
    steps:
      - run: echo $GLOBAL_VAR $JOB_VAR
        env:                    # available to THIS step only
          STEP_VAR: "!"
```

### Secrets — for sensitive data (API keys, passwords, tokens)
Secrets are **never** written directly in YAML. You add them in:
`Repo → Settings → Secrets and variables → Actions → New repository secret`

Then reference them like this:
```yaml
steps:
  - name: Deploy
    run: ./deploy.sh
    env:
      API_KEY: ${{ secrets.MY_API_KEY }}
```

GitHub automatically masks secret values in logs so they don't leak.

### The built-in `GITHUB_TOKEN`
Every workflow run automatically gets a temporary token: `${{ secrets.GITHUB_TOKEN }}`. It's used to authenticate API calls back to GitHub (e.g., commenting on a PR, creating a release) without you needing to create your own token.

---

## 9. Conditionals (`if`)

Run a step or job only when a condition is true.

```yaml
steps:
  - name: Only run on main branch
    if: github.ref == 'refs/heads/main'
    run: echo "This is main!"

  - name: Only run if previous step failed
    if: failure()
    run: echo "Something broke"

  - name: Always run (e.g., cleanup), even if earlier steps failed
    if: always()
    run: echo "Cleaning up..."

  - name: Only on pull requests
    if: github.event_name == 'pull_request'
    run: echo "This is a PR"
```

### Common built-in functions used inside `if`:
| Function | Meaning |
|---|---|
| `success()` | True if all previous steps succeeded (this is the default even without `if`) |
| `failure()` | True if any previous step failed |
| `always()` | Always runs, regardless of success/failure — good for cleanup/notifications |
| `cancelled()` | True if the workflow was manually cancelled |

---

## 10. Matrix Builds

Run the same job multiple times with different configurations (e.g., test across multiple Node/Python versions or OSes) — all in parallel.

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        node-version: [18, 20, 22]
      fail-fast: false        # if one combination fails, don't cancel the others
      max-parallel: 3         # limit how many run at once
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm test
```
This example automatically creates **9 jobs** (3 OS × 3 Node versions) — all run in parallel, each with a different combination.

You can also exclude/include specific combinations:
```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest]
    node: [18, 20]
    exclude:
      - os: windows-latest
        node: 18
    include:
      - os: macos-latest
        node: 22
```

---

## 11. Artifacts

Artifacts let you save files from one job and use them in another job, or download them after the workflow finishes (like build outputs, test reports, coverage files).

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: mkdir dist && echo "built file" > dist/app.txt
      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: my-build-output
          path: dist/
          retention-days: 5      # optional, how long to keep it (default 90)

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Download artifact
        uses: actions/download-artifact@v4
        with:
          name: my-build-output
          path: dist/
      - run: ls dist/
```

---

## 12. Caching

Caching speeds up workflows by reusing dependencies (like `node_modules`) between runs instead of reinstalling every time.

```yaml
steps:
  - uses: actions/checkout@v4

  - name: Cache node_modules
    uses: actions/cache@v4
    with:
      path: ~/.npm
      key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}
      restore-keys: |
        ${{ runner.os }}-npm-

  - run: npm install
```

- `key`: a unique identifier for this cache. If the `package-lock.json` hash changes, a new cache is created.
- `restore-keys`: fallback keys to use a partial match if an exact key isn't found.

Many setup actions (like `setup-node`) also have built-in caching:
```yaml
- uses: actions/setup-node@v4
  with:
    node-version: "20"
    cache: "npm"
```

---

## 13. Reusable Workflows

Instead of copy-pasting the same YAML across repos/files, define a workflow once and call it from others.

**Callable workflow** (`.github/workflows/reusable-deploy.yml`):
```yaml
on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
    secrets:
      DEPLOY_KEY:
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying to ${{ inputs.environment }}"
        env:
          KEY: ${{ secrets.DEPLOY_KEY }}
```

**Caller workflow** (another file):
```yaml
jobs:
  call-deploy:
    uses: ./.github/workflows/reusable-deploy.yml
    with:
      environment: production
    secrets:
      DEPLOY_KEY: ${{ secrets.PROD_DEPLOY_KEY }}
```

This is great for large orgs with many repos that need the same CI/CD logic.

---

## 14. Composite Actions

A composite action bundles multiple **steps** into one reusable action (used with `uses`, unlike reusable workflows which are used with `uses` at the job level too, but composite actions work at the step level and live in their own folder).

`.github/actions/setup-project/action.yml`:
```yaml
name: "Setup Project"
description: "Installs dependencies and sets up environment"
inputs:
  node-version:
    required: false
    default: "20"
runs:
  using: "composite"
  steps:
    - uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}
      shell: bash
    - run: npm install
      shell: bash
```

Used like this in a workflow:
```yaml
steps:
  - uses: actions/checkout@v4
  - uses: ./.github/actions/setup-project
    with:
      node-version: "22"
```

---

## 15. Custom Actions

If Marketplace actions don't do what you need, you can build your own:

| Type | How it works | When to use |
|---|---|---|
| **Composite Action** | Combines existing steps/actions (YAML only, no code) | Simplest — reuse a sequence of steps |
| **JavaScript Action** | Write custom Node.js code, packaged as an action | Fast, no Docker overhead, needs Node runtime |
| **Docker Container Action** | Package any language/tool inside a Docker container | Maximum flexibility, any language, slower startup |

Basic structure of a Docker action (`action.yml`):
```yaml
name: "My Custom Action"
description: "Does something custom"
inputs:
  my-input:
    required: true
runs:
  using: "docker"
  image: "Dockerfile"
  args:
    - ${{ inputs.my-input }}
```

---

## 16. Environments & Approvals

GitHub "Environments" (Settings → Environments) let you add **manual approval gates**, environment-specific secrets, and deployment protection rules — very useful for production deployments.

```yaml
jobs:
  deploy-prod:
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://myapp.com
    steps:
      - run: ./deploy.sh
```
If you configure "required reviewers" on the `production` environment in GitHub settings, the workflow will **pause and wait** for a human to click "Approve" before this job runs.

---

## 17. Permissions & Security

By default, the `GITHUB_TOKEN` has broad permissions. Best practice: restrict it to only what's needed.

```yaml
permissions:
  contents: read       # read repo code
  pull-requests: write # allowed to comment on PRs
  issues: write
```

Common permission scopes: `contents`, `issues`, `pull-requests`, `actions`, `packages`, `deployments`, `id-token` (used for OIDC cloud auth), `checks`, `statuses`.

### Security best practices:
- Always **pin action versions** (`@v4`, or even better, a commit SHA) to avoid supply-chain attacks from a compromised action.
- Avoid `pull_request_target` unless absolutely necessary — it exposes secrets to code from forks.
- Set `permissions` explicitly rather than relying on defaults.
- Never hardcode secrets in YAML — always use `secrets.*`.
- Use **OIDC (OpenID Connect)** instead of long-lived cloud credentials when deploying to AWS/Azure/GCP.

---

## 18. Concurrency Control

Prevents multiple runs of the same workflow from overlapping (e.g., stop old deployments if a newer commit is pushed).

```yaml
concurrency:
  group: deploy-${{ github.ref }}
  cancel-in-progress: true
```
This cancels any in-progress run in the same "group" when a new one starts — useful for saving time/money on CI minutes.

---

## 19. Full Real-World Example

A complete CI/CD pipeline: test → build → deploy (only from `main`, with manual approval).

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18, 20]
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: "npm"

      - run: npm install
      - run: npm test

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
      - run: npm install
      - run: npm run build

      - name: Upload build artifact
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://myapp.com
    steps:
      - name: Download build artifact
        uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/

      - name: Deploy
        run: echo "Deploying to production..."
        env:
          DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
```

---

## 20. Debugging & Troubleshooting

- **View logs**: Go to the "Actions" tab in your repo → click the workflow run → click a job to expand step logs.
- **Re-run failed jobs**: Button available in the UI, top-right of a workflow run.
- **Enable debug logging**: Add these repository secrets:
  - `ACTIONS_STEP_DEBUG = true`
  - `ACTIONS_RUNNER_DEBUG = true`
- **SSH into a runner for live debugging**: Use the community action `mxschmitt/action-tmate` to open an SSH session into the runner mid-workflow.
- **Validate YAML syntax**: Use the GitHub web editor (it flags YAML errors) or a local YAML linter before pushing.
- **Common errors**:
  | Error | Likely Cause |
  |---|---|
  | `Invalid workflow file` | Bad indentation or YAML syntax |
  | `Resource not accessible by integration` | Missing `permissions` for the `GITHUB_TOKEN` |
  | Job stuck "Queued" forever | No available runner matching `runs-on` label (common with self-hosted) |
  | Secret shows as empty | Secret not added at repo/org level, or wrong name |

---

## 21. Useful CLI Commands (`gh`)

The GitHub CLI (`gh`) lets you interact with Actions from your terminal.

```bash
# List recent workflow runs
gh run list

# View details of a specific run
gh run view <run-id>

# Watch a run live (streams logs)
gh run watch <run-id>

# Re-run a failed workflow
gh run rerun <run-id>

# Manually trigger a workflow_dispatch workflow
gh workflow run <workflow-file-name>

# List all workflows in the repo
gh workflow list

# Download artifacts from a run
gh run download <run-id>
```

---

## 22. Glossary — Every Keyword Cheat Sheet

| Keyword | Level | Purpose |
|---|---|---|
| `name` | workflow/job/step | Display label |
| `on` | workflow | Defines trigger events |
| `jobs` | workflow | Container for jobs |
| `runs-on` | job | OS/machine for the job |
| `needs` | job | Job dependency ordering |
| `if` | job/step | Conditional execution |
| `steps` | job | List of tasks |
| `uses` | step | Run a pre-built action |
| `run` | step | Run a shell command |
| `with` | step | Inputs passed to an action |
| `env` | workflow/job/step | Environment variables |
| `id` | step | Reference name for outputs |
| `outputs` | job | Expose values to other jobs |
| `strategy.matrix` | job | Run job in multiple variations |
| `fail-fast` | job | Stop all matrix jobs if one fails |
| `continue-on-error` | job/step | Don't fail workflow on this failure |
| `timeout-minutes` | job/step | Max runtime before auto-cancel |
| `permissions` | workflow/job | Restrict `GITHUB_TOKEN` scopes |
| `concurrency` | workflow/job | Prevent/cancel overlapping runs |
| `environment` | job | Tie to a protected GitHub Environment |
| `secrets` | — | Encrypted sensitive values |
| `workflow_dispatch` | on | Manual trigger with optional inputs |
| `schedule` | on | Cron-based trigger |
| `workflow_call` | on | Makes a workflow reusable |
| `defaults` | workflow/job | Default shell/working-directory |
| `container` | job | Run job inside a Docker container |
| `working-directory` | step | Folder to run the command in |
| `shell` | step | Which shell to use |

---

## Quick Mental Model to Remember Everything

1. **A workflow is triggered by an event** (`on`).
2. **It contains jobs**, which run on **runners** (VMs), in parallel by default.
3. **Each job has steps**, run in order, top to bottom.
4. **Steps either run a command (`run`) or use someone's pre-built action (`uses`)**.
5. **Data flows between jobs via `outputs` and `artifacts`.**
6. **Secrets/env vars configure behavior without hardcoding sensitive info.**
7. **Matrix, caching, reusable workflows, and composite actions** exist purely to reduce repetition and speed things up as your pipeline grows.

