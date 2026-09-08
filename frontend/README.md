# Pneuma / Twin Lab

Interactive React + TypeScript workbench for the existing FastAPI V2.1 backend. Built inside the original `frontend/` folder. Its existing JSX files were empty placeholders and remain preserved; `index.html` loads `src/main.tsx`.

## Run locally

From the repository root, start the backend:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000
```

In another terminal:

```powershell
cd D:\DigitalTwin-PneumaticCylinder\frontend
npm.cmd install
Copy-Item .env.example .env.local
npm.cmd run dev
```

The development server is pinned to `127.0.0.1:5173` with strict port checking. If another process owns that port, Vite reports the conflict instead of silently moving to a new origin that backend CORS does not allow.

Open http://127.0.0.1:5173. **CORS:** the backend default allows `http://localhost:5173`, so either open that hostname or configure both origins before starting the backend:

```powershell
$env:CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
.\.venv\Scripts\python.exe -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000
```

`VITE_API_BASE_URL` defaults to `http://127.0.0.1:8000`. `VITE_STROKE_LENGTH_MM=100` mirrors `backend/config/constants.py`; the API does not expose stroke configuration, so update both if it changes. Vite variables are compiled into the build; restart after editing. Never put secrets in them.

## Verify and build

```powershell
npm.cmd run typecheck
npm.cmd run lint
npm.cmd test
npm.cmd run build
npm.cmd run preview
```

With both development servers running, `node e2e/smoke.cjs` runs a real-backend browser check using installed Microsoft Edge through Playwright. It creates and deletes its own simulation and writes screenshots to ignored `test-results/`. The backend intentionally retains the generated prediction history. Unit tests use mocks and do not need a server.

Production assets are in `dist/`. Serve with SPA history fallback to `index.html`. Add the actual production origin to backend CORS. Preview uses port 4173 and needs that origin allowed too.

## Operation

Choose a planned condition and integer seed, create a session, then start the stream or advance one step. Pause disconnects telemetry; Stop permanently stops that session; Reset removes it and enables a new session. The backend starts faults at step 40 by default, so early samples can legitimately predict Healthy for a fault-planned run.

Routes: `/` Twin Lab, `/diagnostics`, `/trends`, `/history`, `/model`. History fetches up to the latest 1,000 rows and paginates/filter them locally because the backend has no offset pagination. The typed client also exposes single and batch prediction methods for later sensor adapters; the workbench uses the simulator pipeline.

The socket opens only after session creation. HTTP(S) base URLs become WS(S) URLs with the base path preserved. Reconnect uses exponential delays capped at 15 seconds and checks session existence/running status before reopening. Pause, stop, reset and application unmount close the socket. Reconnection cannot recover samples lost during a connection gap. REST errors preserve status, code, message and details. Data is capped at 1,000 chart samples. Chart pause freezes the trace only; clearing it does not delete persisted backend history.

## 3D and interpretation

The long steel tube, machined end caps and blue fittings are inspired by the supplied photograph. The exploded reference informs approximate component ordering only; its printed dimensions are not verified specifications. Configurable conceptual parts are in `src/components/Cylinder.tsx`. No proprietary CAD, external 3D model or generated reference image is required. The generic illustration's return spring is deliberately omitted from this double-acting conceptual model; verify internals against manufacturer drawings before treating geometry as an engineering specification.

Position is clamped against configured stroke and smoothly interpolated, never replaced with a local reciprocation loop. Explore Internals freezes visual rod motion, spreads components along the axis and moves the camera; reassembly reverses the spread and catches up with current telemetry. Fault overlays are illustrative associations based on predicted class/confidence, not localization of physical damage. Valve hesitation comes from backend position; airflow pulses are illustrative. Use the component index as a keyboard-accessible alternative to picking meshes.

The UI separates true simulated state, classification, experimental health, trend RUL and advisory simulation. Null RUL means **Insufficient evidence**. Models use synthetic data and are not industrially validated. No controls actuate physical hardware.

Device pixel ratio is capped at 1.5. Reduced motion disables transition animations. WebGL failure preserves instruments and component details. Fonts use Google Fonts with local system fallbacks; 3D lighting is generated locally. Desktop is the primary layout; tablet and small-screen layouts remain usable.

## Troubleshooting

- Backend offline: verify `/api/v1/health`, port 8000, configured URL and CORS. Press Retry.
- Degraded / HTTP 503: inspect backend artifact compatibility; this frontend does not train or replace models.
- HTTP 404: session may have been removed or lost after a backend restart. Reset/recreate the UI session as appropriate.
- HTTP 409: the session is stopped or the operation conflicts with lifecycle state.
- HTTP 422: inspect structured validation details and use valid seed/sensor values.
- Blank 3D: enable browser hardware acceleration / WebGL2; numerical instruments remain available.
- PowerShell blocks `npm.ps1`: use `npm.cmd` as shown above.
- External hosting requires backend authentication, transport security and deployment hardening; this is a local synthetic-data prototype.
