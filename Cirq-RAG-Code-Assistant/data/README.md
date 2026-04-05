# Data Directory

This directory contains all data files for the Cirq-RAG-Code-Assistant project.

## 📁 Structure

```
data/
├── datasets/          # Training and evaluation datasets
├── knowledge_base/    # Curated Cirq code snippets and documentation
├── models/            # Pre-trained models and embeddings
└── README.md          # This file
```

## 📊 Datasets

The `datasets/` directory contains:

- **Training datasets** for fine-tuning language models
- **Evaluation datasets** for testing system performance
- **Benchmark datasets** for comparison with other systems
- **Synthetic data** for data augmentation and testing

## 🧠 Knowledge Base

The `knowledge_base/` directory contains:

- **Curated Cirq code snippets** with high-quality implementations
- **Natural language descriptions** for each code example
- **Educational explanations** and step-by-step breakdowns
- **Algorithm templates** for common quantum algorithms
- **Best practices and patterns** for quantum programming

## 🤖 Models

The `models/` directory contains:

- **Pre-trained embedding models** for semantic search
- **Fine-tuned language models** for code generation
- **Vector database indices** for efficient retrieval
- **Model checkpoints and weights** for reproducibility

## ⚠️ Important Notes

### Usage Guidelines

- These directories are **automatically created and managed** by the system
- **Do not manually modify** files unless you understand the data format
- The system expects specific file structures and naming conventions

### Git Configuration

- All files in this directory are **ignored by Git** to prevent large files from being committed
- Use **Git LFS** for large model files if needed
- Consider using cloud storage for very large datasets

### Storage Considerations

- **Monitor disk space** as models and datasets can be large
- **Regular cleanup** of temporary files is recommended
- **Backup important models** before major system updates
