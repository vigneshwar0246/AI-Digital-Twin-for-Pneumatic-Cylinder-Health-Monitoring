# Complete Project Audit: AI Digital Twin for a Pneumatic Cylinder

**Audit date:** 2026-09-08

**Branch/commit:** `frontend-astra` / `5cc6882`

**API version:** `2.1.0`

**Status:** Working full-stack research prototype; not ready for production or physical control

## Executive assessment

This project is a software digital twin for a pneumatic cylinder. It generates synthetic operating data, simulates five conditions, classifies faults from sensor readings, estimates an experimental health score, calculates a simple trend-based remaining useful life (RUL), stores prediction history, and shows the results in a React dashboard with an interactive 3D cylinder.

The supported V2.1 path works. During this audit, all **14 backend tests** and all **13 frontend tests** passed, and the frontend production build completed. The V2.1 dataset has **20,000 rows from 50 simulated runs**. The saved classifier reports **95.775% holdout accuracy** and **95.57% mean five-fold accuracy** on complete unseen simulation runs.

These results demonstrate consistency inside this simulator. They do not demonstrate performance on physical machinery. The simulator creates both the training data and test conditions, so real sensor behavior, environmental changes, installation differences, actual wear, and unknown faults remain untested.

The repository also contains legacy V1/V2 code and empty placeholders. MQTT, Docker deployment, Nginx, standalone anomaly detection, and the standalone RUL file are not implemented in the running V2.1 application. Current RUL logic is inside `backend/ai/services.py`.

## What it can do now

- Simulate a stateful cylinder moving between 0 and 100 mm under changing loads.
- Simulate Healthy, Air Leakage, Pressure Drop, Seal Wear, and Valve Sticking.
- Generate pressure, temperature, position, flow, speed, vibration, load, cycle count, true health, and true simulated fault.
- Accept external-looking readings through REST, with validation.
- Build 23 model inputs from seven sensors and sixteen temporal/derived features.
- Return a fault label, confidence, and probabilities for all five classes.
- Return an optional experimental health estimate from 0 to 100.
- Estimate RUL from recent declining predicted-health history.
- Produce rule-based operating and maintenance advice.
- Persist prediction history in SQLite.
- Run multiple named simulations through REST or WebSocket streaming.
- Display a 3D assembled, cutaway, and exploded cylinder.
- Display instruments, telemetry, diagnoses, advice, history, and model evidence.
- Reconnect WebSocket telemetry automatically after interruptions.

## What it cannot do now

- It is not connected to a physical cylinder, PLC, valve, actuator, ESP32, or sensor.
- It sends no commands to hardware.
- MQTT files are empty.
- `Dockerfile`, Compose, Nginx configuration, and `start.bat` are empty.
- `backend/ai/anomaly_detection.py` is empty; there is no separate anomaly detector in the API.
- `backend/ai/rul_prediction.py` is empty; RUL is currently a linear trend helper elsewhere.
- There is no cloud service, time-series database, Grafana integration, mobile app, vision inspection, or edge inference.
- There are no accounts, authentication, authorization, tenant isolation, or maintenance-system integration.

## Architecture and data flow

```text
Built-in simulator or submitted sensor reading
                    |
                    v
       FastAPI validation/orchestration
                    |
                    v
     Per-session bounded feature buffer
                    |
                    v
      7 raw + 16 engineered features
                    |
          +---------+---------+
          |                   |
          v                   v
 Random Forest fault    Extra Trees health
 classifier             regressor (optional)
          |                   |
          +---------+---------+
                    v
        RUL trend + advice policy
                    |
          +---------+---------+
          |                   |
          v                   v
   SQLite history      REST/WebSocket response
                              |
                              v
                    React/Three.js dashboard
```

At startup FastAPI initializes SQLite and loads the classifier. Startup fails if the classifier is absent or uses a different feature order. The health model is optional; without it, health and RUL are unavailable.

For every reading, Pydantic validates the values. The backend appends the seven sensors to the buffer for that `session_id`, calculates the exact 23-feature order used in training, scales it, and asks the classifier for probabilities. The optional health model estimates health. The RUL component updates its session history, the policy creates advisory output, and the complete prediction is stored in SQLite.

For simulations, the backend advances the known physical state first and sends its readings through the same prediction pipeline. The response deliberately keeps `true_simulated_state` separate from `prediction`; this is essential for honest demonstrations.

