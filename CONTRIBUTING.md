# Contributing to NEXUS

## First-time setup

```powershell
git clone https://github.com/Aryansh077/NEXUS-Investigative-Intelligence.git
Set-Location NEXUS-Investigative-Intelligence
```

Use the branch assigned to your team area. Never commit directly to `main`.

## Branch workflow

```powershell
git switch main
git pull origin main
git switch -c feature/your-area
```

Validate before opening a pull request:

```powershell
Set-Location backend
.\.venv\Scripts\python.exe -m pytest -q
Set-Location ..\frontend
npm run build
```

Publish your branch:

```powershell
git add .
git commit -m "Describe the focused change"
git push -u origin feature/your-area
```

Open a pull request into `main`. Another team member should review it before
merge. NEXUS uses synthetic data only; never commit real investigative data.