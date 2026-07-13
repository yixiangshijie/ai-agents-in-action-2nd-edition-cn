# AI Agents In Action (2nd Edition)

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/) [![License](https://img.shields.io/badge/license-MIT-green)](LICENSE) [![OpenAI](https://img.shields.io/badge/OpenAI-API-blue)](https://platform.openai.com/) [![MCP](https://img.shields.io/badge/Protocol-MCP-orange)](https://platform.openai.com/docs/guides/mcp)

This repository contains sample code for the book "Build a Deep Research Agent from Scratch." The code demonstrates how to create and run an AI agent using OpenAI's tools and APIs.

## Setup Instructions

### 1. Clone the Repository

To get started, clone this repository to your local machine:

```bash
git clone https://github.com/cxbxmxcx/AI-Agent-Workflows.git
cd AI-Agent-Workflows
```

### 2. Create Your Environment

This project requires **Python 3.11+**. Create and activate a Python virtual environment:

#### On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

#### On macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

If you prefer to use an external Python environment, ensure you set the Python path in VS Code:

1. Open the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P` on macOS).
2. Search for "Python: Select Interpreter."
3. Choose the Python interpreter for your environment.

### 3. Install Dependencies

#### Path A: Using VS Code Debugging

If you have VS Code, you can simply start debugging (press `F5`) to run the examples. The required dependencies will be installed automatically as part of the debugging process.

#### Path B: Manual Installation

Alternatively, you can manually install the dependencies using pip:

```bash
pip install -r requirements.txt
```

### 4. Configure the Environment

Create a `.env` file in the root directory to store your OpenAI API key. Use the provided `.env.example` file as a template:

#### Example `.env` file:

```
OPENAI_API_KEY=your_openai_api_key_here
```

Replace `your_openai_api_key_here` with your actual OpenAI API key. You can obtain an API key from [OpenAI's API Keys page](https://platform.openai.com/account/api-keys).

### 5. Run the Code

To execute the sample code, navigate to the desired chapter and run the Python file. For example:

```bash
python chapter_02/01_first_agent.py
```

This will run the agent and display the output in the terminal.

## Notes

- Ensure you are using the correct Python interpreter that matches your environment.
- The `.env` file should not be shared or committed to version control to keep your API key secure.
