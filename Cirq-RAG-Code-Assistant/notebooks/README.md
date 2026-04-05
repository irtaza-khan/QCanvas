# Notebooks Directory

This directory contains Jupyter notebooks for different components and workflows of the Cirq-RAG-Code-Assistant project.

## Notebook Structure

The notebooks are organized to follow the development and testing workflow:

### Data Processing
- **01_preprocessing.ipynb**: Data preprocessing and knowledge base preparation
- **02_embeddings.ipynb**: Embedding generation and testing
- **03_vector_store.ipynb**: Vector store operations and testing

### Core System
- **04_rag_system.ipynb**: Complete RAG system workflow testing
- **05_designer_agent.ipynb**: Designer Agent testing and experimentation
- **06_optimizer_agent.ipynb**: Optimizer Agent testing
- **07_validator_agent.ipynb**: Validator Agent testing
- **08_educational_agent.ipynb**: Educational Agent testing
- **09_orchestration.ipynb**: Multi-agent orchestration testing

### Evaluation & Analysis
- **10_evaluation.ipynb**: System evaluation and benchmarking
- **11_training.ipynb**: Model training and fine-tuning (if applicable)
- **12_visualization.ipynb**: Visualization of circuits, metrics, and results

### Testing
- **13_api_testing.ipynb**: REST API endpoint testing
- **14_cli_testing.ipynb**: Command-line interface testing

## Usage

Each notebook is designed to import functions and classes from the `src` directory. The notebooks should remain clean and focused on calling the implemented functionality rather than containing implementation code.

### Example Usage

```python
# In a notebook cell
from src.rag.retriever import Retriever
from src.agents.designer import DesignerAgent

# Use the imported classes
retriever = Retriever()
designer = DesignerAgent()
```

## Development Workflow

1. **Implement code** in the `src` directory
2. **Test and experiment** in the corresponding notebook
3. **Iterate** on implementation based on notebook results
4. **Keep notebooks clean** - they should primarily call functions from `src`

## Notes

- Notebooks are currently empty templates with markdown headers
- Add code cells as you implement and test each component
- Keep implementation code in `src`, use notebooks for experimentation and testing
- Notebooks can be used for visualization, analysis, and demonstration

