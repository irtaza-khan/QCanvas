# FastQSim SDK Test Project

A beautiful quantum circuit IDE and playground built with the FastQSim Python SDK.

## Features
- **Monaco Editor**: Full-featured code editor with OpenQASM 3.0 support.
- **Multi-Backend**: Switch between Qiskit, Cirq, and PennyLane seamlessly.
- **Real-time Results**: Live status updates and histogram visualization.
- **Job History**: Keep track of all your past simulations.
- **Premium Design**: Dark mode, glassmorphism, and smooth animations.

## Quick Start

### 1. Prerequisites
- Python 3.8+
- FastQubit Account (User ID and API Token)

### 2. Installation
```bash
# Clone the repository
cd "QSim Link Test Final"

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the `backend/` directory:
```env
FASTQUBIT_USER_ID=your_id
FASTQUBIT_SESSION_TOKEN=your_token
FASTQUBIT_ENDPOINT=https://fastqubit.dev/api
```

### 4. Run
```bash
python app.py
```
Open `http://localhost:5000` in your browser.

## Documentation
- [SDK Overview](SDK_OVERVIEW.md)
- [API Cookbook](API_COOKBOOK.md)
