# Development

NEXUS is a local prototype that uses synthetic data only.

## Local run

Start the API from `backend`:

```powershell
..\.backend\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

The reliable Windows form is:

```powershell
Set-Location backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Start the frontend in a second terminal:

```powershell
Set-Location frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

Seed synthetic data before the first run:

```powershell
Set-Location backend
.\.venv\Scripts\python.exe ..\scripts\generate_data.py
.\.venv\Scripts\python.exe ..\scripts\seed_database.py
```

## Checks

```powershell
Set-Location backend
.\.venv\Scripts\python.exe -m pytest -q
Set-Location ..\frontend
npm run build
```

## Container run

From the repository root:

```powershell
docker compose up --build
```

The container serves the API on port `8000`. The Vite development server is still
the supported frontend workflow for local UI development.

For a remote host, build with the public API URL so the browser bundle does not
point at the developer machine:

```powershell
docker build --build-arg VITE_API_URL=https://your-api.example.com -t nexus:latest .
```