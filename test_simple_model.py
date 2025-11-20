from simple_model import DummyModel, DummyAgent


def test_model_creates_correct_number_of_agents():
    n_agents = 5
    model = DummyModel(n_agents=n_agents, seed=42)

    # Mesa 3.x: model.agents is an AgentSet
    assert len(model.agents) == n_agents


def test_step_calls_step_on_all_agents():
    n_agents = 3
    model = DummyModel(n_agents=n_agents, seed=42)

    # Before stepping: all agents should have steps == 0
    for agent in model.agents:
        assert agent.steps == 0

    # One model step
    model.step()

    # After stepping: each agent.steps should be 1
    for agent in model.agents:
        assert agent.steps == 1

