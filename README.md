<h1 align="center">BeSimulator: A Large Language Model Powered Text-based 
Behavior Simulator</h1>


<div align="center">

[![arXiv](https://img.shields.io/badge/arXiv-2409.15865-b31b1b.svg)](https://arxiv.org/abs/2409.15865)
![Python](https://img.shields.io/badge/python-3.9-blue)
</div>


A modular LLM-powered framework designed to efficiently simulate complex robotic behavior architectures, such as Behavior Trees (BTs), Finite State Machines (FSMs), and Hierarchical Task Networks (HTNs), as an effort towards behavior simulation in text-based environments.


______________________________________________________________________


## 📦 Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Dawn888888/BeSimulator.git
    cd BeSimulator
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    conda create --name besimulator python=3.9
    conda activate besimulator
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## ⚙️ Configuration

Before running BeSimulator, you must set up your API keys.
```
export OPENAI_API_KEY=<your_api_key>
```

*Replace the placeholder text with your actual API keys.*

## 🚀 Quick Start

Here is a basic example to run a Behavior Tree (BT) simulation using the DeepSeek model.

    ```
    python main.py --llm_model deepseek-chat --category good --run_task_id 1
    ```

## 📚 Citation
If you use any of this work, it would be really nice if you could please cite 🥺 :

```
@article{wang2024besimulator,
  title={BeSimulator: A Large Language Model Powered Text-based Behavior Simulator},
  author={Wang, Jianan and Li, Bin and Wang, Xueying and Li, Fu and Wu, Yunlong and Chen, Juan and Yi, Xiaodong},
  journal={arXiv preprint arXiv:2409.15865},
  year={2024}
}
```