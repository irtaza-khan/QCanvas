@echo off
REM Optional: set AWS credentials for Cirq-RAG-Code-Assistant (Windows CMD).
REM Recommended on Windows: use PowerShell script instead:  scripts\set_aws_env.ps1 -CreateEnv
REM Or copy .env.example to .env in the project root and edit - the app loads .env automatically.
echo To set AWS credentials in this CMD session, run (replace with your values):
echo   set AWS_ACCESS_KEY_ID=your_access_key_id_here
echo   set AWS_SECRET_ACCESS_KEY=your_secret_access_key_here
echo   set AWS_DEFAULT_REGION=us-east-1
echo.
echo Recommended: copy .env.example to .env in the project root and edit .env.
echo The application reads .env automatically (no "set" in the file); do not commit .env.
