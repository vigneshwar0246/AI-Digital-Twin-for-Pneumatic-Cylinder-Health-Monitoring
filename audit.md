# Backend Audit and Next Steps

**Project:** AI Digital Twin for Pneumatic Cylinder Health Monitoring  
**Audit date:** 2026-09-08  
**Branch:** `prototype-api`  
**Audited commit:** `ce7c70f`  
**Backend version:** `2.1.0`  
**Overall status:** Prototype backend complete and ready for frontend integration

## Executive summary

The V2.1 backend is operational. It provides a versioned FastAPI interface for stateful fault prediction, experimental health estimation, transparent RUL estimation, advisory control recommendations, simulation management, WebSocket streaming, and SQLite prediction history.

The classifier and health-model artifacts are present. The application was tested using the repaired project virtual environment with Python 3.13.9, Uvicorn 0.52.4, and scikit-learn 1.9.0. The API started successfully, `/docs` returned HTTP 200, and classifier, health-model, and database health checks all reported available.

No frontend work is included in this branch. The next useful activity is to keep the backend running and connect the Astra frontend to the documented API contract.

## Verified repository state

| Check | Result |
|---|---|
| Active branch | `prototype-api` |
| Current commit | `ce7c70f` |
| Working tree at audit start | Clean |
| V2.1 classifier artifact | Present |
| V2.1 health artifact | Present locally; intentionally ignored by Git |
| Classifier metrics | Present and preserved |
| Health metrics | Present and tracked |
| Dataset V2.1 | Present and unchanged |
| Frontend API contract | Present |
| Uvicorn in `.venv` | Installed, version 0.52.4 |

The old broken virtual environment was preserved as `.venv-broken-20260908`. It is not needed for normal operation and may be removed manually after the repaired `.venv` has been used successfully for a while.

## Implemented architecture

1. FastAPI loads application services and model artifacts once through its lifespan handler.
2. Raw readings enter an independent bounded temporal buffer identified by `session_id`.
3. Online feature engineering reuses the exact offline V2.1 formulas and produces the classifier's ordered 23-feature vector.
4. The classifier returns a fault class, confidence, and probabilities for all five classes.
5. The separate regressor returns an experimental health estimate constrained to 0–100.
6. The RUL component uses recent predicted-health trends and returns `null` when a valid declining trend is unavailable.
7. The policy engine creates deterministic `advisory_simulation` recommendations and never sends hardware commands.
8. Predictions are persisted in local SQLite storage.
9. The V2.1 simulator uses the same prediction pipeline and exposes true simulated state separately from AI estimates.

## Available interfaces

The base address for local development is `http://127.0.0.1:8000`.

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Application identity and status |
| GET | `/docs` | Interactive OpenAPI documentation |
| GET | `/api/v1/health` | Classifier, health model, database, and simulator availability |
| GET | `/api/v1/model/info` | Features, faults, saved metrics, and limitations |
| POST | `/api/v1/predict` | Stateful prediction for one reading |
| POST | `/api/v1/predict/batch` | Ordered batch prediction |
| GET | `/api/v1/history` | Recent prediction history with filtering |
| POST | `/api/v1/simulations` | Create and start a simulation session |
| GET | `/api/v1/simulations/{session_id}` | Read current simulation state |
| POST | `/api/v1/simulations/{session_id}/step` | Advance and predict one step |
| POST | `/api/v1/simulations/{session_id}/stop` | Stop a simulation |
| DELETE | `/api/v1/simulations/{session_id}` | Reset and remove a simulation |
| WS | `/api/v1/ws/simulations/{session_id}` | Stream simulated state and predictions |

The exact request types, response types, enum values, nullability rules, errors, and WebSocket messages are documented in [`docs/frontend_api_contract.md`](docs/frontend_api_contract.md).

## Model audit

### Fault classifier

- Dataset: synthetic V2.1, 20,000 rows from 50 complete independent runs
- Supported classes: Healthy, Air Leakage, Pressure Drop, Seal Wear, and Valve Sticking
- Inputs: seven raw sensors plus sixteen approved temporal/derived features
- Excluded from classification: Time, CycleCount, Health, Fault, RunID, Step, PlannedFault, Severity, and simulator metadata
- Unseen-run accuracy: 95.775%
- Balanced accuracy: 95.4452%
- Macro F1: 0.9542
- Five-fold unseen-run accuracy: 95.57% ± 1.44%

These are synthetic-data results and must not be represented as physical-equipment performance.

### Health estimator

- Status: experimental
- Split: complete RunID groups
- MAE: 3.6775 health points
- RMSE: 5.3895
- R²: 0.3576
- Leakage controls: Health, fault labels, time/cycle fields, RunID, Step, and simulator metadata are excluded

