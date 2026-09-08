# Frontend API Contract (V2.1)

Base URL: `http://127.0.0.1:8000`. OpenAPI: `/docs`. JSON fields use `snake_case`. Configure browser origins with the comma-separated `CORS_ORIGINS` environment variable (defaults: `http://localhost:3000,http://localhost:5173`).

## Types

```ts
type Fault = "Healthy" | "Air Leakage" | "Pressure Drop" | "Seal Wear" | "Valve Sticking";
type RulStatus = "estimated" | "insufficient_history" | "non_degrading_trend" | "health_unavailable";
type SensorReading = {
  pressure: number; temperature: number; position: number; flow: number;
  speed: number; vibration: number; load: number; cycle_count?: number | null;
};
type RulEstimate = {
  estimated_remaining_cycles: number | null; status: RulStatus;
  method: "recent_health_linear_trend"; reliability: "none" | "low" | "medium";
  critical_health_threshold: number; explanation: string;
};
type ControlAdvice = {
  output_type: "advisory_simulation"; operating_mode: string; maintenance_priority: string;
  recommended_speed_limit_percent: number; recommended_load_limit_percent: number;
  inspection_action: string; shutdown_recommended: boolean; reason: string;
};
type Prediction = {
  history_id: number; timestamp: string; session_id: string; reading: SensorReading;
  fault: Fault; confidence: number; probabilities: Record<Fault, number>;
  health: number | null; health_status: "experimental" | "unavailable";
  rul: RulEstimate; control: ControlAdvice; warmup: boolean; buffer_samples: number;
};
```

Sensor validation ranges are: pressure 0–12 bar, temperature −20–120 °C, position 0–100 mm, flow 0–30 L/min, speed 0–250 mm/s, vibration 0–15 mm/s, load 0–100 kg, and cycle count ≥ 0. Session IDs are 1–100 characters using letters, digits, `_ . : -`. Unknown fields are rejected.

## REST

`GET /` returns `{"application": string, "version": string, "status": "ok", "documentation_url": "/docs"}`.

`GET /api/v1/health` reports `status`, `classifier_available`, `health_model_available`, `database_available`, and `simulator_status`.

`GET /api/v1/model/info` returns model version, supported faults, raw sensor and 23-feature arrays, actual saved metrics, and limitations.

`POST /api/v1/predict`:

```json
{"session_id":"cylinder-1","reading":{"pressure":5.4,"temperature":31,"position":10,"flow":10,"speed":122,"vibration":0.4,"load":15,"cycle_count":1}}
```

Returns `Prediction`. `warmup` remains true until 10 ordered samples exist. A session's temporal state is independent of every other session.

`POST /api/v1/predict/batch` accepts `{"session_id": string, "readings": SensorReading[], "reset_buffer": boolean}` and returns `{"session_id": string, "predictions": Prediction[]}` in input order. One to 1,000 readings are allowed.

`GET /api/v1/history?session_id=cylinder-1&limit=100` returns `{"items": StoredPrediction[], "limit": number}` newest first. `session_id` is optional; `limit` is 1–1,000. Stored rows use `raw_sensors` for the original reading and `predicted_fault`, `estimated_health`, and `estimated_rul` for scalar outputs.

Simulation lifecycle:

- `POST /api/v1/simulations` accepts `session_id`, `planned_fault`, optional integer `seed`, optional `fault_start` (default 40), `maximum_severity` (0–1), and `rise_time` (≥1).
- `GET /api/v1/simulations/{session_id}` gets current state without advancing.
- `POST /api/v1/simulations/{session_id}/step` advances one deterministic step and predicts through the normal pipeline.
- `POST /api/v1/simulations/{session_id}/stop` stops advancement.
- `DELETE /api/v1/simulations/{session_id}` removes simulation and temporal/RUL buffers.

Simulation responses separate `true_simulated_state` and `simulation_metadata` from `prediction`; metadata never enters either ML model.

## WebSocket

Connect to `ws://127.0.0.1:8000/api/v1/ws/simulations/{session_id}` after creating the simulation. Each message is:

```json
{"type":"simulation_update","data":{"session_id":"demo","running":true,"step":1,"true_simulated_state":{},"simulation_metadata":{},"prediction":{}}}
```

The server advances only while a client is connected, waits `WEBSOCKET_INTERVAL` seconds between messages, and cleans up its connection loop on disconnect. Stop/reset remains explicit through REST.

## Errors and nullability

Errors have `{"error":{"code":string,"message":string,"details"?:array}}`. Status 422 means schema validation, 404 means a session was not found, 409 means invalid lifecycle state/fault selection, and 503 means an ML artifact is missing or incompatible. `health` can be null only when the health model is unavailable. `estimated_remaining_cycles` is null unless history has a negative trend. Do not interpret null RUL as zero.
