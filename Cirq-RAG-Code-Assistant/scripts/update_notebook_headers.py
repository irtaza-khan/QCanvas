import json
import os
from pathlib import Path

notebooks_dir = Path("notebooks")

updates = {
    "02_embeddings.ipynb": {
        "title": "# Embeddings Notebook",
        "description": [
            "This notebook focuses on the generation and analysis of vector embeddings for quantum circuits and text descriptions.\n",
            "\n",
            "## Purpose\n",
            "The primary goal of this notebook is to demonstrate how the system converts natural language text and code into high-dimensional vector representations. Specifically, it covers:\n",
            "\n",
            "1.  **Embedding Generation**: Using the configured embedding model to transform text queries and Cirq code snippets into vector embeddings.\n",
            "2.  **Dimensionality Analysis**: Verifying the output dimensions of the embeddings to ensure compatibility with the vector store.\n",
            "3.  **Similarity Analysis**: Calculating cosine similarity between different embeddings to understand how the model perceives relationships between concepts.\n",
            "4.  **Visualization**: Using dimensionality reduction techniques to visualize the embedding space.\n",
            "\n",
            "## Usage\n",
            "Run the cells to load the embedding model, generate embeddings for sample texts, and visualize the results."
        ]
    },
    "03_vector_store.ipynb": {
        "title": "# Vector Store Notebook",
        "description": [
            "This notebook handles vector store operations for the RAG system.\n",
            "\n",
            "## Purpose\n",
            "This notebook demonstrates how to manage the vector database, which is crucial for efficient retrieval. It covers:\n",
            "\n",
            "1.  **Initialization**: Setting up the vector store using FAISS or ChromaDB.\n",
            "2.  **Indexing**: Adding embeddings along with their metadata to the index.\n",
            "3.  **Search**: Performing semantic similarity searches to find relevant documents for a given query.\n",
            "4.  **Persistence**: Saving and loading the vector index to/from disk.\n",
            "\n",
            "## Usage\n",
            "Import vector store functions from `src.rag.vector_store` and use this notebook to manage your vector database."
        ]
    },
    "04_rag_system.ipynb": {
        "title": "# RAG System Notebook",
        "description": [
            "This notebook demonstrates the full Retrieval-Augmented Generation (RAG) pipeline.\n",
            "\n",
            "## Purpose\n",
            "This notebook integrates the retrieval and generation components to create a complete RAG system. It demonstrates:\n",
            "\n",
            "1.  **Component Initialization**: Setting up the Retriever and Generator with the Knowledge Base.\n",
            "2.  **Context Retrieval**: Querying the knowledge base to find relevant code examples and documentation.\n",
            "3.  **Code Generation**: Using an LLM (e.g., OpenAI, Anthropic) augmented with retrieved context to generate Cirq code from natural language prompts.\n",
            "\n",
            "## Usage\n",
            "Run this notebook to test the end-to-end RAG pipeline, from query to generated code."
        ]
    },
    "05_designer_agent.ipynb": {
        "title": "# Designer Agent Notebook",
        "description": [
            "This notebook showcases the Designer Agent, the primary interface for code generation.\n",
            "\n",
            "## Purpose\n",
            "The Designer Agent is responsible for translating user requirements into quantum circuits. This notebook demonstrates:\n",
            "\n",
            "1.  **Agent Setup**: Initializing the Designer Agent with RAG capabilities.\n",
            "2.  **Task Execution**: Sending natural language tasks (e.g., \"Create a Teleportation circuit\") to the agent.\n",
            "3.  **Code Production**: Verifying that the agent produces syntactically correct Cirq code based on the input.\n",
            "\n",
            "## Usage\n",
            "Use this notebook to interact with the Designer Agent and generate initial circuit implementations."
        ]
    },
    "06_optimizer_agent.ipynb": {
        "title": "# Optimizer Agent Notebook",
        "description": [
            "This notebook demonstrates the Optimizer Agent's capabilities in improving quantum circuits.\n",
            "\n",
            "## Purpose\n",
            "The Optimizer Agent refines generated circuits to improve performance and efficiency. This notebook covers:\n",
            "\n",
            "1.  **Heuristic Optimization**: Applying standard optimizations like gate merging and dropping negligible operations.\n",
            "2.  **RL Optimization**: Using a Reinforcement Learning loop to iteratively improve circuit metrics (depth, gate count) based on a reward function.\n",
            "3.  **Comparison**: Analyzing and comparing the metrics of the original vs. optimized circuits.\n",
            "\n",
            "## Usage\n",
            "Run this notebook to optimize existing Cirq circuits and observe the improvements in circuit depth and gate count."
        ]
    },
    "07_validator_agent.ipynb": {
        "title": "# Validator Agent Notebook",
        "description": [
            "This notebook validates the quality and correctness of generated circuits.\n",
            "\n",
            "## Purpose\n",
            "The Validator Agent ensures that the generated code is functional and meets requirements. This notebook demonstrates:\n",
            "\n",
            "1.  **Syntax Checking**: Verifying that the code compiles without errors.\n",
            "2.  **Structural Analysis**: Checking for valid circuit construction and qubit usage.\n",
            "3.  **Simulation**: Running quantum simulations to verify that the circuit executes successfully.\n",
            "\n",
            "## Usage\n",
            "Use this notebook to test the validity of generated code and ensure it is ready for execution."
        ]
    },
    "08_educational_agent.ipynb": {
        "title": "# Educational Agent Notebook",
        "description": [
            "This notebook demonstrates the Educational Agent, which provides explanations and learning materials.\n",
            "\n",
            "## Purpose\n",
            "The Educational Agent enhances user understanding of the generated code. This notebook shows how to:\n",
            "\n",
            "1.  **Generate Explanations**: Produce step-by-step explanations of the quantum circuit's logic.\n",
            "2.  **Analyze Concepts**: Identify and explain key quantum concepts used in the code (e.g., superposition, entanglement).\n",
            "3.  **Retrieve Materials**: Fetch relevant tutorials and documentation from the knowledge base.\n",
            "\n",
            "## Usage\n",
            "Run this notebook to generate educational content accompanying the quantum circuits."
        ]
    },
    "09_orchestration.ipynb": {
        "title": "# Orchestration Notebook",
        "description": [
            "This notebook illustrates the Orchestrator component, which manages the multi-agent workflow.\n",
            "\n",
            "## Purpose\n",
            "The Orchestrator coordinates the specialized agents to deliver a complete solution. This notebook demonstrates:\n",
            "\n",
            "1.  **Workflow Management**: Chaining the Designer, Optimizer, Validator, and Educational agents.\n",
            "2.  **End-to-End Execution**: Processing a user query through the full pipeline: Design -> Optimize -> Validate -> Explain.\n",
            "3.  **Error Handling**: Managing failures and feedback between agents.\n",
            "\n",
            "## Usage\n",
            "Use this notebook to run the complete multi-agent system for high-quality code generation."
        ]
    },
    "10_evaluation.ipynb": {
        "title": "# Evaluation Notebook",
        "description": [
            "This notebook implements the evaluation framework for the system.\n",
            "\n",
            "## Purpose\n",
            "This notebook is used to assess the performance and quality of the system. It covers:\n",
            "\n",
            "1.  **Metrics Calculation**: Computing specific metrics like circuit depth, gate count, and code validity.\n",
            "2.  **Benchmarking**: Running the system against a set of standard quantum algorithms (e.g., VQE, Grover) to measure success rates.\n",
            "3.  **Ablation Studies**: systematically disabling components (e.g., RAG, Optimizer) to evaluate their impact on performance.\n",
            "\n",
            "## Usage\n",
            "Run this notebook to perform rigorous evaluation and benchmarking of the Cirq-RAG-Code-Assistant."
        ]
    },
    "11_training.ipynb": {
        "title": "# Training Notebook",
        "description": [
            "This notebook demonstrates the fine-tuning pipeline for the RAG system.\n",
            "\n",
            "## Purpose\n",
            "This notebook handles the training of the underlying models. It demonstrates:\n",
            "\n",
            "1.  **Dataset Preparation**: Loading and formatting data for training.\n",
            "2.  **Fine-Tuning**: Training the LLM and/or embedding models on Cirq-specific datasets to improve domain understanding.\n",
            "3.  **Model Saving**: Persisting the fine-tuned models for use in the RAG system.\n",
            "\n",
            "## Usage\n",
            "Use this notebook to fine-tune the models when new data becomes available or to improve performance on specific tasks."
        ]
    },
    "12_visualization.ipynb": {
        "title": "# Visualization Notebook",
        "description": [
            "This notebook provides visualization tools for analyzing the system's outputs.\n",
            "\n",
            "## Purpose\n",
            "Visualization is key for understanding quantum circuits and system performance. This notebook covers:\n",
            "\n",
            "1.  **Circuit Visualization**: Displaying quantum circuits using text diagrams or SVG.\n",
            "2.  **Metrics Plotting**: Visualizing evaluation metrics (e.g., success rates, latency) using charts.\n",
            "3.  **Data Inspection**: Visualizing embedding clusters or other internal data structures.\n",
            "\n",
            "## Usage\n",
            "Run this notebook to generate visual insights into the circuits and the system's performance."
        ]
    },
    "13_api_testing.ipynb": {
        "title": "# API Testing Notebook",
        "description": [
            "This notebook serves as a test suite for the system's internal APIs.\n",
            "\n",
            "## Purpose\n",
            "This notebook verifies the health and functionality of the system's core modules. It includes:\n",
            "\n",
            "1.  **Import Verification**: Ensuring all modules can be imported without errors.\n",
            "2.  **Component Testing**: Basic instantiation and execution tests for Retrievers, Generators, and Agents.\n",
            "3.  **Configuration Check**: Verifying that the configuration system loads settings correctly.\n",
            "\n",
            "## Usage\n",
            "Run this notebook to perform a quick health check of the system's codebase."
        ]
    },
    "14_cli_testing.ipynb": {
        "title": "# CLI Testing Notebook",
        "description": [
            "This notebook demonstrates the Command Line Interface (CLI) usage.\n",
            "\n",
            "## Purpose\n",
            "This notebook verifies the functionality of the system's CLI. It demonstrates:\n",
            "\n",
            "1.  **Command Availability**: Checking help messages and available commands.\n",
            "2.  **Simulation**: Running CLI commands (e.g., `generate`, `optimize`) from within the notebook to verify their behavior.\n",
            "\n",
            "## Usage\n",
            "Use this notebook to learn about and test the CLI commands provided by the system."
        ]
    }
}

for filename, content in updates.items():
    file_path = notebooks_dir / filename
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                notebook = json.load(f)
            
            # Update the first cell (assuming it's a markdown cell)
            if notebook['cells'] and notebook['cells'][0]['cell_type'] == 'markdown':
                notebook['cells'][0]['source'] = [content['title'] + "\n", "\n"] + [line + "\n" if not line.endswith("\n") else line for line in content['description']]
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(notebook, f, indent=1)
                
                print(f"Updated {filename}")
            else:
                print(f"Skipped {filename}: First cell is not markdown")
        except Exception as e:
            print(f"Error updating {filename}: {e}")
    else:
        print(f"File not found: {filename}")
