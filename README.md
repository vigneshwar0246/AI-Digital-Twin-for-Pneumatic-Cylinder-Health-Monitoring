# AI-Driven Digital Twin for Pneumatic Cylinder Health Monitoring and Predictive Maintenance

## Overview

This project presents an AI-powered Digital Twin of a pneumatic cylinder that continuously monitors its operational health using simulated sensor data and intelligent analytics. The Digital Twin mirrors the physical system in real time, enabling condition monitoring, anomaly detection, fault prediction, and predictive maintenance.

The project combines Artificial Intelligence (AI), Internet of Things (IoT), and Digital Twin technology to create a scalable predictive maintenance solution for industrial automation.

---

## Features

- Real-time Digital Twin simulation
- Pneumatic cylinder behavior modeling
- Live sensor data simulation
- AI-based anomaly detection
- Remaining Useful Life (RUL) prediction
- Health score calculation
- Fault detection
- REST API using FastAPI
- Interactive React dashboard
- MQTT communication support
- Docker deployment
- Modular architecture

---

## Technologies Used

### Backend
- Python
- FastAPI
- NumPy
- Pandas
- Scikit-learn

### Frontend
- React
- Vite
- JavaScript
- CSS

### AI & Machine Learning
- Feature Engineering
- Anomaly Detection
- Predictive Analytics
- Remaining Useful Life Prediction

### IoT
- MQTT
- Sensor Simulation

### DevOps
- Docker
- Docker Compose
- Nginx

---

## Project Structure

```
AI-DigitalTwin-PneumaticCylinder/
│
├── backend/
│   ├── ai/
│   ├── api/
│   ├── simulator/
│   ├── mqtt/
│   ├── database/
│   ├── config/
│   └── app.py
│
├── frontend/
│   ├── src/
│   └── package.json
│
├── deployment/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx.conf
│
├── docs/
├── notebooks/
├── tests/
├── datasets/
│
├── README.md
├── requirements.txt
└── start.bat
```

---

## Digital Twin Workflow

```
Physical Pneumatic Cylinder
            │
            ▼
     Sensor Data Collection
            │
            ▼
      Digital Twin Model
            │
            ▼
 AI Prediction & Analytics
            │
            ▼
 Health Monitoring Dashboard
            │
            ▼
 Predictive Maintenance Alerts
```

---

## Simulated Parameters

The Digital Twin continuously monitors:

- Pressure (bar)
- Temperature (°C)
- Position (mm)
- Speed (mm/s)
- Flow Rate (L/min)
- Cycle Count
- Health Score
- Fault Status

---

## AI Modules

### Feature Engineering
Processes sensor readings into machine learning features.

### Anomaly Detection
Detects abnormal operating conditions.

### Predictive Maintenance
Predicts possible failures before breakdown.

### Remaining Useful Life (RUL)
Estimates the operational life remaining.

---

## Fault Types

- Healthy
- Air Leakage
- Seal Wear
- Valve Sticking
- Pressure Drop

---

## Installation

### Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/AI-DigitalTwin-PneumaticCylinder.git
```

### Enter Project

```bash
cd AI-DigitalTwin-PneumaticCylinder
```

### Install Python Packages

```bash
pip install -r requirements.txt
```

### Start Backend

```bash
python backend/app.py
```

### Start Frontend

```bash
cd frontend
npm install
npm run dev
```"

---

## Future Enhancements

- Real IoT sensor integration
- ESP32 connectivity
- Cloud deployment
- Time-series database
- LSTM-based prediction
- Computer Vision inspection
- Mobile application
- Grafana monitoring
- Digital Twin synchronization
- Edge AI deployment

---

## Applications

- Smart Manufacturing
- Industry 4.0
- Predictive Maintenance
- Industrial Automation
- Condition Monitoring
- Smart Factories

---

## Learning Outcomes

- Digital Twin Modeling
- AI for Predictive Maintenance
- IoT Communication
- FastAPI Development
- React Dashboard Development
- MQTT Integration
- Docker Deployment
- Industrial Automation Concepts

---

## Author

**Your Name**

AI & Machine Learning Student

---

## License

This project is developed for educational and research purposes.

---

## Acknowledgements

- FastAPI
- React
- Scikit-learn
- Docker
- MQTT
- Open Source Community

python -m backend.simulator.engine - run live simulation

---

## V2.1 Prototype Backend

The supported backend is a stateful FastAPI service. It loads the fault classifier and separate experimental health regressor once at startup, produces the same 23 features used in offline training, persists predictions to SQLite, and exposes the V2.1 simulator through REST and WebSocket APIs. Control output is advisory simulation output only; it never operates hardware.

### Windows setup and startup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m backend.ai.train_v2_1          # only if the classifier artifact is absent
python -m backend.ai.train_health_v2_1   # creates the separate health artifact
python -m uvicorn backend.api.main:app --reload
```

Use a scikit-learn runtime compatible with the version that generated each joblib artifact. OpenAPI is at `http://127.0.0.1:8000/docs`.

### API summary

All application routes except `/` use `/api/v1`:

- `GET /`, `/health`, `/model/info`, and `/history`
- `POST /predict` and `/predict/batch`
- `POST /simulations`, `GET /simulations/{session_id}`, `POST /simulations/{session_id}/step`, `POST /simulations/{session_id}/stop`, and `DELETE /simulations/{session_id}`
- `WS /ws/simulations/{session_id}`

```powershell
$reading = @{session_id='cylinder-1'; reading=@{pressure=5.4;temperature=31;position=10;flow=10;speed=122;vibration=0.4;load=15;cycle_count=1}} | ConvertTo-Json -Depth 4
Invoke-RestMethod http://127.0.0.1:8000/api/v1/predict -Method Post -ContentType application/json -Body $reading

$simulation = @{session_id='demo';planned_fault='Seal Wear';seed=42} | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:8000/api/v1/simulations -Method Post -ContentType application/json -Body $simulation
Invoke-RestMethod http://127.0.0.1:8000/api/v1/simulations/demo/step -Method Post
```

Sensor units are pressure (bar), temperature (°C), position (mm), flow (L/min), speed (mm/s), vibration (mm/s), load (kg), and optional non-negative cycle count. Supported classes are Healthy, Air Leakage, Pressure Drop, Seal Wear, and Valve Sticking.

Copy `.env.example` to `.env` or set its variables in PowerShell before startup. Configuration covers allowed CORS origins, SQLite/model paths, buffer size, RUL threshold/cap, and WebSocket interval. Environment variables are read directly; no cloud service is required.

Run verification with:

```powershell
python -m pytest -q
python -m backend.simulator.validate_dataset_v2_1
```

The models and reported evaluation results come from synthetic simulation data. The health regressor is experimental, and RUL is returned only when a measurable declining health trend exists. Physical sensor calibration, run-to-failure collection, industrial safety validation, and a hardware control layer remain future work. See [the frontend contract](docs/frontend_api_contract.md) for exact payloads.

----------------------------------------------------------------------------------------
terminal 1

cd D:\DigitalTwin-PneumaticCylinder
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
$env:CORS_ORIGINS="http://localhost:5173,http://127.0.0.1:5173"
python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8001

-----------------------------------------------------------------------------------------

terminal 2

cd D:\DigitalTwin-PneumaticCylinder\frontend
$env:VITE_API_BASE_URL="http://127.0.0.1:8001"
npm.cmd run dev

----------------------------------------------------------------------------------------
to run 

double tap the bat file!!
----------------------------------------------------------------------------------------