# Test Guide

Backend tests live in `backend/tests` and run with:

```powershell
Set-Location backend
.\.venv\Scripts\python.exe -m pytest -q
```

The frontend production check is:

```powershell
Set-Location frontend
npm run build
```