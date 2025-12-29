# Windows Setup Guide for QCanvas

This guide provides step-by-step instructions for setting up a fresh Windows PC to run QCanvas. Follow these steps before using the `win_runner.ps1` script.

## 1. Install Prerequisites

### 🐍 Install Python (for Backend)
The backend requires Python 3.10 or newer.

1.  Go to [python.org/downloads](https://www.python.org/downloads/).
2.  Download the latest version (e.g., 3.11 or 3.12).
3.  **Run the installer.**
4.  ⚠️ **CRITICAL STEP**: On the first screen, **CHECK the box** that says **"Add python.exe to PATH"**.
5.  Click **Install Now**.

### 📦 Install Node.js (for Frontend)
The frontend is built with Next.js/React.

1.  Go to [nodejs.org](https://nodejs.org/en/download/prebuilt-installer).
2.  Download the **LTS (Long Term Support)** version.
3.  Run the installer and accept all defaults. This automatically adds `npm` and `node` to your system.

### 🛠 Install Visual Studio Build Tools (Optional but Recommended)
Some Python packages (like `numpy` or quantum libraries) may require C++ compilers.

1.  Download **Visual Studio Build Tools** from [visualstudio.microsoft.com/visual-cpp-build-tools/](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
2.  Run the installer.
3.  Select the workload **"Desktop development with C++"**.
4.  Click **Install** (this may take some time).

*(Note: You can skip this step initially. Only come back to it if the installation fails with "Microsoft Visual C++ 14.0 or greater is required" errors.)*

### 🐙 Install Git (Optional)
Required if you need to clone the repository or manage version control.

1.  Download from [git-scm.com/download/win](https://git-scm.com/download/win).
2.  Run the installer and accept defaults.

---

## 2. Configure PowerShell Permissions

By default, Windows restricts running scripts. You need to allow local scripts to run.

1.  Open **PowerShell** as **Administrator**.
    *   Right-click the Start button -> **Terminal (Admin)** or **PowerShell (Admin)**.
2.  Copy and paste the following command and press Enter:
    ```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    ```
3.  If asked for confirmation, type `A` (Yes to All) and press Enter.

---

## 3. Verification

Close any open terminals and open a **new** PowerShell window. Run the following commands to confirm everything is ready:

```powershell
python --version
# Should show Python 3.x.x

node --version
# Should show v18.x.x or higher

npm --version
# Should show a version number
```

---

## 4. Running QCanvas

Once the above setup is complete, navigate to the project folder in PowerShell and use the provided `win_runner.ps1` script.

### First Time Installation
```powershell
.\win_runner.ps1 install
```
*This installs all Python and Node.js dependencies.*

### Start Services
```powershell
.\win_runner.ps1 start
```
*Starts Frontend and Backend in the background.*

### Stop Services
```powershell
.\win_runner.ps1 stop
```
