> **Language:** [**中文**](./README.md) | [**English**](./README_EN.md)

> **Note:** This project is an MVP implementation of a task-oriented, FSM-driven agent designed for high-reliability structured data extraction. Its core value lies in the architectural pattern, not just the extraction performance.

# Engineering Specification Extraction Agent

![Status](https://img.shields.io/badge/status-MVP-green)
![Version](https://img.shields.io/badge/version-2.3-blue)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

This is a **task-oriented, FSM-driven agent** for structured data extraction from engineering documents. It is designed for high-reliability, auditable, and automated workflows, such as extracting executable constraints from building codes, mechanical specifications, or compliance documents.

Unlike a general-purpose chatbot, this agent operates as a deterministic engine, prioritizing accuracy and traceability over conversational ability.

## ✨ Key Features

- **🤖 Self-Repair Mechanism:** Automatically detects, analyzes, and attempts to fix failed extractions (e.g., malformed JSON, missing required fields). This is the core of its engineering-grade reliability.
- **📄 Strict JSON Schema Output:** All outputs are rigorously validated against a predefined JSON schema, ensuring data consistency and immediate usability for downstream systems.
- **🔍 Full Traceability & Auditing:** Every extracted piece of data is linked back to its original source in the document (`source_ref`), and the entire process is logged step-by-step, including state transitions and repair attempts.
- **🎯 Task-Oriented & Non-Conversational:** Built as a pure extraction engine, not a chatbot. It follows a deterministic, state-driven process (`Plan -> Act -> Verify -> Repair`) to achieve its goal.

---

## 🚀 Quick Start: See Self-Repair in Action

We've made it easy to see the agent's core self-repair mechanism. The provided example is designed to fail on the first attempt and then repair itself.

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/yanzhao77/spec-extraction-agent.git
cd spec-extraction-agent

# Install dependencies
pip install -r requirements.txt

# Set your API Key (uses OpenAI-compatible APIs like Gemini)
export OPENAI_API_KEY="your_api_key_here"
```

### 2. One-Click Run Example

Run the example script. It will process a sample engineering document, intentionally trigger a validation failure, and demonstrate the self-repair loop.

```bash
python examples/run_example.py
```

### 3. Expected Output

You will see a detailed log in your console, showcasing the agent's entire process. The most important part is the **Validation -> Repair -> Validation** loop:

```log
# ... (Initial extraction logs)

[2025-12-30 10:30:24,440] INFO: STATE TRANSITION: EXTRACTION -> VALIDATION
[2025-12-30 10:30:24,440] WARNING: JSON parsing/validation failed for result from '...'. Error: LLM output is not a JSON array.
[2025-12-30 10:30:24,440] WARNING: Schema validation failed for item from '...'. Errors: [\"Numeric 'value' requires a 'unit'\"]
[2025-12-30 10:30:24,440] INFO: 5 items failed validation. Entering REPAIR state.

# --- The Self-Repair Loop Begins --- #
[2025-12-30 10:30:24,440] INFO: STATE TRANSITION: VALIDATION -> REPAIR
[2025-12-30 10:30:24,440] INFO: Attempting to repair item from '...' (Attempt 1)
[2025-12-30 10:30:27,851] INFO: HTTP Request: POST https://api.manus.im/api/llm-proxy/v1/chat/completions \"HTTP/1.1 200 OK\"

# --- Repair Succeeded, Re-Validating --- #
[2025-12-30 10:30:30,727] INFO: STATE TRANSITION: REPAIR -> VALIDATION
[2025-12-30 10:30:30,728] INFO: All items validated successfully.
[2025-12-30 10:30:30,728] INFO: STATE TRANSITION: VALIDATION -> FINALIZE

# ... (Final output generation)

✅ EXTRACTION COMPLETE: 21 constraints extracted and validated.

---

## 📂 Project Structure

```
spec-extraction-agent/
├── docs/                  # Detailed documentation
│   ├── TECHNICAL_WHITEPAPER.md  # System architecture, design principles, and performance.
│   └── API_DOCUMENTATION.md     # REST API interface for deploying the agent as a service.
├── examples/              # Example documents and run scripts
│   ├── GB50016_2014_sample.txt  # Sample engineering specification document.
│   └── run_example.py           # One-click script to run the demo.
├── src/                   # Core source code
│   └── agent.py               # The main FSM-driven agent logic.
├── .github/               # GitHub-specific files (CI, issue templates)
├── logs/                  # Log files are stored here by default.
├── README.md              # This file.
└── requirements.txt       # Python dependencies.
```

## ⚙️ System Architecture

The agent's behavior is governed by an 8-stage Finite State Machine (FSM), which ensures the process is deterministic and auditable. The `VALIDATION` -> `REPAIR` loop is the key to its robustness.

![State Machine](docs/state_machine.png)

For a deep dive into the architecture, design principles, and performance metrics, please see the [**Technical Whitepaper**](docs/TECHNICAL_WHITEPAPER.md).

## 🤝 Contributing

Contributions are welcome! Whether it's bug reports, feature requests, or code improvements, please feel free to open an issue or submit a pull request. See our [**Contributing Guidelines**](CONTRIBUTING.md) for more details.

## 📄 License

This project is licensed under the [MIT License](LICENSE).
