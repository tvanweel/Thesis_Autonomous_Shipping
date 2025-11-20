import numpy as np


class BassDiffusionModel:
    """
    Bass diffusion model for technology adoption.

    Continuous form:
        dN/dt = (p + q * N/M) * (M - N)

    This class implements a simple discrete-time approximation.
    """

    def __init__(
        self,
        market_potential: float,
        p: float,
        q: float,
        dt: float = 1.0,
        initial_adopters: float = 0.0,
    ):
        self.M = float(market_potential)
        self.p = float(p)
        self.q = float(q)
        self.dt = float(dt)

        # State - ensure initial adopters don't exceed market potential
        self.t = 0.0
        self.N = min(float(initial_adopters), self.M)  # cumulative adopters

        # Histories
        self.history_time = [self.t]
        self.history_N = [self.N]
        self.history_new_adopters = [0.0]

    def step(self):
        """Advance the Bass diffusion model by one discrete time step."""
        remaining = self.M - self.N  # remaining potential adopters

        if remaining <= 0:
            # Saturated: no more adoption
            self.t += self.dt
            self.history_time.append(self.t)
            self.history_N.append(self.N)
            self.history_new_adopters.append(0.0)
            return

        # Bass adoption rate
        adoption_rate = (self.p + self.q * (self.N / self.M)) * remaining
        dN = adoption_rate * self.dt

        # Ensure non-negative growth
        dN = max(dN, 0.0)

        # Clip at market potential
        if self.N + dN > self.M:
            dN = self.M - self.N

        self.N += dN
        self.t += self.dt

        self.history_time.append(self.t)
        self.history_N.append(self.N)
        self.history_new_adopters.append(dN)

    def run(self, steps: int):
        for _ in range(steps):
            self.step()


class MultiLevelAutomationDiffusion:
    """
    Models adoption of maritime automation levels with hierarchical constraints.

    Each automation level (L2, L3, L4-L5) has its own Bass diffusion model.
    Ships transition from manual (Level 0) to increasingly automated levels.

    Hierarchical constraints enforce that higher automation levels can only exist
    if the vessel has adopted the lower levels:
    - L4-L5 <= L3 <= L2
    - Total adoption <= total_fleet

    Real-world context (as of model initialization):
    - Total fleet: 8000 vessels (all initially manual)
    - Level 2 (partial automation): ~900 vessels, high market capacity
    - Level 3 (conditional automation): Not yet implemented (0 vessels)
    - Level 4-5 (high/full automation): Combined, not yet implemented (0 vessels)
    """

    def __init__(
        self,
        total_fleet: int,
        # Initial adopters at each level
        initial_L2: float = 0.0,
        initial_L3: float = 0.0,
        initial_L45: float = 0.0,
        # Market potentials (maximum vessels that could adopt each level)
        M2: float = 0.0,
        M3: float = 0.0,
        M45: float = 0.0,
        # Bass parameters per level (p=innovation, q=imitation)
        p2: float = 0.0,
        q2: float = 0.0,
        p3: float = 0.0,
        q3: float = 0.0,
        p45: float = 0.0,
        q45: float = 0.0,
        dt: float = 1.0,
    ):
        self.total_fleet = float(total_fleet)
        self.dt = float(dt)

        # Store market potentials
        self.M2 = float(M2)
        self.M3 = float(M3)
        self.M45 = float(M45)

        # Enforce initial hierarchical constraints
        initial_L2 = min(float(initial_L2), self.M2, self.total_fleet)
        initial_L3 = min(float(initial_L3), self.M3, initial_L2)
        initial_L45 = min(float(initial_L45), self.M45, initial_L3)

        # Create separate Bass diffusion model for each automation level
        self.l2_model = BassDiffusionModel(
            market_potential=self.M2,
            p=p2,
            q=q2,
            dt=dt,
            initial_adopters=initial_L2,
        )
        self.l3_model = BassDiffusionModel(
            market_potential=self.M3,
            p=p3,
            q=q3,
            dt=dt,
            initial_adopters=initial_L3,
        )
        self.l45_model = BassDiffusionModel(
            market_potential=self.M45,
            p=p45,
            q=q45,
            dt=dt,
            initial_adopters=initial_L45,
        )

        # Initialize history tracking for each level
        self.t = 0.0
        self.history_time = [self.t]
        self.history_L2 = [initial_L2]
        self.history_L3 = [initial_L3]
        self.history_L45 = [initial_L45]

    def step(self):
        """
        Advance all diffusion models by one time step with hierarchical constraint enforcement.

        Enforces: L45 <= L3 <= L2 <= min(M2, total_fleet)
        """
        # Advance each Bass process independently first
        self.l2_model.step()
        self.l3_model.step()
        self.l45_model.step()

        # Get unconstrained adoption counts from Bass models
        N2_unconstrained = self.l2_model.N
        N3_unconstrained = self.l3_model.N
        N45_unconstrained = self.l45_model.N

        # Apply hierarchical constraints from top-down
        # L2 cannot exceed total fleet or its market potential
        N2 = min(N2_unconstrained, self.total_fleet, self.M2)

        # L3 cannot exceed L2 or its market potential
        N3 = min(N3_unconstrained, N2, self.M3)

        # L45 cannot exceed L3 or its market potential
        N45 = min(N45_unconstrained, N3, self.M45)

        # Enforce non-negativity
        N2 = max(N2, 0.0)
        N3 = max(N3, 0.0)
        N45 = max(N45, 0.0)

        # Enforce non-decreasing property (adoption cannot go backwards)
        if len(self.history_L2) > 0:
            N2 = max(N2, self.history_L2[-1])
            N3 = max(N3, self.history_L3[-1])
            N45 = max(N45, self.history_L45[-1])

        # Update time
        self.t += self.dt

        # Update the internal state of Bass models to match constrained values
        self.l2_model.N = N2
        self.l3_model.N = N3
        self.l45_model.N = N45

        # Record history
        self.history_time.append(self.t)
        self.history_L2.append(N2)
        self.history_L3.append(N3)
        self.history_L45.append(N45)

    def run(self, steps: int):
        """Run the simulation for a specified number of time steps."""
        for _ in range(steps):
            self.step()