## Simulator behavior

The supported simulator is `PneumaticCylinderV21`.

- Stroke: 100 mm, in 10 mm steps.
- Direction reverses at 100 mm; a cycle completes after returning to 0 mm.
- Every run has five randomized load targets.
- The target changes every 80 steps and actual load approaches it gradually with noise.
- Fault severity follows a smooth S-curve after `fault_start`.
- Severity below 0.15 remains labelled Healthy because it is treated as incipient.
- Valve-sticking events last 3–8 steps and can pause physical position movement.

| Condition | Simulated effect |
|---|---|
| Healthy | Very small random health loss |
| Air Leakage | Lower pressure, higher flow, reduced speed, mild heat and vibration |
| Pressure Drop | Strong pressure and flow loss, reduced speed, mild heat and vibration |
| Seal Wear | Gradual heat and vibration rise, speed loss, nearly normal pressure/flow |
| Valve Sticking | Moderate persistent changes plus intermittent stalls, low flow and speed, vibration, and position dwell |

Health degrades at a fault-specific random rate. These are useful educational approximations, not a calibrated thermodynamic or mechanical model.

### V2.1 dataset

The generator creates 50 runs × 400 rows: 10 runs for each planned condition. Faulty conditions receive balanced maximum severities of 0.40, 0.55, 0.70, 0.85, and 1.00. Seed 84 makes generation reproducible.

The main CSV contains observable readings and labels. A separate metadata CSV contains RunID, step, planned fault, severity, fault timing, direction, load phase, and valve events. The model preparation joins them for grouping but excludes metadata from features.

## Machine-learning system

### Inputs and validation

| Input | API range | UI unit |
|---|---:|---|
| Pressure | 0–12 | bar |
| Temperature | -20–120 | °C |
| Position | 0–100 | mm |
| Flow | 0–30 | L/min |
| Speed | 0–250 | mm/s |
| Vibration | 0–15 | mm/s |
| Load | 0–100 | kg |
| Cycle count | optional integer ≥ 0 | cycles |

These are broad software-validation limits, not calibrated safe operating limits.

### Feature engineering

The models use the seven raw sensors plus:

- pressure, speed, temperature, and vibration residuals adjusted for load;
- deviation from nominal flow 10;
- absolute pressure, flow, speed, and vibration changes;
- ten-sample rolling standard deviations for those four signals;
- ten-step temperature trend;
- position dwell and ten-sample dwell rate.

Time, cycle count, health, fault, RunID, step, planned fault, severity, and simulator metadata are excluded. This avoids direct target and run-identity leakage.

The first nine readings are marked `warmup=true`. Predictions still exist, but rolling features do not yet contain a full ten-sample history.

### Fault classifier

The classifier is a 300-tree Random Forest with maximum depth 14, minimum leaf size 3, square-root feature selection, balanced-subsample weighting, and seed 42. Evaluation holds out complete runs instead of randomly mixing rows from the same run.

| Metric | V2.1 result |
|---|---:|
| Holdout accuracy | 95.775% |
| Holdout balanced accuracy | 95.445% |
| Holdout macro F1 | 0.9542 |
| Five-fold accuracy | 95.57% ± 1.44% |
| Five-fold balanced accuracy | 94.90% ± 2.00% |
| Five-fold macro F1 | 0.9503 ± 0.0182 |

Holdout recall ranges from 92.95% for Valve Sticking to 97.67% for Pressure Drop. The most important saved features are temperature residual, pressure residual, vibration variation, raw temperature, vibration residual, and flow signals.

Saved V2 five-fold accuracy was only 63.83%, with extremely weak Seal Wear recall. V2.1 improves the simulator and temporal features, but it still evaluates recognition of simulator-created patterns.

### Health estimator

The health model is a 250-tree Extra Trees regressor. It is trained against simulator-generated health and clipped to 0–100.

| Metric | Result |
|---|---:|
| MAE | 3.677 health points |
| RMSE | 5.389 |
| R² | 0.3576 |

The modest R² means health is only a prototype signal. It is not a measured wear quantity or validated asset-health index. The UI and API correctly label it experimental.

### RUL calculation

RUL is not a trained failure-time model. It fits a line through up to 30 recent predicted-health points and estimates when health will cross 30.

