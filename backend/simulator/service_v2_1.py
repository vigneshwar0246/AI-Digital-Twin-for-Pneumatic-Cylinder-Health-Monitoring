"""Session-isolated lifecycle wrapper for the V2.1 simulator."""
import random
import threading
from dataclasses import dataclass
from backend.simulator.cylinder_v2_1 import PneumaticCylinderV21
from backend.simulator.faults_v2_1 import FaultEngineV21


@dataclass
class SimulationSession:
    simulator: PneumaticCylinderV21
    random_state: object
    step: int = 0
    running: bool = True
    last_prediction: dict | None = None


class SimulationService:
    def __init__(self):
        self.sessions = {}
        self.lock = threading.RLock()

    def create(self, session_id, planned_fault, seed=None, **kwargs):
        if planned_fault not in FaultEngineV21.FAULT_TYPES: raise ValueError(f"Unsupported fault: {planned_fault}")
        with self.lock:
            prior = random.getstate(); random.seed(seed)
            try:
                simulator = PneumaticCylinderV21(planned_fault=planned_fault, **kwargs)
                state = random.getstate()
            finally: random.setstate(prior)
            self.sessions[session_id] = SimulationSession(simulator, state)
            return self.state(session_id)

    def state(self, session_id):
        session = self._get(session_id)
        return {"session_id":session_id,"running":session.running,"step":session.step,
                "true_simulated_state":session.simulator.get_state(),"simulation_metadata":session.simulator.get_metadata(),
                "prediction":session.last_prediction}

    def advance(self, session_id):
        with self.lock:
            session = self._get(session_id)
            if not session.running: raise ValueError("Simulation is stopped")
            prior = random.getstate(); random.setstate(session.random_state)
            try: session.simulator.simulate_step(session.step); session.random_state = random.getstate()
            finally: random.setstate(prior)
            session.step += 1
            return self.state(session_id)

    def stop(self, session_id): self._get(session_id).running = False; return self.state(session_id)
    def reset(self, session_id):
        self._get(session_id); del self.sessions[session_id]
    def _get(self, session_id):
        if session_id not in self.sessions: raise KeyError(f"Simulation session not found: {session_id}")
        return self.sessions[session_id]