The modest R² means the estimate is useful as a prototype signal, not as a validated wear measurement.

### Remaining useful life

RUL is a transparent recent-health linear trend estimate, not a trained run-to-failure model. It correctly returns `null` for insufficient history, unavailable health, or a non-degrading trend. Physical run-to-failure data is required before reporting validated remaining life.

## Test and validation evidence

- `python -m pytest -q`: **14 passed**
- Modified Python file compilation: passed
- FastAPI TestClient and WebSocket smoke tests: passed
- Live Uvicorn HTTP smoke test: passed
- `/docs`: HTTP 200
- `/api/v1/health`: classifier, health model, and database available
- Dataset V2.1 validator: all checks passed
- `git diff --check`: passed before the completion commit

The test suite covers API identity and health, model information, valid and invalid predictions, ordered batches, persistence filtering, feature parity, feature ordering, leakage exclusions, buffer isolation/reset, health bounds, insufficient-history RUL, all control policies, simulation lifecycle, deterministic simulation, WebSocket behavior, and missing artifacts.

## What to do now

### 1. Start the backend

Open PowerShell in the repository:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
python -m uvicorn backend.api.main:app --reload
```

Keep this terminal open. Confirm the following pages:

- API documentation: `http://127.0.0.1:8000/docs`
- Service health: `http://127.0.0.1:8000/api/v1/health`
- Model information: `http://127.0.0.1:8000/api/v1/model/info`

### 2. Exercise a simulated session

Use `/docs` or a second PowerShell window:

```powershell
$body = @{
    session_id = "astra-demo"
    planned_fault = "Seal Wear"
    seed = 42
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/api/v1/simulations" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/api/v1/simulations/astra-demo/step" `
    -Method Post
```

Advance several steps and inspect `true_simulated_state`, `prediction`, `warmup`, `health`, `rul`, and `control` separately.

### 3. Build the frontend against the frozen contract

Give Astra [`docs/frontend_api_contract.md`](docs/frontend_api_contract.md) as the primary integration specification. The frontend should:

- Use a configurable backend base URL, defaulting locally to `http://127.0.0.1:8000`.
- Display all five class probabilities instead of only the winning label.
- Show the temporal warm-up state clearly.
- Treat nullable RUL as “not enough evidence,” never as zero.
- Mark health as experimental.
- Display every control recommendation as advisory simulation output.
- Show true simulator state and AI estimates as separate concepts.
- Open the WebSocket only after creating its corresponding simulation session.
- Handle 404, 409, 422, and 503 structured errors.

If Astra runs on a different local origin, add it to `CORS_ORIGINS` before starting the backend. Example:

```powershell
$env:CORS_ORIGINS = "http://localhost:3000,http://localhost:5173,http://localhost:4321"
python -m uvicorn backend.api.main:app --reload
```

### 4. Re-run verification before a demo

```powershell
python -m pytest -q
python -m backend.simulator.validate_dataset_v2_1
git status
```

Do not regenerate the classifier unless its artifact is absent. Regenerate the ignored health artifact after cloning or changing compatible scikit-learn environments with:

```powershell
python -m backend.ai.train_health_v2_1
```

## Known limitations and risks

1. All training and evaluation data is synthetic.
2. The health estimator has limited explanatory performance and is explicitly experimental.
3. RUL is not validated against physical failure events.
4. SQLite is appropriate for a single-node prototype, not a high-volume distributed deployment.
5. In-memory feature and simulation sessions do not survive an API restart.
6. The prototype has no authentication or authorization and should not be exposed directly to an untrusted network.
7. Sensor boundaries are broad API-validation limits, not calibrated equipment safety limits.
8. There is no connection to PLCs, valves, actuators, or other physical control hardware.

## Required work before physical deployment

- Define and validate real sensor units, calibration, sampling rates, timestamp semantics, and missing-data behavior.
- Collect equipment-separated labeled operating data and real run-to-failure histories.
- Retrain and validate models against physical measurements, including uncertainty and drift monitoring.
- Add authenticated ingestion, transport security, audit logging, rate limits, and operational monitoring.
- Define restart/session recovery behavior and select production persistence if necessary.
- Conduct formal hazard analysis and fail-safe validation.
- Keep recommendations human-reviewed until qualified industrial safety systems authorize any actuation.

## Audit conclusion

The backend definition of done is satisfied for a local synthetic-data prototype. The immediate next milestone is frontend integration and an end-to-end demonstration using the simulator. The project is not ready for claims of real-world predictive accuracy or for direct industrial control.
