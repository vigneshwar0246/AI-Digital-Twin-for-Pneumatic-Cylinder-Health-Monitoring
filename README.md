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
```

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