It returns no number if health is unavailable, fewer than five observations exist, cycle/step values do not change, or the trend is flat/improving. Numeric output is capped at 10,000 cycles. Reliability is low below ten points and medium thereafter. There is no high-reliability state, uncertainty interval, survival model, or real failure validation.

### Advisory policy

| Prediction | Mode | Priority | Speed | Load |
|---|---|---|---:|---:|
| Healthy | standard | routine | 100% | 100% |
| Air Leakage | efficiency limited | planned | 90% | 90% |
| Pressure Drop | load limited | urgent | 80% | 75% |
| Seal Wear | reduced stress | planned | 75% | 75% |
| Valve Sticking | restricted | urgent | 65% | 70% |

Confidence below 60% changes the advice to observation and human review. Shutdown review is recommended if estimated health is ≤30, pressure >10 bar, temperature >90 °C, vibration >10 mm/s, or estimated RUL is zero. These are hard-coded research rules and are not a certified safety function.

## API reference

Local server: `http://127.0.0.1:8000`

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Identity, version, status |
| GET | `/docs` | Swagger UI |
| GET | `/openapi.json` | OpenAPI schema |
| GET | `/api/v1/health` | Model/database availability |
| GET | `/api/v1/model/info` | Features, classes, metrics, limitations |
| POST | `/api/v1/predict` | Stateful prediction for one reading |
| POST | `/api/v1/predict/batch` | Ordered prediction for 1–1,000 readings |
| GET | `/api/v1/history` | Recent history, optional session filter |
| POST | `/api/v1/simulations` | Create/start a simulation |
| GET | `/api/v1/simulations/{id}` | Current state |
| POST | `/api/v1/simulations/{id}/step` | Advance and predict once |
| POST | `/api/v1/simulations/{id}/stop` | Stop |
| DELETE | `/api/v1/simulations/{id}` | Remove simulation and temporal state |
| WS | `/api/v1/ws/simulations/{id}` | Advance and stream continuously |

Session IDs are 1–100 characters and accept letters, numbers, `_`, `.`, `:`, and `-`. REST errors use structured 404, 409, 422, and 503 responses. Unexpected errors still return the framework's normal 500 response. Exact payloads are documented in `docs/frontend_api_contract.md`.

## Storage and state

SQLite defaults to `data/predictions.db`. A row stores timestamp, session, raw sensors, prediction, confidence, all probabilities, health, numeric RUL when available, warm-up state, and advisory output.

Prediction history survives an API restart. Simulations, feature buffers, RUL histories, and streams are only in process memory and disappear on restart. Deleting a simulation does not delete historical database rows.

This is suitable for a local single-process demo. It does not support shared state across workers, database migrations, high-volume writes, retention, archival, or time-series analysis.

## Frontend

The active frontend uses React 19, TypeScript, Vite, Zustand, React Router, Recharts, Three.js, React Three Fiber, Drei, GSAP, and Lucide.

- **Twin Lab:** 3D cylinder, instruments, diagnosis, controls, telemetry.
- **Diagnostics:** probabilities, health/RUL, advice, confidence history.
- **Trends:** selectable sensor chart and 30/60/300/1,000 sample windows.
- **History:** newest 1,000 records, session query, client-side fault filtering and pagination.
- **Model:** saved metrics, supported conditions, features, and limitations.

The UI creates unique session IDs and supports create, start, pause, step, stop, and reset. It stores up to 1,000 samples in memory, validates incoming WebSocket messages, and reconnects with exponential backoff up to 15 seconds. `VITE_API_BASE_URL` configures the backend and defaults to `http://127.0.0.1:8000`; HTTPS correctly maps to secure `wss://`.

The build succeeds but warns about large chunks: roughly 638 KB for the main bundle and 1,043 KB for the lazy cylinder bundle before gzip. The repository also contains legacy `.jsx` pages and components. The active entry is `main.tsx` → `App.tsx`; old JSX code adds confusion and should be archived or removed.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_PATH` | `data/predictions.db` | SQLite file |
| `CLASSIFIER_PATH` | `models/fault_classifier_v2_1.joblib` | classifier artifact |
| `HEALTH_MODEL_PATH` | `models/health_estimator_v2_1.joblib` | optional health artifact |
| `CORS_ORIGINS` | localhost 3000 and 5173 | allowed browser origins |
| `FEATURE_BUFFER_SIZE` | 100 | readings per feature session |
| `CRITICAL_HEALTH` | 30 | RUL/shutdown threshold |
| `MAX_RUL_CYCLES` | 10000 | RUL cap |
| `WEBSOCKET_INTERVAL` | 1.0 | seconds between streamed steps |

Values are parsed during import/startup. Invalid values can prevent startup; feature buffer size must be at least 11.

## Setup and operation

### Backend

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn backend.api.main:app --reload
```

