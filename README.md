# BeSimulator: A Large Language Model Powered Behavior Simulator

[![arXiv](https://img.shields.io/badge/arXiv-2409.15865-b31b1b.svg)](https://arxiv.org/abs/2409.15865)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](3.9)

A modular and extensible framework powered by Large Language Models (LLMs) designed to simulate complex behavior architectures—such as Behavior Trees (BTs), Finite State Machines (FSMs), and Hierarchical Task Networks (HTNs)—in text-based environments.

BeSimulator leverages the reasoning and generative capabilities of modern LLMs to create dynamic, believable agents for simulations, game prototyping, and AI research.

> **Paper**: For detailed methodology, experiments, and discussion, please see our preprint: **[BeSimulator: A Large Language Model Powered Text-based Behavior Simulator](https://arxiv.org/abs/1234.56789)** on arXiv.

## ✨ Key Features

*   **LLM-Powered Core:** Utilizes APIs from providers like OpenAI, Anthropic, and DeepSeek for sophisticated behavior generation and decision-making.
*   **Multi-Architecture Support:** Simulate various behavior modeling paradigms out-of-the-box (BT, FSM, HTN).
*   **Modular & Extensible:** Easily add new behavior models, LLM providers, or environments.
*   **Text-Based Environment Agnostic:** Designed to integrate with any text-based simulator or game (e.g., text adventures, interactive fiction).
*   **Detailed Logging:** Comprehensive logs for analyzing agent decision-making processes.

## 📦 Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/BeSimulator.git
    cd BeSimulator
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## ⚙️ Configuration

Before running BeSimulator, you must set up your API keys.

1.  Copy the example environment file:
    ```bash
    cp .env.example .env
    ```
2.  Edit the `.env` file and add your API keys:
    ```ini
    # For DeepSeek API
    DEEPSEEK_API_KEY=your_deepseek_api_key_here

    # For OpenAI API (optional)
    OPENAI_API_KEY=your_openai_api_key_here

    # For Anthropic API (optional)
    ANTHROPIC_API_KEY=your_anthropic_api_key_here
    ```
*Replace the placeholder text with your actual API keys.*

## 🚀 Quick Start

Here is a basic example to run a Behavior Tree (BT) simulation using the DeepSeek model.

```bash
python main.py --llm_model deepseek-chat --category good --run_task_id 1