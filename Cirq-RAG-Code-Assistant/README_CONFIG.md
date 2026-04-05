# Configuration System

## Overview

The Cirq-RAG-Code-Assistant uses a JSON-based configuration system located in the `config/` folder in the root directory. All configuration is centralized in JSON files and can be accessed by any Python file or notebook.

## Configuration Files

All configuration files are located in the `config/` folder:

- **`config/config.json`** - Main configuration file (production/default settings)
- **`config/config.dev.json`** - Development configuration (used when `ENVIRONMENT=development`)
- **`config/config.template.json`** - Template file with placeholders for API keys
- **`config/config_loader.py`** - Configuration loader module

## Usage

### In Python Files

```python
# Option 1: Import from config folder directly
from config import get_config, get_config_loader

# Option 2: Import from src package (which imports from config folder)
from src.cirq_rag_code_assistant.config import get_config, get_config_loader

# Get configuration dictionary
config = get_config()

# Access values using dot notation
embedding_model = config.get("models.embedding.model_name")
batch_size = config.get("models.embedding.batch_size", 32)  # with default

# Get entire section
config_loader = get_config_loader()
rag_config = config_loader.get_section("rag")
```

### In Notebooks

```python
import sys
from pathlib import Path

# Add project root to path
project_root = Path("..").resolve()
sys.path.insert(0, str(project_root))

# Import from config folder
from config import get_config, get_config_loader

# Initialize config
config = get_config()
config_loader = get_config_loader()

# Use config values
model_name = config.get("models.embedding.model_name")
```

## Configuration Structure

The configuration is organized into sections:

- **`app`** - Application settings (name, version, debug, environment)
- **`api_keys`** - API keys for external services (can be overridden by environment variables)
- **`models`** - Model configurations (embedding, LLM, fine-tuning)
- **`rag`** - RAG system settings (knowledge base, vector store, retrieval)
- **`agents`** - Agent configurations (general, designer, optimizer, validator, educational)
- **`tools`** - Tool settings (compiler, simulator, analyzer)
- **`paths`** - Directory paths
- **`pytorch`** - PyTorch/CUDA settings
- **`evaluation`** - Evaluation and benchmark settings
- **`logging`** - Logging configuration

## Environment Variable Overrides

The following environment variables can override config values:

- `OPENAI_API_KEY` - OpenAI API key
- `HUGGINGFACE_API_KEY` - Hugging Face API key
- `ANTHROPIC_API_KEY` - Anthropic API key
- `ENVIRONMENT` - Environment name (development, production)
- `DEBUG` - Debug mode (true/false)
- `LOG_LEVEL` - Logging level

## Setup

1. Copy the template:
   ```bash
   cp config/config.template.json config/config.json
   ```

2. Edit `config/config.json` and add your API keys:
   ```json
   {
     "api_keys": {
       "openai_api_key": "your-key-here"
     }
   }
   ```

3. Or use environment variables:
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

## Notes

- The config loader automatically creates all necessary directories
- PyTorch/CUDA settings are automatically applied on import
- Config is loaded once and cached globally
- Use `reload_config()` to reload from file if needed

