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
    Models adoption of maritime automation levels as mutually exclusive categories.

    Each automation level (L0-L5) represents a DISTINCT automation capability
    based on CCNR definitions. Vessels belong to exactly ONE level:
    - L0: Manual operation (no automation)
    - L1: Steering assistance (track pilot with basic automation)
    - L2: Partial automation (track pilot + propulsion control)
    - L3: Conditional automation (with collision avoidance systems)
    - L4: High automation (advanced autonomous capabilities)
    - L5: Full automation (fully autonomous vessels)

    Key constraint: L0 + L1 + L2 + L3 + L4 + L5 = total_fleet (always)

    Each level has its own Bass diffusion model with independent adoption dynamics.
    Market potentials represent the maximum number of vessels that could adopt
    each specific level, and their sum can equal the total fleet.

    Real-world context (as of model initialization):
    - Total fleet: ~10,000 vessels in European inland shipping
    - L0: ~9,100 vessels (manual operation, majority of fleet)
    - L1+L2: ~900 vessels with track pilot systems (initial adopters)
    - L3-L5: 0 vessels (technologies still in development)
    """

    def __init__(
        self,
        total_fleet: int,
        # Initial adopters at each level
        initial_L1: float = 0.0,
        initial_L2: float = 0.0,
        initial_L3: float = 0.0,
        initial_L4: float = 0.0,
        initial_L5: float = 0.0,
        # Market potentials (maximum vessels that could adopt each level)
        M1: float = 0.0,
        M2: float = 0.0,
        M3: float = 0.0,
        M4: float = 0.0,
        M5: float = 0.0,
        # Bass parameters per level (p=innovation, q=imitation)
        p1: float = 0.0,
        q1: float = 0.0,
        p2: float = 0.0,
        q2: float = 0.0,
        p3: float = 0.0,
        q3: float = 0.0,
        p4: float = 0.0,
        q4: float = 0.0,
        p5: float = 0.0,
        q5: float = 0.0,
        dt: float = 1.0,
    ):
        self.total_fleet = float(total_fleet)
        self.dt = float(dt)

        # Store market potentials
        self.M1 = float(M1)
        self.M2 = float(M2)
        self.M3 = float(M3)
        self.M4 = float(M4)
        self.M5 = float(M5)

        # Enforce initial hierarchical constraints
        initial_L1 = min(float(initial_L1), self.M1, self.total_fleet)
        initial_L2 = min(float(initial_L2), self.M2, initial_L1)
        initial_L3 = min(float(initial_L3), self.M3, initial_L2)
        initial_L4 = min(float(initial_L4), self.M4, initial_L3)
        initial_L5 = min(float(initial_L5), self.M5, initial_L4)

        # Create separate Bass diffusion model for each automation level
        self.l1_model = BassDiffusionModel(
            market_potential=self.M1,
            p=p1,
            q=q1,
            dt=dt,
            initial_adopters=initial_L1,
        )
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
        self.l4_model = BassDiffusionModel(
            market_potential=self.M4,
            p=p4,
            q=q4,
            dt=dt,
            initial_adopters=initial_L4,
        )
        self.l5_model = BassDiffusionModel(
            market_potential=self.M5,
            p=p5,
            q=q5,
            dt=dt,
            initial_adopters=initial_L5,
        )

        # Initialize history tracking for each level
        self.t = 0.0
        self.history_time = [self.t]
        self.history_L1 = [initial_L1]
        self.history_L2 = [initial_L2]
        self.history_L3 = [initial_L3]
        self.history_L4 = [initial_L4]
        self.history_L5 = [initial_L5]

    def step(self):
        """
        Advance all diffusion models by one time step.

        Each level evolves independently according to its Bass diffusion dynamics.
        The only constraint is that total adoption across all levels cannot exceed
        the total fleet: L1 + L2 + L3 + L4 + L5 <= total_fleet
        """
        # Advance each Bass process independently
        self.l1_model.step()
        self.l2_model.step()
        self.l3_model.step()
        self.l4_model.step()
        self.l5_model.step()

        # Get unconstrained adoption counts from Bass models
        N1_unconstrained = self.l1_model.N
        N2_unconstrained = self.l2_model.N
        N3_unconstrained = self.l3_model.N
        N4_unconstrained = self.l4_model.N
        N5_unconstrained = self.l5_model.N

        # Apply market potential constraints (each level capped by its own M)
        N1 = min(N1_unconstrained, self.M1)
        N2 = min(N2_unconstrained, self.M2)
        N3 = min(N3_unconstrained, self.M3)
        N4 = min(N4_unconstrained, self.M4)
        N5 = min(N5_unconstrained, self.M5)

        # Apply fleet constraint: total adoption cannot exceed fleet size
        total_adopted = N1 + N2 + N3 + N4 + N5
        if total_adopted > self.total_fleet:
            # Proportionally scale down all levels to fit within fleet
            scale_factor = self.total_fleet / total_adopted
            N1 *= scale_factor
            N2 *= scale_factor
            N3 *= scale_factor
            N4 *= scale_factor
            N5 *= scale_factor

        # Enforce non-negativity
        N1 = max(N1, 0.0)
        N2 = max(N2, 0.0)
        N3 = max(N3, 0.0)
        N4 = max(N4, 0.0)
        N5 = max(N5, 0.0)

        # Enforce non-decreasing property (adoption cannot go backwards)
        if len(self.history_L1) > 0:
            N1 = max(N1, self.history_L1[-1])
            N2 = max(N2, self.history_L2[-1])
            N3 = max(N3, self.history_L3[-1])
            N4 = max(N4, self.history_L4[-1])
            N5 = max(N5, self.history_L5[-1])

        # Update time
        self.t += self.dt

        # Update the internal state of Bass models to match constrained values
        self.l1_model.N = N1
        self.l2_model.N = N2
        self.l3_model.N = N3
        self.l4_model.N = N4
        self.l5_model.N = N5

        # Record history
        self.history_time.append(self.t)
        self.history_L1.append(N1)
        self.history_L2.append(N2)
        self.history_L3.append(N3)
        self.history_L4.append(N4)
        self.history_L5.append(N5)

    def run(self, steps: int):
        """Run the simulation for a specified number of time steps."""
        for _ in range(steps):
            self.step()
