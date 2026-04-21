# QCanvas Machine Setup Guide (Including Cirq RAG AI)

This guide walks through setting up the entire QCanvas project on a new laptop or developer machine from scratch. This includes the Next.js frontend, Django backend, PostgreSQL database, and the Dockerized AWS Bedrock-backed Cirq RAG Assistant.

## Prerequisites

- **Python 3.9+** installed.
- **Node.js 18+** installed.
- **Docker Desktop** installed and running.
- **Git** installed.
- **AWS Credentials** with Bedrock permissions (for the Cirq AI).

---

## Step 1: Clone the Repository

Clone the project to your local machine and navigate into the root directory:

```bash
git clone https://github.com/your-username/qcanvas.git
cd qcanvas
```

---

## Step 2: Configure Environment Variables

You need to provide your AWS keys for the Cirq RAG AI to generate multi-modal embeddings via AWS Bedrock.

1. Navigate to the `Cirq-RAG-Code-Assistant` directory:
   ```bash
   cd Cirq-RAG-Code-Assistant
   ```
2. Create a `.env` file from the template (or copy your existing one):
   ```bash
   cp .env.example .env
   ```
3. Open `.env` and fill in your AWS credentials:
   ```ini
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_DEFAULT_REGION=us-east-1
   # Ensure your Bedrock ARNs are also correctly set
   ```
4. Return to the root directory:
   ```bash
   cd ..
   ```

---

## Step 3: Fast-Track Build & Start with Docker

You don't need to manually configure Python virtual environments! Since the backend and the new, optimized Cirq Agent are both containerized, a single Docker command will build the slim images and launch the entire infrastructure (Postgres, Redis, SonarQube, Django backend, and the Cirq AI).

Run this single command from your root directory:

```bash
docker-compose up -d --build
```

*(This command ensures both your backend and AI agent are freshly built to match the code, avoiding the heavy 11GB default AI image by utilizing our CPU optimizations!)*

Verify everything is running successfully:

```bash
docker-compose ps
```

---

## Step 4: Run Database Migrations

Even though the backend is running in Docker, you still need to format your Postgres database tables. You can execute this command directly inside the running backend container:

```bash
# Migrate the postgres database layout
docker-compose exec backend python -m alembic upgrade head

# Verify the database
docker-compose exec backend python backend/verify_database.py

# (Optional) Create an Admin user
docker-compose exec backend python backend/create_user.py
```

*The backend API is now fully available at `http://localhost:8000`.*

---

## Step 6: Start the Frontend

Open a **new terminal tab/window**, leave your backend running, and navigate to the `frontend` folder:

```bash
cd frontend

# Install node dependencies
npm install

# Start the Next.js development server
npm run dev
```

---

## 🎉 Success!

You have completely deployed the architecture locally!

- **QCanvas App**: [http://localhost:3000](http://localhost:3000)
- **Django Backend**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Cirq RAG AI Agent**: Running in Docker on `localhost:8001`
