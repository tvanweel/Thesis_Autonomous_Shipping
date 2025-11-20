import mesa

class DummyAgent(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.steps = 0  # track how often step() is called

    def step(self):
        self.steps += 1


class DummyModel(mesa.Model):
    def __init__(self, n_agents=10, seed=None):
        super().__init__(seed=seed)

        # Create agents – automatically added to model.agents
        for _ in range(n_agents):
            DummyAgent(self)

    def step(self):
        # Random order, call step() once per agent
        self.agents.shuffle_do("step")