Open `http://127.0.0.1:8000/docs` and `http://127.0.0.1:8000/api/v1/health`.

### Frontend

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Open `http://127.0.0.1:5173`. `npm.cmd` avoids the Windows execution-policy error that may block `npm.ps1`.

### Training

```powershell
python -m backend.ai.train_v2_1
python -m backend.ai.train_health_v2_1
```

Retrain only when the dataset, features, model code, or supported scikit-learn environment changes. The classifier artifact is about 22 MB; the health artifact is about 247 MB.

## Verification evidence

| Check performed | Result |
|---|---|
| `python -m pytest -q` | 14 passed |
| `npm.cmd test` | 13 passed |
| `npm.cmd run build` | passed, with bundle-size warning |
| V2.1 main CSV | 20,000 rows |
| V2.1 metadata CSV | 20,000 rows |
| Classifier and health artifacts | present |

Tests cover API validation, prediction, batch ordering, history, feature parity and ordering, leakage exclusions, isolated buffers, model compatibility, health bounds, null RUL, all advice policies, deterministic and isolated simulations, lifecycle operations, WebSocket output, frontend offline/retry behavior, session creation, bounded traces, scientific labels, structured errors, URL conversion, and reconnect handling.

An end-to-end Playwright script exists for real backend streaming, 3D rendering, exploded/isolate/reassemble behavior, routes, responsive layouts, and offline behavior. It was not run in this audit because it requires both servers and an installed Edge/Playwright browser.

## Problems and risks

### Critical before physical or public use

1. **Synthetic-only evidence:** accuracy cannot be transferred to physical machines.
2. **No safety qualification:** rules have no hazard analysis, redundancy, fail-safe proof, or certification.
3. **No authentication/authorization:** any network client can submit data, create sessions, or read history.
4. **No TLS deployment:** defaults are HTTP/WS and Nginx configuration is empty.
5. **No physical ingestion contract:** timing, calibration, device identity, missing values, duplicates, ordering, and stale readings are not handled.

### High-priority engineering issues

1. **Model/runtime version mismatch:** artifacts were produced with scikit-learn 1.9.0, but this audit loaded them with 1.7.2. Tests passed, but 31 warnings say cross-version unpickling may cause invalid results. Pin the environment and retrain or load with the matching version.
2. **Empty advertised features:** MQTT, deployment, anomaly, standalone RUL, and startup files are zero bytes.
3. **Volatile state:** API restarts erase all active sessions and cannot support multiple workers consistently.
4. **Unbounded sessions:** simulations, buffers, and RUL histories have no expiry or global limit, allowing memory growth through unique IDs.
5. **Silent replacement:** creating an existing simulation ID overwrites the prior session rather than returning a conflict.
6. **Incomplete concurrency protection:** simulation advancement has a lock, while feature/RUL buffers do not. Concurrent REST and WebSocket predictions can race.
7. **Large health artifact:** 247 MB increases packaging, startup, and memory costs; omitting it removes health and RUL.
8. **No schema migration/retention:** SQLite setup is embedded in startup and history has no purge, archival, or migration tooling.

### Scientific/model limitations

1. The model must choose one of five known classes; there is no unknown or out-of-distribution result.
2. Class probabilities are not shown to be calibrated.
3. Warm-up predictions are returned without confidence adjustment.
4. Health learns a hidden simulator target and has R² of only 0.3576.
5. RUL assumes a recent linear decline will continue and compounds health-model error.
6. Health and RUL have no uncertainty intervals.
7. There is no input drift, model drift, model registry, signature, or outcome monitoring.
8. No tests cover sensor dropout, stuck sensors, jitter, reordering, calibration drift, new environments, or other cylinder designs.
9. Simulator distributions may make faults easier to distinguish than real faults.

### Backend/API limitations

