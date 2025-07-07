
---

# 📊 **Weights & Biases (WandB) — Complete Guide**

---

## ✅ What is WandB?

**Weights & Biases (WandB)** is a platform to help **track machine learning experiments**, **visualize metrics**, **compare models**, and **collaborate** across teams.

It's especially useful for:

* 🧪 Experiment Tracking
* 📈 Metrics Visualization
* 🔎 Hyperparameter Tuning
* 🏗️ Model Versioning
* ⚙️ Pipeline Logging
* 🌐 Model Monitoring (Production)

WandB integrates with **TensorFlow**, **PyTorch**, **Keras**, **scikit-learn**, **XGBoost**, **Hugging Face**, and even **LangChain**, **OpenAI** and **LLMs**.

---

## 🛠️ Core Components of WandB

| Component        | Purpose                                           |
| ---------------- | ------------------------------------------------- |
| `wandb.init()`   | Initialize a run/experiment                       |
| `wandb.log()`    | Log metrics, images, charts                       |
| `wandb.config`   | Log hyperparameters                               |
| `wandb.save()`   | Save artifacts, files                             |
| `wandb.Artifact` | Versioned datasets, models                        |
| `wandb.Table`    | Structured data (for logging rows, results, etc.) |
| `wandb.sweep()`  | Automate hyperparameter tuning                    |

---

## 🧪 1. **Experiment Tracking**

### 🔧 Setup

Install WandB:

```bash
pip install wandb
```

Login:

```bash
wandb login
```

### 🧬 Example (PyTorch)

```python
import wandb

# 1. Initialize project
wandb.init(project="my-cool-experiment")

# 2. Log config
wandb.config.batch_size = 32
wandb.config.learning_rate = 0.001

# 3. Training loop
for epoch in range(10):
    train_loss = 0.5 - 0.05 * epoch
    val_acc = 0.7 + 0.02 * epoch
    
    # Log metrics
    wandb.log({"epoch": epoch, "train_loss": train_loss, "val_acc": val_acc})
```

Go to: [https://wandb.ai/](https://wandb.ai/) → see metrics plotted in real-time 🚀

---

## 🧮 2. **Hyperparameter Tuning with Sweeps**

### 🔁 What is a Sweep?

WandB Sweeps lets you define a **search space** of hyperparameters and automatically run multiple experiments to find the best configuration.

### 📘 sweep.yaml

```yaml
method: bayes  # grid / random / bayes
metric:
  name: val_acc
  goal: maximize
parameters:
  learning_rate:
    min: 0.0001
    max: 0.1
  batch_size:
    values: [16, 32, 64]
```

### 🧪 Usage

1. Define sweep:

```bash
wandb sweep sweep.yaml
```

2. Launch agents:

```bash
wandb agent <SWEEP_ID>
```

---

## 📦 3. **Artifact Management**

### 🧠 Why Artifacts?

* Track **datasets**, **models**, and **intermediate files**
* Auto-versioned and stored with metadata

### 🛠️ Code Example

```python
artifact = wandb.Artifact("model-v1", type="model")
artifact.add_file("best_model.pt")
wandb.log_artifact(artifact)
```

Later you can retrieve:

```python
artifact = run.use_artifact("model-v1:latest")
artifact.download()
```

---

## 📉 4. **Visualizations & Dashboards**

* Line plots, bar charts, histograms
* Compare runs across metrics
* Create **Reports**: Collaborative experiment notebooks with charts & notes
* Example: confusion matrices, ROC curves, embeddings, gradients

```python
wandb.log({"conf_matrix": wandb.plot.confusion_matrix(...)})
```

---

## 🧾 5. **Integration with ML Libraries**

WandB supports plug-and-play integration with:

| Library                                  | Integration                            |
| ---------------------------------------- | -------------------------------------- |
| **Keras**                                | `callbacks=[WandbCallback()]`          |
| **PyTorch Lightning**                    | `Trainer(logger=WandbLogger())`        |
| **Transformers (HF)**                    | `TrainingArguments(report_to="wandb")` |
| **Scikit-learn**                         | Manual logging                         |
| **FastAI**, **XGBoost**, **spaCy**, etc. | Native/Manual support                  |

---

## 🧰 6. **Production Monitoring (WandB Traces & Prompts)**

Especially for **LLMs & APIs**:

### 🧠 Log Prompt + Response

```python
wandb.init(project="rag-qa")
wandb.log({
  "prompt": "What is the capital of France?",
  "response": "Paris",
  "context": "France is a country in Europe..."
})
```

You can trace performance, latency, and accuracy of prompts.

---

## 🔐 7. **Advanced Features**

* ✅ **Teams & Projects**
* 🔁 **Reproducibility via config snapshots**
* 🧪 **Versioned experiments & runs**
* 💾 **Offline logging** (`wandb offline`)
* 🔄 **Resume interrupted runs**
* 🌐 **Private/self-hosted WandB server**
* 🧩 **Custom Panels & Dashboards**
* 🔍 **Compare hundreds of runs side-by-side**

---

## 🧑‍💻 Real Use Cases

| Use Case                    | How WandB Helps                  |
| --------------------------- | -------------------------------- |
| Track ML model experiments  | `wandb.log()` with metrics       |
| Compare 100s of model runs  | Dashboard + Filtering            |
| Find best hyperparameters   | Sweeps                           |
| Track model/data versioning | Artifacts                        |
| Analyze LLM prompt behavior | `wandb.log()` with text + Traces |
| Collaborate with team       | Reports, Workspaces              |

---

## 🧠 Real Projects Ideas

1. **CNN for Image Classification + WandB Logging**
2. **HuggingFace Sentiment Classifier + Sweeps**
3. **LangChain QA System + Prompt Logging**
4. **MLOps Pipeline (Airflow/ZenML) + Artifacts**
5. **Fine-tune LLaMA model and visualize attention with WandB**

---

## 📚 Learning Resources

* [wandb.ai](https://wandb.ai/)
* [WandB Docs](https://docs.wandb.ai/)
* [WandB Examples GitHub](https://github.com/wandb/examples)
* [Integrations List](https://docs.wandb.ai/guides/integrations)
* [WandB Reports Showcase](https://wandb.ai/site/reports)

---

## ⚙️ Optional Setup for Projects

```
my_project/
├── main.py
├── config.yaml
├── wandb/
│   └── artifacts/
├── logs/
├── models/
└── sweep.yaml
```

---


