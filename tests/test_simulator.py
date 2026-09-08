from backend.simulator.service_v2_1 import SimulationService

def test_deterministic_and_isolated_simulations():
    service=SimulationService(); service.create("a","Healthy",seed=42); service.create("b","Healthy",seed=42)
    assert service.advance("a")["true_simulated_state"]==service.advance("b")["true_simulated_state"]
    service.stop("a"); assert service.state("a")["running"] is False and service.state("b")["running"] is True