1. `/health` says overall `ok` when the classifier exists even if the database fails or health is unavailable.
2. `/model/info` reads metric files on each request and can return an unstructured 500 if one is missing/malformed.
3. WebSocket accepts before checking session existence and silently catches missing/stopped session errors.
4. There are no rate limits, quotas, connection caps, or request IDs.
5. External readings cannot include their measurement timestamp.
6. Batch writes are one row at a time and are not atomic.
7. Logs and operational metrics are minimal; no tracing or audit-event system exists.
8. Joblib uses pickle semantics, so model files must come only from trusted sources.

### Frontend/repository limitations

1. Large bundles can delay loading on slow devices and networks.
2. Reloading the browser loses active UI state.
3. History filters only the newest 1,000 retrieved rows and is not true database pagination.
4. The primary UI drives the simulator rather than real sensor ingestion.
5. Legacy JSX and older V1/V2 code increase ambiguity and maintenance cost.
6. Unit tests mock the 3D scene; full visual checks require the separate end-to-end run.
7. Accessibility has not received a formal WCAG audit.
8. README instructions and claims are outdated, include placeholder text, and contain encoding corruption.
9. Dependency ranges are broad rather than reproducibly locked.
10. No CI workflow, explicit license file, changelog, contribution guide, or production runbook is visible.

## Recommended roadmap

### Priority 0 — reproducible prototype

1. Pin Python, scikit-learn, and JavaScript dependencies; document supported runtime versions.
2. Resolve the model/runtime mismatch by matching 1.9.0 or retraining on the chosen pinned version.
3. Correct the README and remove claims for empty modules.
4. Implement or remove empty MQTT, Docker, Nginx, anomaly, RUL, and startup placeholders.
5. Add CI for backend tests, frontend tests, lint/typecheck, build, and dataset validation.
6. Archive or clearly separate V1/V2 and legacy JSX code.

### Priority 1 — hardened software demo

1. Add authentication, authorization, TLS, rate limiting, request IDs, structured logs, and security headers.
2. Add session ownership, duplicate-ID conflicts, expiry, cleanup, limits, and concurrency-safe ordering.
3. Add database migrations, retention, backup guidance, and server-side pagination/filtering.
4. Report classifier, health, database, and simulator readiness separately.
5. Return meaningful WebSocket close codes and errors.
6. Split frontend bundles further and complete accessibility/browser audits.

### Priority 2 — engineering validation

1. Define the exact cylinder, valves, sensors, sample rate, units, tolerances, and environment.
2. Version a physical-data contract with timestamps, device/sequence IDs, and quality flags.
3. Collect multiple physical assets across loads, installations, and fault severities.
4. Split training/test data by physical asset and time.
5. Add unknown-condition detection, calibration, uncertainty, and drift monitoring.
6. Define health from inspections or measurable degradation.
7. Collect run-to-failure/censored data and replace simple RUL with a validated degradation or survival model.
8. Compare ML against thresholds and physics-based baselines.

### Priority 3 — safe equipment connection

1. Add authenticated, buffered, replay-safe MQTT or OPC UA ingestion.
2. Keep the first hardware integration read-only.
3. Test stale data, communication loss, restarts, invalid sensors, and clocks.
4. Conduct FMEA/hazard analysis and define safe states outside the web app.
5. Keep recommendations human-reviewed until the complete system is independently validated.
6. If actuation is added, use a qualified PLC/safety system with hard interlocks; the ML API must not be the safety controller.

## Demonstration guide

1. Start backend and frontend and confirm `Connected` and model V2.1.
2. Create a Healthy session with seed 42 and start streaming.
3. Observe motion, sensors, warm-up, probabilities, health, and initially unavailable RUL.
4. Reset and repeat for each fault.
5. Compare true simulated condition with AI prediction as separate values.
6. Use Diagnostics for probabilities/advice, Trends for traces, History for persistence, and Model for evidence.
7. Stop and reset the session.
8. State clearly that this demonstrates a software pipeline against synthetic scenarios, not real-world predictive accuracy.

## Final conclusion

This is a credible educational and research prototype with a working path from simulation through temporal feature engineering, inference, persistence, streaming, and visualization. Its strongest choices are complete-run evaluation, session-separated features, clear warm-up state, separation of simulated truth from AI estimates, and explicit advisory-only output.

It is not yet an operational industrial digital twin because it is not synchronized with a physical asset and lacks real-data validation, production security, durable distributed state, and safety qualification. The reported accuracy shows that the classifier learned the V2.1 simulator well. The next sound milestone is reproducible packaging and repository cleanup, followed by read-only physical data collection and asset-separated validation.
